from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class AudioData(BaseModel):
    audio: str
    format: str = "webm"
    sample_rate: int = 16000


class TranscriptionResponse(BaseModel):
    text: str
    timestamp: datetime = datetime.now()


class CommandRequest(BaseModel):
    command: str
    timestamp: datetime = datetime.now()


class CommandResponse(BaseModel):
    response: str
    audio_url: Optional[str] = None
    command_type: Literal["predefined", "gpt"] = "predefined"
    timestamp: datetime = datetime.now()


class WebSocketMessage(BaseModel):
    type: Literal["audio", "text", "control"]
    data: dict


class AssistantState(BaseModel):
    is_listening: bool = False
    is_processing: bool = False
    current_command: Optional[str] = None
    last_response: Optional[str] = None
