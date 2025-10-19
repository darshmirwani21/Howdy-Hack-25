import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class OpenRouterClient:
    """
    Client for forwarding Stagehand/OpenAI-format requests to OpenRouter API.
    Handles request transformation and response formatting.
    """
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1-distill-qwen-32b")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.base_url,
        }

    def chat_completion(self, messages: list, model: Optional[str] = None, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        import json
        import time
        
        # Use provided model or fall back to default
        selected_model = model or self.model
        
        # Inject JSON formatting instruction into the system message
        # This ensures the LLM responds in JSON format for Stagehand
        enhanced_messages = self._inject_json_instruction(messages)
        
        # Prepare request payload with JSON mode enforcement
        payload = {
            "model": selected_model,
            "messages": enhanced_messages,
            "temperature": temperature,
        }
        
        # Force JSON response format if the model supports it
        # Check if response_format was explicitly provided in kwargs
        if "response_format" not in kwargs:
            # Add JSON mode by default for structured output
            payload["response_format"] = {"type": "json_object"}
        
        # Add optional parameters
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # Add any additional parameters (like response_format, etc.)
        for key, value in kwargs.items():
            if key not in payload and value is not None:
                payload[key] = value
        
        try:
            # Make request to OpenRouter
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            # Raise exception for HTTP errors
            response.raise_for_status()
            
            # Get the response JSON
            response_data = response.json()
            
            # Validate and normalize the response for Stagehand compatibility
            response_data = self._normalize_openai_response(response_data, selected_model)
            print(response_data)
            return response_data
            
        except requests.exceptions.RequestException as e:
            # Handle API errors and return a fallback response
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', error_message)
                except:
                    error_message = e.response.text or error_message
            
            # Return a minimal error response in OpenAI format with JSON content
            return {
                "id": f"chatcmpl-error-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": selected_model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": json.dumps({
                            "method": "waitForTimeout",
                            "element": None,
                            "args": [1000],
                            "step": f"Error: {error_message}",
                            "completed": False
                        })
                    },
                    "finish_reason": "stop",
                    "logprobs": None
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
    
    def _inject_json_instruction(self, messages: list) -> list:
        """
        Inject JSON formatting instructions into the message list.
        Ensures the LLM understands it must respond in Stagehand's internal action schema.
        """
        # Create a copy to avoid modifying the original
        enhanced_messages = messages.copy()
        
        # JSON instruction for Stagehand's internal action schema
        json_instruction = """You are a browser automation assistant using Stagehand. You must respond with valid JSON only.

Your response MUST be a valid JSON object matching Stagehand's internal action schema:
{
  "method": "the Playwright function to call (e.g., click, fill, press, hover, scrollIntoViewIfNeeded)",
  "element": "element number to act on (integer or null for page-level actions)",
  "args": ["array", "of", "required", "arguments", "for", "the", "method"],
  "step": "human-readable description of what this action does",
  "completed": false
}

VALID PLAYWRIGHT METHODS:
- "click" - Click an element
- "fill" - Fill an input field with text
- "press" - Press a keyboard key
- "hover" - Hover over an element
- "scrollIntoViewIfNeeded" - Scroll element into view
- "selectOption" - Select an option from dropdown
- "check" - Check a checkbox
- "uncheck" - Uncheck a checkbox
- "goto" - Navigate to a URL (page-level, element: null)
- "waitForTimeout" - Wait for specified time (page-level)

CRITICAL RULES:
1. Use exact Playwright method names
2. "element" is a number (0, 1, 2, etc.) or null for page-level actions
3. "args" is ALWAYS an array, even if empty []
4. "step" is a human-readable description
5. "completed" is boolean (usually false unless task is done)
6. Respond ONLY with the JSON object, no additional text

Examples:

Clicking an element:
{
  "method": "click",
  "element": 0,
  "args": [],
  "step": "Click the first link on the page",
  "completed": false
}

Filling a form field:
{
  "method": "fill",
  "element": 1,
  "args": ["myusername"],
  "step": "Enter username into the login field",
  "completed": false
}

Pressing Enter key:
{
  "method": "press",
  "element": null,
  "args": ["Enter"],
  "step": "Submit the form by pressing Enter",
  "completed": false
}

Navigating to URL:
{
  "method": "goto",
  "element": null,
  "args": ["https://example.com"],
  "step": "Navigate to example.com",
  "completed": false
}

Task completed:
{
  "method": "click",
  "element": 0,
  "args": [],
  "step": "Clicked the link as requested",
  "completed": true
}"""
        
        # Check if there's already a system message
        has_system = any(msg.get("role") == "system" for msg in enhanced_messages)
        
        if has_system:
            # Prepend instruction to existing system message
            for msg in enhanced_messages:
                if msg.get("role") == "system":
                    msg["content"] = json_instruction + "\n\n" + msg["content"]
                    break
        else:
            # Insert system message at the beginning
            enhanced_messages.insert(0, {
                "role": "system",
                "content": json_instruction
            })
        
        return enhanced_messages
    
    def _normalize_openai_response(self, response_data: Dict[str, Any], model: str) -> Dict[str, Any]:
        """
        Normalize OpenRouter response to strict OpenAI format for Stagehand compatibility.
        Ensures all required fields are present and properly formatted.
        """
        import json
        import time
        
        # Ensure top-level fields exist
        normalized = {
            "id": response_data.get("id", f"chatcmpl-{int(time.time())}"),
            "object": "chat.completion",
            "created": response_data.get("created", int(time.time())),
            "model": response_data.get("model", model),
            "choices": [],
            "usage": response_data.get("usage", {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            })
        }
        
        # Process choices
        if "choices" in response_data and len(response_data["choices"]) > 0:
            for choice in response_data["choices"]:
                # Get the message content
                message = choice.get("message", {})
                content = message.get("content", "")
                
                # Ensure content is a string (not None)
                if content is None:
                    content = ""
                
                # Validate and format JSON content
                content = self._ensure_json_content(content)
                
                # Build normalized choice
                normalized_choice = {
                    "index": choice.get("index", 0),
                    "message": {
                        "role": message.get("role", "assistant"),
                        "content": content
                    },
                    "finish_reason": choice.get("finish_reason", "stop"),
                    "logprobs": choice.get("logprobs", None)
                }
                
                # Add tool_calls if present (for function calling)
                if "tool_calls" in message:
                    normalized_choice["message"]["tool_calls"] = message["tool_calls"]
                
                normalized["choices"].append(normalized_choice)
        else:
            # No choices returned, create a default one with JSON
            normalized["choices"] = [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps({
                        "method": "waitForTimeout",
                        "element": None,
                        "args": [1000],
                        "step": "I apologize, but I couldn't generate a response.",
                        "completed": False
                    })
                },
                "finish_reason": "stop",
                "logprobs": None
            }]
        
        return normalized
    
    def _ensure_json_content(self, content: str) -> str:
        """
        Ensure the content is valid JSON with valid computer use actions.
        Validates and fixes action names if needed.
        """
        import json
        
        # If content is empty, return default JSON
        if not content or content.strip() == "":
            return json.dumps({
                "method": "waitForTimeout",
                "element": None,
                "args": [1000],
                "step": "No action specified - waiting",
                "completed": False
            })
        
        # If content is a dict, convert to JSON
        if isinstance(content, dict):
            content = json.dumps(content)
        
        # If content is not a string, convert it
        if not isinstance(content, str):
            content = str(content)
        
        # Try to parse as JSON to validate
        try:
            # Try to parse the content as JSON
            parsed = json.loads(content)
            
            # Validate and fix the action if needed
            validated_json = self._validate_computer_action(parsed)
            
            # Return the validated JSON
            return json.dumps(validated_json)
            
        except (json.JSONDecodeError, ValueError):
            # Content is not valid JSON, wrap it in a JSON structure
            # Check if it looks like it's trying to be JSON but has formatting issues
            content_stripped = content.strip()
            
            if content_stripped.startswith('{') or content_stripped.startswith('['):
                # Looks like attempted JSON, try to extract or fix it
                try:
                    # Try to find JSON in the content
                    import re
                    json_match = re.search(r'\{.*\}', content_stripped, re.DOTALL)
                    if json_match:
                        potential_json = json_match.group(0)
                        parsed = json.loads(potential_json)  # Validate
                        validated = self._validate_computer_action(parsed)
                        return json.dumps(validated)
                except:
                    pass
            
            # Wrap plaintext response in JSON structure
            return json.dumps({
                "method": "click",
                "element": 0,
                "args": [],
                "step": content,
                "completed": False
            })
    
    def _validate_computer_action(self, action_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize to Stagehand's internal action schema.
        Ensures response has method, element, args, step, and completed fields.
        """
        # Valid Playwright methods (what Stagehand uses internally)
        VALID_METHODS = {
            "click", "fill", "press", "hover", "scrollIntoViewIfNeeded",
            "selectOption", "check", "uncheck", "goto", "waitForTimeout",
            "type", "screenshot", "evaluate"
        }
        
        # Handle various input formats and convert to Stagehand's schema
        validated = {}
        
        # Determine the method
        method = action_json.get("method") or action_json.get("action", "click")
        method = method.lower() if method else "click"
        
        # Map common variations to valid Playwright methods
        method_mappings = {
            "type": "fill",  # Stagehand uses "fill" for typing
            "input": "fill",
            "enter": "fill",
            "write": "fill",
            "key": "press",
            "keypress": "press",
            "navigate": "goto",
            "scroll": "scrollIntoViewIfNeeded",
            "wait": "waitForTimeout",
            "left_click": "click",
            "right_click": "click",
            "move": "hover"
        }
        
        if method in method_mappings:
            original_method = method
            method = method_mappings[method]
            print(f"Mapped method: {original_method} -> {method}")
        
        # Default to "click" if method is unknown
        if method not in VALID_METHODS:
            print(f"Unknown method '{method}', using 'click'")
            method = "click"
        
        validated["method"] = method
        
        # Get element number (convert selector to element index)
        # If no element specified, use 0 for element-based actions, null for page-level
        element = action_json.get("element")
        
        if element is None:
            # Determine if this is a page-level action
            page_level_methods = {"goto", "waitForTimeout", "evaluate", "screenshot"}
            if method in page_level_methods:
                element = None
            else:
                # Default to first element (0) for element-based actions
                element = 0
        
        # Ensure element is int or None
        if element is not None:
            try:
                element = int(element)
            except (ValueError, TypeError):
                element = 0
        
        validated["element"] = element
        
        # Build args array based on method type
        args = []
        
        if method == "fill":
            # Fill needs text argument
            text = (action_json.get("args", [None])[0] if isinstance(action_json.get("args"), list) else
                   action_json.get("text") or 
                   action_json.get("value") or 
                   action_json.get("arguments", {}).get("text") or
                   "")
            args = [text]
        
        elif method == "press":
            # Press needs key name
            key = (action_json.get("args", [None])[0] if isinstance(action_json.get("args"), list) else
                  action_json.get("key") or 
                  action_json.get("arguments", {}).get("key") or
                  "Enter")
            args = [key]
        
        elif method == "goto":
            # Goto needs URL
            url = (action_json.get("args", [None])[0] if isinstance(action_json.get("args"), list) else
                  action_json.get("url") or 
                  action_json.get("arguments", {}).get("url") or
                  action_json.get("selector") or  # Sometimes URL is in selector
                  "")
            args = [url]
        
        elif method == "waitForTimeout":
            # Wait needs duration in milliseconds
            duration = (action_json.get("args", [None])[0] if isinstance(action_json.get("args"), list) else
                       action_json.get("duration") or 
                       action_json.get("arguments", {}).get("duration") or
                       1000)
            try:
                duration = int(duration)
            except (ValueError, TypeError):
                duration = 1000
            args = [duration]
        
        elif method == "selectOption":
            # SelectOption needs value
            value = (action_json.get("args", [None])[0] if isinstance(action_json.get("args"), list) else
                    action_json.get("value") or 
                    action_json.get("arguments", {}).get("value") or
                    "")
            args = [value]
        
        else:
            # For methods that don't need args (click, hover, etc.)
            # Check if args were provided
            if "args" in action_json and isinstance(action_json["args"], list):
                args = action_json["args"]
            else:
                args = []
        
        validated["args"] = args
        
        # Get step (human-readable description)
        step = (action_json.get("step") or 
               action_json.get("description") or 
               action_json.get("reasoning") or 
               action_json.get("message") or
               f"Perform {method} action")
        validated["step"] = step
        
        # Get completed status
        completed = action_json.get("completed", False)
        # Ensure it's a boolean
        if isinstance(completed, str):
            completed = completed.lower() in ("true", "yes", "1", "completed")
        validated["completed"] = bool(completed)
        
        return validated
    
    async def async_chat_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Async version of chat_completion for use with FastAPI.
        Currently wraps the synchronous version, but can be upgraded to use aiohttp.
        """
        return self.chat_completion(messages, model, temperature, max_tokens, **kwargs)
    
    def test_connection(self) -> bool:
        """
        Test the connection to OpenRouter API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            # Check if there's an error in the response
            if "error" in response:
                print(f"OpenRouter connection test failed: {response.get('error')}")
                return False
            return True
        except Exception as e:
            print(f"OpenRouter connection test exception: {str(e)}")
            return False
