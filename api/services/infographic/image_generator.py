"""
Image Generator Module
Handles AI image generation using Vidu API with local saving and async polling logic.
"""
import logging
import httpx
import base64
import time
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import hashlib

from api.core.config import settings

logger = logging.getLogger(__name__)


class GenerationError(Exception):
    """Image generation error"""
    pass


class ImageGenerator:
    """
    AI Image Generator using Vidu API

    Features:
    - Vidu API integration (nano/q2-fast, nano pro/q2-pro, nano 2/q3-fast)
    - Local image saving
    - Asynchronous polling logic for task checking
    - URL and base64 output support
    """

    def __init__(self):
        """Initialize image generator"""
        self.api_key = getattr(settings, "vidu_api_key", getattr(settings, "novita_api_key", None))
        
        # User defined mapping: q2-fast (nano), q2-pro (nano pro), q3-fast (nano 2)
        model_name = settings.image_model or "q2-fast"
        # Backward compatibility if it still is gemini
        if "gemini" in model_name:
            self.model = "q2-fast"
        else:
            self.model = model_name
            
        self.enhancement_model = "q3-fast" 
        self.api_base = "https://api.vidu.cn/ent/v2"
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)

        # Configuration
        self.max_retries = 3
        self.timeout = 60.0
        self.polling_interval = 3.0
        self.max_polling_time = 120.0
        self.aspect_ratio = "3:4"  # Default aspect ratio

        if self.api_key and self.api_key != "your-api-key-here" and "your-novita" not in self.api_key:
            logger.info(f"ImageGenerator initialized with Vidu model: {self.model}, enhancement model: {self.enhancement_model}")
        else:
            logger.warning("Vidu API key not configured")

    def generate(
        self,
        prompt: str,
        save_local: bool = True,
        filename: Optional[str] = None,
        retry_on_failure: bool = True
    ) -> Dict[str, Any]:
        """
        Generate image from prompt

        Args:
            prompt: Complete prompt text
            save_local: Whether to save image locally
            filename: Custom filename (auto-generated if None)
            retry_on_failure: Whether to retry on failure

        Returns:
            Dict with success, image_url, local_path, error etc.
        """
        if not self.api_key or self.api_key == "your-api-key-here" or "your-novita" in self.api_key:
            return self._get_mock_result(prompt)

        logger.info(f"Generating image with prompt length: {len(prompt)} chars")

        attempt = 0
        last_error = None

        while attempt < (self.max_retries if retry_on_failure else 1):
            attempt += 1
            try:
                result = self._generate_with_vidu(prompt=prompt, model=self.model)

                if result["success"] and save_local:
                    local_path = self._save_image(
                        result["image_url"],
                        filename or self._generate_filename(prompt)
                    )
                    result["local_path"] = str(local_path)

                return result

            except Exception as e:
                last_error = e
                logger.warning(f"Generation attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    logger.info(f"Retrying... ({attempt}/{self.max_retries})")

        logger.error(f"Image generation failed after {attempt} attempts: {last_error}")
        return {
            "success": False,
            "error": str(last_error),
            "attempts": attempt
        }

    def _generate_with_vidu(self, prompt: str, model: str, image_path: str = None) -> Dict[str, Any]:
        """Generate or edit image using Vidu API and poll until completion"""
        url = f"{self.api_base}/reference2image/nano"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.api_key}"
        }

        # Vidu limit prompt length
        safe_prompt = prompt[:5000]

        payload = {
            "model": model,
            "prompt": safe_prompt,
            "aspect_ratio": self.aspect_ratio
        }

        if image_path:
            # Process reference image to base64
            if image_path.startswith("http"):
                response = httpx.get(image_path, timeout=10)
                file_ext = image_path.split('.')[-1][:4].lower()
                mime_type = "image/jpeg" if file_ext in ["jpg", "jpeg"] else "image/png"
                b64_data = base64.b64encode(response.content).decode("utf-8")
            else:
                with open(image_path, "rb") as f:
                    file_ext = image_path.split('.')[-1].lower()
                    mime_type = "image/jpeg" if file_ext in ["jpg", "jpeg"] else "image/png"
                    b64_data = base64.b64encode(f.read()).decode("utf-8")
                    
            # For editing we might want to ensure prompt relates to editing
            payload["images"] = [f"data:{mime_type};base64,{b64_data}"]
            payload["prompt"] = f"修改图片: {safe_prompt}"[:5000]

        logger.info(f"Calling Vidu Create API: {url} with model {model}")

        response = httpx.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()

        task_id = result.get("task_id")
        if not task_id:
            # Sometimes doc might use 'id' instead of 'task_id' but their example states task_id inside creation, wait their task query doc says `id` ? Let's check both
            task_id = result.get("id") 
            if not task_id:
                raise GenerationError(f"Unexpected start response missing task_id: {result}")

        return self._poll_vidu_task(task_id, headers, model)

    def _poll_vidu_task(self, task_id: str, headers: dict, model: str) -> Dict[str, Any]:
        """Poll the Vidu task query API until completion"""
        query_url = f"{self.api_base}/tasks/{task_id}/creations"
        
        start_time = time.time()
        
        while True:
            if time.time() - start_time > self.max_polling_time:
                raise GenerationError(f"Polling timeout after {self.max_polling_time}s for Vidu task {task_id}")
                
            time.sleep(self.polling_interval)
            
            logger.info(f"Checking Vidu task {task_id} status...")
            response = httpx.get(query_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            poll_result = response.json()
            state = poll_result.get("state")
            
            if state == "success":
                creations = poll_result.get("creations", [])
                if creations and len(creations) > 0 and "url" in creations[0]:
                    image_url = creations[0]["url"]
                    logger.info(f"Vidu image generated successfully: {image_url}")
                    return {
                        "success": True,
                        "image_url": image_url,
                        "model": model,
                        "task_id": task_id
                    }
                else:
                    raise GenerationError(f"Task succeeded but no image URL found: {poll_result}")
            elif state == "failed":
                err_code = poll_result.get("err_code", "Unknown error")
                raise GenerationError(f"Vidu generation task failed with err_code: {err_code}")
            elif state in ["created", "queueing", "processing"]:
                continue # keep polling
            else:
                raise GenerationError(f"Unknown Vidu task state '{state}': {poll_result}")

    def edit_image(
        self,
        image_path: str,
        prompt: str,
        save_local: bool = True,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Edit existing image using Vidu Reference to Image
        """
        if not self.api_key or self.api_key == "your-api-key-here" or "your-novita" in self.api_key:
            return {
                "success": False,
                "error": "Vidu API key not configured"
            }

        attempt = 0
        last_error = None

        while attempt < self.max_retries:
            attempt += 1
            try:
                # Use enhancement_model for edit tasks ideally
                result = self._generate_with_vidu(prompt=prompt, model=self.enhancement_model, image_path=image_path)

                if result["success"] and save_local:
                    local_path = self._save_image(
                        result["image_url"],
                        filename or self._generate_filename(f"edit_{prompt}")
                    )
                    result["local_path"] = str(local_path)

                return result

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Image edit attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)

        return {
            "success": False,
            "error": f"Image edit failed after {attempt} attempts: {last_error}",
            "attempts": attempt
        }

    def _save_image(self, image_url: str, filename: str) -> Path:
        """Save image from URL to local file"""
        local_path = self.output_dir / filename

        try:
            response = httpx.get(image_url, timeout=30.0)
            response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Image saved locally: {local_path}")
            return local_path

        except Exception as e:
            logger.error(f"Failed to save image locally: {e}")
            return Path("")

    def _generate_filename(self, prompt: str) -> str:
        """Generate unique filename from prompt"""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"infographic_{timestamp}_{prompt_hash}.png"

    def _get_mock_result(self, prompt: str) -> Dict[str, Any]:
        """Get mock result when API is not configured"""
        logger.warning("Using mock image result (API not configured)")
        seed = abs(hash(prompt)) % 1000
        mock_url = f"https://picsum.photos/1024/1366?random={seed}"

        return {
            "success": True,
            "image_url": mock_url,
            "local_path": None,
            "mock": True
        }

    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Validate prompt before generation
        """
        issues = []
        suggestions = []

        if len(prompt) < 100:
            issues.append("Prompt too short (< 100 chars)")
        elif len(prompt) > 5000:
            issues.append("Prompt too long (> 5000 chars)")

        required_sections = [
            "CRITICAL", "LAYOUT", "COLOR", "TYPOGRAPHY",
            "VISUAL", "CONTENT", "CHECKLIST"
        ]

        missing_sections = []
        for section in required_sections:
            if section not in prompt:
                missing_sections.append(section)

        if missing_sections:
            issues.append(f"Missing sections: {', '.join(missing_sections)}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }


# Global instance
_image_generator_instance: Optional[ImageGenerator] = None

def get_image_generator() -> ImageGenerator:
    """Get singleton image generator instance"""
    global _image_generator_instance
    if _image_generator_instance is None:
        _image_generator_instance = ImageGenerator()
    return _image_generator_instance
