# Infographic Service Configuration Example
# Copy this to your .env file and update with your API keys

# ============================================================================
# NOVITA AI API (Required for image generation)
# ============================================================================
# Get your API key from: https://novita.ai/
NOVITA_API_KEY=your-novita-api-key-here

# ============================================================================
# GROQ API (Recommended for topic generation - faster and more cost-effective)
# ============================================================================
# Get your API key from: https://console.groq.com/
GROQ_API_KEY=your-groq-api-key-here

# ============================================================================
# OPENAI API (Fallback if Groq is not available)
# ============================================================================
# Get your API key from: https://platform.openai.com/
OPENAI_API_KEY=your-openai-api-key-here

# ============================================================================
# Model Configuration
# ============================================================================
# Image generation model (default: gemini-2.5-flash-image)
IMAGE_MODEL=gemini-2.5-flash-image

# Default model for text generation (if using OpenAI)
DEFAULT_MODEL=gpt-4

# Maximum tokens for text generation
MAX_TOKENS=2000

# ============================================================================
# Output Configuration
# ============================================================================
# Local directory for saving generated images
# Relative to backend directory or absolute path
INFOGRAPHIC_OUTPUT_DIR=generated_images

# ============================================================================
# Quality Settings
# ============================================================================
# Maximum retries for failed image generations
MAX_GENERATION_RETRIES=3

# Timeout for API requests (seconds)
API_TIMEOUT=60

# ============================================================================
# OCR Configuration (Optional - for image validation)
# ============================================================================
# Install tesseract for local OCR validation:
# - Mac: brew install tesseract
# - Linux: sudo apt-get install tesseract-ocr
# - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

# Python packages required:
# pip install pytesseract Pillow
