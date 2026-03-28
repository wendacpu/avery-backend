"""
Image Generator Module
Handles AI image generation using Novita AI API with local saving and retry logic.
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
    AI Image Generator using Novita AI API

    Features:
    - Novita AI API integration (Gemini 2.5 Flash)
    - Local image saving
    - Retry logic for failed generations
    - URL and base64 output support
    """

    def __init__(self):
        """Initialize image generator"""
        self.api_key = settings.novita_api_key
        self.model = settings.image_model or "gemini-2.5-flash-image"
        # Use gemini-2.5-flash-image for editing as requested
        self.enhancement_model = "gemini-2.5-flash-image" 
        self.api_base = "https://api.novita.ai/v3"
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)

        # Configuration
        self.max_retries = 3
        self.timeout = 60.0
        self.aspect_ratio = "3:4"  # LinkedIn optimized

        if self.api_key and self.api_key != "your-novita-api-key-here":
            logger.info(f"ImageGenerator initialized with model: {self.model}, enhancement_model: {self.enhancement_model}")
        else:
            logger.warning("Novita API key not configured")

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
            Dict with:
                - success: bool
                - image_url: str (if successful)
                - local_path: str (if saved locally)
                - error: str (if failed)
        """
        if not self.api_key or self.api_key == "your-novita-api-key-here":
            return self._get_mock_result(prompt)

        logger.info(f"Generating image with prompt length: {len(prompt)} chars")

        attempt = 0
        last_error = None

        while attempt < (self.max_retries if retry_on_failure else 1):
            attempt += 1
            try:
                result = self._generate_with_novita(prompt)

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

        # All retries failed
        logger.error(f"Image generation failed after {attempt} attempts: {last_error}")
        return {
            "success": False,
            "error": str(last_error),
            "attempts": attempt
        }

    def _generate_with_novita(self, prompt: str) -> Dict[str, Any]:
        """Generate image using Novita AI API"""
        url = f"{self.api_base}/{self.model}-text-to-image"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "prompt": prompt,
            "aspect_ratio": self.aspect_ratio
        }

        logger.info(f"Calling Novita API: {url}")

        response = httpx.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.timeout
        )

        response.raise_for_status()
        result = response.json()

        if "image_urls" in result and len(result["image_urls"]) > 0:
            image_url = result["image_urls"][0]
            logger.info(f"Image generated successfully: {image_url}")
            return {
                "success": True,
                "image_url": image_url,
                "model": self.model
            }
        else:
            raise GenerationError(f"Unexpected response format: {result}")

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
            # Don't fail the whole operation if local save fails
            return Path("")

    def _generate_filename(self, prompt: str) -> str:
        """Generate unique filename from prompt"""
        # Create hash of prompt for uniqueness
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]

        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return f"infographic_{timestamp}_{prompt_hash}.png"

    def edit_image(
        self,
        image_path: str,
        prompt: str,
        save_local: bool = True,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Edit existing image using image-to-image generation

        Args:
            image_path: Path or URL to source image
            prompt: Edit instruction prompt
            save_local: Whether to save edited image locally
            filename: Custom filename (auto-generated if None)

        Returns:
            Dict with:
                - success: bool
                - image_url: str (if successful)
                - local_path: str (if saved locally)
                - error: str (if failed)
        """
        if not self.api_key or self.api_key == "your-novita-api-key-here":
            return {
                "success": False,
                "error": "Novita API key not configured"
            }

        attempt = 0
        last_error = None

        while attempt < self.max_retries:
            attempt += 1
            try:
                result = self._edit_with_novita(image_path, prompt)

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
                    time.sleep(2 ** attempt)  # Exponential backoff

        return {
            "success": False,
            "error": f"Image edit failed after {attempt} attempts: {last_error}",
            "attempts": attempt
        }

    def _edit_with_novita(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Edit image using Novita Gemini 2.5 Flash Image Edit API"""
        # Endpoint precisely as per user specification
        url = f"{self.api_base}/{self.enhancement_model}-edit"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Convert local file to base64
        if image_path.startswith("http"):
            # If it's already a URL, we need to download it first or use image_urls
            # specification says choose either image_urls OR image_base64s. 
            # For consistency, let's keep it as base64 array as requested by the spec
            response = httpx.get(image_path, timeout=10)
            img_data = base64.b64encode(response.content).decode("utf-8")
        else:
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")

        # Wrap the user's prompt with strong modification instructions 
        # (Improves model adherence to the 'edit' intent)
        instruction_prompt = (
            f"DIRECTLY MODIFY the attached image: {prompt}. "
            f"Maintain the overall typography and professional list layout, "
            f"but change the visual elements as requested."
        )

        # Payload structure from user spec
        payload = {
            "prompt": instruction_prompt,
            "image_base64s": [img_data], # Array of string - NO prefix (data:image/...)
            "aspect_ratio": self.aspect_ratio
        }

        logger.info(f"Calling Novita Image Edit API: {url}")

        response = httpx.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.timeout
        )

        response.raise_for_status()
        result = response.json()

        if "image_urls" in result and len(result["image_urls"]) > 0:
            new_image_url = result["image_urls"][0]
            logger.info(f"Image edited successfully: {new_image_url}")
            return {
                "success": True,
                "image_url": new_image_url,
                "model": self.enhancement_model
            }
        else:
            raise GenerationError(f"Unexpected response format: {result}")

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

        Returns:
            Dict with:
                - valid: bool
                - issues: List[str]
                - suggestions: List[str]
        """
        issues = []
        suggestions = []

        # Check prompt length
        if len(prompt) < 100:
            issues.append("Prompt too short (< 100 chars)")
        elif len(prompt) > 4000:
            issues.append("Prompt too long (> 4000 chars)")

        # Check for required sections
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

        # Check for sequence numbers
        import re
        sequences = re.findall(r'\bModule\s+(\d+)', prompt)
        if sequences:
            # Check if sequential
            sequences_int = [int(s) for s in sequences]
            if sequences_int != list(range(1, len(sequences_int) + 1)):
                issues.append("Module numbers are not sequential")

        # Check for English content
        # Simple heuristic: check for common non-English characters
        non_english = sum(1 for c in prompt if ord(c) > 127 and c not in "—–")
        if non_english > len(prompt) * 0.1:  # More than 10% non-ASCII
            issues.append("Prompt may contain non-English content")

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
