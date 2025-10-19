import requests
import base64
import json
from pathlib import Path

class UIDesignAnalyzer:
    def __init__(self):
        self.api_key = "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"
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "openai/gpt-5-nano"
    
    def encode_image(self, image_path):
        """Convert image to base64 for API submission"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_ui(self, image_path):
        """Analyze UI design quality"""
        # Validate image exists and get file info
        img_path = Path(image_path)
        if not img_path.exists():
            return {"error": f"Image not found: {image_path}"}
        
        # Check file size (most APIs have limits)
        file_size_mb = img_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 20:
            return {"error": f"Image too large: {file_size_mb:.2f}MB. Maximum 20MB"}
        
        # Get image format
        file_format = img_path.suffix.lower()
        valid_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if file_format not in valid_formats:
            return {"error": f"Invalid format: {file_format}. Use {', '.join(valid_formats)}"}
        
        # Encode image
        base64_image = self.encode_image(image_path)
        
        # Construct the prompt
        prompt = """Analyze this UI design screenshot and evaluate it across these criteria:"""