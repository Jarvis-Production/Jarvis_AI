import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
from datetime import datetime
from typing import Dict, Set

from backend.config import settings
from backend.models import CommandRequest, CommandResponse
from backend.services import (
    AudioProcessor,
    SpeechRecognizer,
    CommandProcessor,
    LLMHandler,
    TextToSpeech
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jarvis AI Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

audio_processor = AudioProcessor(sample_rate=settings.SAMPLE_RATE)
speech_recognizer = SpeechRecognizer()
command_processor = CommandProcessor()
llm_handler = LLMHandler()
text_to_speech = TextToSpeech()

active_connections: Set[WebSocket] = set()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
    
    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Jarvis AI Assistant API")
    is_valid, missing_keys = settings.validate_api_keys()
    if not is_valid:
        logger.warning(f"Missing API keys: {', '.join(missing_keys)}")
    else:
        logger.info("All required API keys are configured")


@app.get("/")
async def root():
    return {
        "service": "Jarvis AI Assistant API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    is_valid, missing_keys = settings.validate_api_keys()
    return {
        "status": "healthy" if is_valid else "degraded",
        "timestamp": datetime.now().isoformat(),
        "api_keys_configured": is_valid,
        "missing_keys": missing_keys if not is_valid else []
    }


@app.post("/api/command")
async def process_command(request: CommandRequest) -> CommandResponse:
    try:
        response_text, command_type = await command_processor.process_command(request.command)
        
        if command_type == "gpt":
            gpt_response = await llm_handler.get_response(request.command)
            response_text = gpt_response if gpt_response else "Извините, не могу обработать этот запрос."
        
        audio_base64 = await text_to_speech.synthesize_speech_base64(response_text)
        
        return CommandResponse(
            response=response_text,
            audio_url=f"data:audio/mpeg;base64,{audio_base64}" if audio_base64 else None,
            command_type=command_type,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error processing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive()
            
            if "text" in data:
                message = json.loads(data["text"])
                await handle_websocket_message(websocket, client_id, message)
            
            elif "bytes" in data:
                audio_data = data["bytes"]
                await handle_audio_data(websocket, client_id, audio_data)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)


async def handle_websocket_message(websocket: WebSocket, client_id: str, message: dict):
    msg_type = message.get("type")
    
    if msg_type == "text":
        command_text = message.get("data", {}).get("text", "")
        
        await manager.send_message(client_id, {
            "type": "status",
            "data": {"status": "processing", "message": "Обрабатываю команду..."}
        })
        
        response_text, command_type = await command_processor.process_command(command_text)
        
        if command_type == "gpt":
            gpt_response = await llm_handler.get_response(command_text)
            response_text = gpt_response if gpt_response else "Извините, не могу обработать этот запрос."
        
        audio_base64 = await text_to_speech.synthesize_speech_base64(response_text)
        
        await manager.send_message(client_id, {
            "type": "response",
            "data": {
                "text": response_text,
                "audio": f"data:audio/mpeg;base64,{audio_base64}" if audio_base64 else None,
                "command_type": command_type,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    elif msg_type == "control":
        action = message.get("data", {}).get("action")
        
        if action == "clear_history":
            llm_handler.clear_history()
            await manager.send_message(client_id, {
                "type": "status",
                "data": {"status": "success", "message": "История очищена"}
            })
        
        elif action == "get_reminders":
            reminders = command_processor.get_reminders()
            await manager.send_message(client_id, {
                "type": "reminders",
                "data": {"reminders": reminders}
            })


async def handle_audio_data(websocket: WebSocket, client_id: str, audio_data: bytes):
    try:
        volume = audio_processor.calculate_volume(audio_data)
        
        await manager.send_message(client_id, {
            "type": "volume",
            "data": {"volume": volume}
        })
        
        if len(audio_data) < 1000:
            return
        
        await manager.send_message(client_id, {
            "type": "status",
            "data": {"status": "transcribing", "message": "Распознаю речь..."}
        })
        
        wav_data = audio_processor.convert_to_wav(audio_data)
        
        transcription = await speech_recognizer.transcribe_audio(wav_data, language=settings.LANGUAGE)
        
        if not transcription:
            await manager.send_message(client_id, {
                "type": "error",
                "data": {"error": "Не удалось распознать речь"}
            })
            return
        
        await manager.send_message(client_id, {
            "type": "transcription",
            "data": {"text": transcription}
        })
        
        await manager.send_message(client_id, {
            "type": "status",
            "data": {"status": "processing", "message": "Обрабатываю команду..."}
        })
        
        response_text, command_type = await command_processor.process_command(transcription)
        
        if command_type == "gpt":
            gpt_response = await llm_handler.get_response(transcription)
            response_text = gpt_response if gpt_response else "Извините, не могу обработать этот запрос."
        
        audio_base64 = await text_to_speech.synthesize_speech_base64(response_text)
        
        await manager.send_message(client_id, {
            "type": "response",
            "data": {
                "text": response_text,
                "audio": f"data:audio/mpeg;base64,{audio_base64}" if audio_base64 else None,
                "command_type": command_type,
                "timestamp": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error handling audio data: {e}")
        await manager.send_message(client_id, {
            "type": "error",
            "data": {"error": str(e)}
        })


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
