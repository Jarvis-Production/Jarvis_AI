import logging
from openai import OpenAI
from typing import Optional
import io
from backend.config import settings
from .fast_speech_recognition import FastSpeechRecognizer

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.WHISPER_MODEL
        self.fast_recognizer = FastSpeechRecognizer()
    
    async def transcribe_audio(self, audio_data: bytes, language: str = "ru") -> Optional[str]:
        """
        Быстрое распознавание сначала локально, затем через OpenAI как запасной вариант
        """
        try:
            # Сначала пробуем быстрое локальное распознавание
            fast_result = await self.fast_recognizer.transcribe_audio_fast(audio_data, language)
            
            if fast_result and fast_result.strip():
                logger.info(f"Fast local transcription successful: {fast_result}")
                return fast_result
            
            # Если локальное распознавание не удалось, используем OpenAI
            logger.info("Fast recognition failed, falling back to OpenAI Whisper")
            return await self._transcribe_with_openai(audio_data, language)
            
        except Exception as e:
            logger.error(f"Error in hybrid transcription: {e}")
            # В случае ошибки всегда возвращаемся к OpenAI
            return await self._transcribe_with_openai(audio_data, language)
    
    async def _transcribe_with_openai(self, audio_data: bytes, language: str = "ru") -> Optional[str]:
        """Оригинальное распознавание через OpenAI Whisper"""
        try:
            import asyncio
            
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            logger.info(f"Transcribing audio with OpenAI (size: {len(audio_data)} bytes)")
            
            # Запуск синхронного API вызова в отдельном потоке
            def transcribe_sync():
                return self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=language,
                    response_format="text"
                )
            
            # Выполнение в thread pool для избежания блокировки event loop
            loop = asyncio.get_event_loop()
            transcript = await loop.run_in_executor(None, transcribe_sync)
            
            if isinstance(transcript, str):
                text = transcript
            else:
                text = transcript.text if hasattr(transcript, 'text') else str(transcript)
            
            logger.info(f"OpenAI transcription result: {text}")
            return text.strip() if text else None
            
        except Exception as e:
            logger.error(f"Error transcribing audio with OpenAI: {e}")
            return None
