import numpy as np
import base64
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AudioProcessor:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
    
    def calculate_volume(self, audio_data: bytes) -> float:
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            if len(audio_array) == 0:
                return 0.0
            
            rms = np.sqrt(np.mean(np.square(audio_array.astype(float))))
            
            max_amplitude = 32768.0
            volume_normalized = min(100, (rms / max_amplitude) * 100)
            
            return round(volume_normalized, 2)
        except Exception as e:
            logger.error(f"Error calculating volume: {e}")
            return 0.0
    
    def decode_base64_audio(self, base64_audio: str) -> Optional[bytes]:
        try:
            if "," in base64_audio:
                base64_audio = base64_audio.split(",")[1]
            
            audio_bytes = base64.b64decode(base64_audio)
            return audio_bytes
        except Exception as e:
            logger.error(f"Error decoding base64 audio: {e}")
            return None
    
    def convert_to_wav(self, audio_data: bytes) -> bytes:
        try:
            import wave
            
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data)
            
            wav_buffer.seek(0)
            return wav_buffer.read()
        except Exception as e:
            logger.error(f"Error converting to WAV: {e}")
            return audio_data
    
    def normalize_audio(self, audio_data: bytes) -> bytes:
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            if len(audio_array) == 0:
                return audio_data
            
            max_val = np.max(np.abs(audio_array))
            if max_val > 0:
                normalized = (audio_array.astype(float) / max_val * 32767).astype(np.int16)
                return normalized.tobytes()
            
            return audio_data
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return audio_data
    
    def detect_speech(self, audio_data: bytes, threshold: float = 10.0) -> bool:
        volume = self.calculate_volume(audio_data)
        return volume > threshold
