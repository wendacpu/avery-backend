# Infographic Generation Service

A complete Python module system for generating professional LinkedIn infographics using AI.

## Architecture

```
Input Processing → Topic Generation → Prompt Building → Image Generation → Quality Validation
```

### Module Overview

| Module | Purpose | Key Features |
|--------|---------|--------------|
| `input_processor.py` | Multi-source input handling | Text, PDF, URL → Unified structure |
| `topic_generator.py` | Topic generation engine | CTO/CEO dual-perspective, "how-to" framework |
| `prompt_builder.py` | 9-section prompt builder | CRITICAL, LAYOUT, COLOR, TYPOGRAPHY, VISUAL, CONTENT, CHART, EMPHASIS, CHECKLIST |
| `image_generator.py` | AI image generation | Novita API integration, local saving |
| `quality_validator.py` | Quality validation | **Sequence number verification**, OCR support |
| `infographic_service.py` | Unified entry point | Orchestrates complete workflow |

## Quick Start

```python
from api.services.infographic_service import generate_infographic

# Generate an infographic
result = generate_infographic(
    content="Industry background about AI adoption in enterprises...",
    job_title="ceo",
    perspective="hybrid"
)

if result.success:
    print(f"Generated: {result.image_url}")
else:
    print(f"Error: {result.error}")
```

## Installation

### Required Python Packages

```bash
# Core dependencies
pip install httpx pydantic-settings openai

# Optional: For PDF processing
pip install PyPDF2

# Optional: For OCR validation
pip install pytesseract Pillow
brew install tesseract  # Mac
```

### Configuration

Copy `config.py` to your `.env` file and add your API keys:

```bash
NOVITA_API_KEY=your-key-here
GROQ_API_KEY=your-key-here  # Optional but recommended
```

## Workflow Requirements

### Success Factors

1. **Client files = Industry background** (NOT content source)
2. **All English content** - High information density
3. **Maximum 4 colors** - Clean business style
4. **14px body text** - Fixed size, no exceptions
5. **Key numbers 32-48px** - Highlighted for emphasis
6. **Data visualization** - Charts for statistics
7. **No decorations** - Professional, minimalist

### The "How-To" Framework

Topics are structured as actionable how-to guides:

1. Assess current state
2. Define clear objectives
3. Build alignment
4. Implement core capabilities
5. Measure and iterate
6. Scale successful patterns
7. Avoid common pitfalls

## Module Details

### 1. Input Processor (`input_processor.py`)

Handles multiple input sources:

```python
from api.services.infographic.input_processor import get_input_processor

processor = get_input_processor()

# From text
result = processor.process("Industry background text", InputType.TEXT)

# From URL
result = processor.process("https://example.com/article", InputType.URL)

# From PDF
result = processor.process("/path/to/file.pdf", InputType.PDF)
```

### 2. Topic Generator (`topic_generator.py`)

Generates topics with CTO/CEO perspectives:

```python
from api.services.infographic.topic_generator import get_topic_generator, Perspective

generator = get_topic_generator()

# Generate CTO perspective
topics = generator.generate(
    industry_context="AI industry background...",
    job_title="cto",
    perspective=Perspective.CTO,
    framework="how-to"
)

# Generate both perspectives
cto_topic, ceo_topic = generator.generate_dual_perspective(...)
```

### 3. Prompt Builder (`prompt_builder.py`)

Builds 9-section structured prompts:

```python
from api.services.infographic.prompt_builder import get_prompt_builder, ColorScheme

builder = get_prompt_builder()

prompt = builder.build_from_topic(
    topic="How to Implement AI in Your Business",
    key_points=[
        "Assess current capabilities: Audit existing data",
        "Define clear objectives: Set specific goals",
        # ... more points
    ],
    color_scheme=ColorScheme.FOREST
)
```

### 4. Image Generator (`image_generator.py`)

Generates images using Novita AI:

