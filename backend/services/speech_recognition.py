import logging
from openai import OpenAI
from typing import Optional
import io
from backend.config import settings

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.WHISPER_MODEL
    
    async def transcribe_audio(self, audio_data: bytes, language: str = "ru") -> Optional[str]:
        try:
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            logger.info(f"Transcribing audio (size: {len(audio_data)} bytes)")
            
            transcript = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                response_format="text"
            )
            
            if isinstance(transcript, str):
                text = transcript
            else:
                text = transcript.text if hasattr(transcript, 'text') else str(transcript)
            
            logger.info(f"Transcription result: {text}")
            return text.strip() if text else None
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def transcribe_audio_detailed(self, audio_data: bytes, language: str = "ru") -> Optional[dict]:
        try:
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            transcript = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                response_format="verbose_json"
            )
            
            return transcript.model_dump() if hasattr(transcript, 'model_dump') else transcript
            
        except Exception as e:
            logger.error(f"Error transcribing audio (detailed): {e}")
            return None
