import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    OPENWEATHERMAP_API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY", "")
    
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "nPczCjzI2devNBz1zQrb")
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    WHISPER_MODEL: str = "whisper-1"
    GPT_MODEL: str = "gpt-4"
    
    MAX_AUDIO_DURATION: int = 30
    SAMPLE_RATE: int = 16000
    
    LANGUAGE: str = os.getenv("LANGUAGE", "ru")

    @staticmethod
    def validate_api_keys() -> tuple[bool, list[str]]:
        missing_keys = []
        if not Settings.OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")
        if not Settings.ELEVENLABS_API_KEY:
            missing_keys.append("ELEVENLABS_API_KEY")
        
        return len(missing_keys) == 0, missing_keys


settings = Settings()
