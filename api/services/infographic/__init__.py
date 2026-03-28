"""
Infographic Generation Modules Package

Core modules for the infographic generation system:
- input_processor: Multi-source input processing
- topic_generator: CTO/CEO dual-perspective topic generation
- prompt_builder: 9-section structured prompt building
- image_generator: Novita AI image generation
- quality_validator: Quality validation with sequence verification

Main entry point: api.services.infographic_service
"""
from .input_processor import (
    InputProcessor,
    InputType,
    ProcessedInput,
    get_input_processor
)

from .topic_generator import (
    TopicGenerator,
    Perspective,
    GeneratedTopic,
    get_topic_generator
)

from .prompt_builder import (
    PromptBuilder,
    ColorScheme,
    ContentModule,
    InfographicSpec,
    get_prompt_builder
)

from .image_generator import (
    ImageGenerator,
    GenerationError,
    get_image_generator
)

from .quality_validator import (
    QualityValidator,
    ValidationResult,
    ValidationIssue,
    get_quality_validator
)

__all__ = [
    # Input Processing
    "InputProcessor",
    "InputType",
    "ProcessedInput",
    "get_input_processor",

    # Topic Generation
    "TopicGenerator",
    "Perspective",
    "GeneratedTopic",
    "get_topic_generator",

    # Prompt Building
    "PromptBuilder",
    "ColorScheme",
    "ContentModule",
    "InfographicSpec",
    "get_prompt_builder",

    # Image Generation
    "ImageGenerator",
    "GenerationError",
    "get_image_generator",

    # Quality Validation
    "QualityValidator",
    "ValidationResult",
    "ValidationIssue",
    "get_quality_validator",
]
