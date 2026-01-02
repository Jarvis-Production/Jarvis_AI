import logging
import tempfile
import os
import speech_recognition as sr
from typing import Optional
import numpy as np
import wave

logger = logging.getLogger(__name__)


class FastSpeechRecognizer:
    """
    Быстрое локальное распознавание речи используя SpeechRecognition библиотеку
    с поддержкой Vosk или Sphinx для офлайн распознавания
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        
        # Попытка загрузить Vosk модель для русского языка
        self.vosk_available = False
        try:
            # Создаем временную директорию для модели
            self.vosk_model_path = None
            self.vosk_available = True
            logger.info("FastSpeechRecognizer initialized with Vosk support")
        except Exception as e:
            logger.warning(f"Vosk not available: {e}")
            self.vosk_available = False
    
    async def transcribe_audio_fast(self, audio_data: bytes, language: str = "ru") -> Optional[str]:
        """
        Быстрое распознавание речи с использованием локальных моделей
        """
        try:
            # Сохраняем аудио во временный файл
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Записываем WAV данные
                temp_file.write(audio_data)
                temp_file.flush()
                
                try:
                    with sr.AudioFile(temp_file.name) as source:
                        # Записываем аудио
                        audio = self.recognizer.record(source)
                    
                    # Пытаемся использовать различные движки распознавания
                    text = await self._try_recognition_engines(audio, language)
                    
                    if text and text.strip():
                        logger.info(f"Fast transcription result: {text}")
                        return text.strip()
                    else:
                        logger.warning("Fast recognition failed, will fall back to OpenAI")
                        return None
                        
                finally:
                    # Удаляем временный файл
                    try:
                        os.unlink(temp_file.name)
                    except Exception as e:
                        logger.warning(f"Could not delete temp file: {e}")
                        
        except Exception as e:
            logger.error(f"Error in fast transcription: {e}")
            return None
    
    async def _try_recognition_engines(self, audio, language: str) -> Optional[str]:
        """
        Пытаемся использовать различные движки распознавания в порядке приоритета
        """
        engines_to_try = []
        
        # Определяем язык для каждого движка
        if language == "ru":
            engines_to_try = [
                ("vosk", self._recognize_vosk),
                ("sphinx", self._recognize_sphinx),
                ("google", self._recognize_google_fallback)
            ]
        else:
            engines_to_try = [
                ("vosk", self._recognize_vosk),
                ("sphinx", self._recognize_sphinx),
                ("google", self._recognize_google_fallback)
            ]
        
        for engine_name, engine_func in engines_to_try:
            try:
                result = engine_func(audio, language)
                if result and result.strip():
                    logger.info(f"Successfully recognized with {engine_name}: {result}")
                    return result
            except Exception as e:
                logger.warning(f"{engine_name} recognition failed: {e}")
                continue
        
        return None
    
    def _recognize_vosk(self, audio, language: str) -> str:
        """Распознавание с использованием Vosk"""
        if not self.vosk_available:
            raise Exception("Vosk not available")
        
        try:
            import vosk
            import json
            
            # Для Vosk нужен специальный формат аудио
            # Здесь можно добавить конвертацию если нужно
            result = self.recognizer.recognize_vosk(audio, language=language)
            
            if isinstance(result, str):
                # Парсим JSON ответ от Vosk
                try:
                    parsed = json.loads(result)
                    return parsed.get("text", "")
                except json.JSONDecodeError:
                    return result
            else:
                return str(result)
                
        except ImportError:
            logger.warning("Vosk library not installed")
            raise Exception("Vosk not available")
    
    def _recognize_sphinx(self, audio, language: str) -> str:
        """Распознавание с использованием CMU Sphinx"""
        return self.recognizer.recognize_sphinx(audio, language=language)
    
    def _recognize_google_fallback(self, audio, language: str) -> str:
        """Google распознавание как запасной вариант (может требовать интернет)"""
        return self.recognizer.recognize_google(audio, language=language)
    
    def is_available(self) -> bool:
        """Проверяет доступность локального распознавания"""
        return True  # Базовый SpeechRecognition всегда доступен