import logging
from typing import Optional
import base64
import aiohttp
from backend.config import settings

logger = logging.getLogger(__name__)


class TextToSpeech:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.voice_id = settings.ELEVENLABS_VOICE_ID
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def synthesize_speech(self, text: str) -> Optional[bytes]:
        if not self.api_key:
            logger.error("ElevenLabs API key not configured")
            return None
        
        try:
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            
            logger.info(f"Synthesizing speech for text: {text[:50]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        logger.info(f"Speech synthesized successfully (size: {len(audio_data)} bytes)")
                        return audio_data
                    else:
                        error_text = await response.text()
                        logger.error(f"ElevenLabs API error: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None
    
    async def synthesize_speech_base64(self, text: str) -> Optional[str]:
        audio_data = await self.synthesize_speech(text)
        if audio_data:
            return base64.b64encode(audio_data).decode('utf-8')
        return None
    
    async def get_available_voices(self) -> Optional[list]:
        try:
            url = f"{self.base_url}/voices"
            
            headers = {
                "Accept": "application/json",
                "xi-api-key": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("voices", [])
                    else:
                        logger.error(f"Error fetching voices: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return None
