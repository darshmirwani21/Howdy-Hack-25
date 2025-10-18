from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

# Basic OpenAI Messages
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    response_format: Optional[Dict[str, Any]] = None