```python
from api.services.infographic.image_generator import get_image_generator

generator = get_image_generator()

result = generator.generate(
    prompt=prompt,
    save_local=True
)

if result["success"]:
    print(f"Image URL: {result['image_url']}")
    print(f"Local path: {result['local_path']}")
```

### 5. Quality Validator (`quality_validator.py`)

**CRITICAL**: Validates sequence numbers - the key fix for the production issue.

```python
from api.services.infographic.quality_validator import get_quality_validator

validator = get_quality_validator()

# Validate prompt before generation
validation = validator.validate_prompt(
    prompt=prompt,
    expected_module_count=7
)

print(f"Passed: {validation.passed}")
print(f"Score: {validation.score}")
print(f"Sequences: {validation.detected_sequences}")

# Validate generated image (requires OCR)
if result["local_path"]:
    image_validation = validator.validate_image(
        image_path=result["local_path"],
        expected_module_count=7
    )
```

## Color Schemes

Three predefined schemes (max 4 colors each):

### Forest (Default)
- Primary: #2D5A3D (forest green)
- Secondary: #C9A65C (gold)
- Background: #F7F4EF (beige)
- Accents: Light green, pale yellow, soft pink, sky blue

### Ocean
- Primary: #1E4A6B (ocean blue)
- Secondary: #D4A574 (tan)
- Background: #F0F4F8 (light gray-blue)

### Minimal
- Primary: #1F2937 (dark gray)
- Secondary: #6B7280 (medium gray)
- Background: #FFFFFF (white)

## Sequence Number Validation

**This is the critical fix for the production issue.**

The quality validator ensures:
1. Each sequence number (1, 2, 3...) appears **exactly once**
2. Numbers are **sequential** (no gaps, no duplicates)
3. Numbers are **clearly visible** in the generated image

```python
# Automatic validation
result = infographic_service.generate_from_text(
    content=industry_context,
    job_title="ceo",
    validate_prompt=True  # Validates before generation
)

# Manual validation
validation = infographic_service.validate_only(prompt, 7)
```

## API Reference

### InfographicService

Main service class with all methods:

```python
class InfographicService:
    def generate_from_text(content, job_title, perspective, **kwargs) -> GenerationResult
    def generate_from_url(url, job_title, **kwargs) -> GenerationResult
    def generate_from_pdf(pdf_path, job_title, **kwargs) -> GenerationResult
    def generate_dual_perspective(content, job_title) -> Dict[str, GenerationResult]
    def validate_only(prompt, expected_module_count) -> ValidationResult
    def build_prompt_from_keypoints(title, key_points, **kwargs) -> str
    def get_color_schemes() -> List[str]
    def get_perspectives() -> List[str]
    def get_frameworks() -> List[str]
```

### GenerationResult

```python
@dataclass
class GenerationResult:
    success: bool
    status: GenerationStatus
    topic: str
    prompt: str
    image_url: str
    local_path: str
    validation_result: ValidationResult
    metadata: Dict[str, Any]
    error: str
```

## Troubleshooting

### Issue: "Novita API key not configured"

**Solution**: Add `NOVITA_API_KEY` to your `.env` file

### Issue: "Sequence numbers not sequential"

**Solution**: The quality validator will auto-fix minor issues. For major issues, check your input key_points.

### Issue: "OCR not available"

**Solution**: Install `pytesseract` and system tesseract:
```bash
pip install pytesseract Pillow
brew install tesseract  # Mac
sudo apt install tesseract-ocr  # Linux
```

### Issue: "Non-English content detected"

**Solution**: All content must be in English. The validator checks for CJK characters.

## File Structure

```
backend/api/services/infographic/
├── __init__.py              # Package exports
├── config.py                # Configuration template
├── example_usage.py         # Usage examples
├── README.md                # This file
├── input_processor.py       # Input processing
├── topic_generator.py       # Topic generation
├── prompt_builder.py        # Prompt building
├── image_generator.py       # Image generation
├── quality_validator.py     # Quality validation
└── ../infographic_service.py  # Main entry point
```

## License

Internal use only.
