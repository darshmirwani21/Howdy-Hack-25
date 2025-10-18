from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from enum import Enum

# Basic OpenAI Messages
class Message(BaseModel):
    role: str
    content: Union[str, List[Dict[str, Any]]]  # Support both text and multimodal (text + images)

# Tool definitions for computer use
class ToolFunction(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class Tool(BaseModel):
    type: str  # "function"
    function: ToolFunction

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    response_format: Optional[Dict[str, Any]] = None
    tools: Optional[List[Tool]] = None  # For computer use functions
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None  # "auto", "none", or specific tool
#openrouter takes this in; convert to json to send to openrouter