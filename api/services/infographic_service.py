"""
Infographic Service - Unified Entry Point
Main service for the complete infographic generation workflow.

This module orchestrates all components of the infographic generation system:
1. Input Processing - Multi-source input handling
2. Topic Generation - CTO/CEO dual-perspective with "how-to" framework
3. Prompt Building - 9-section structured prompt generation
4. Image Generation - Novita AI API integration
5. Quality Validation - Sequence number verification

Key Features:
- All English content, high information density
- Maximum 4 colors, 14px body text
- Clean business style, no decorations
- Data visualization support
- Key numbers 32-48px highlighted
- CRITICAL: Sequence number validation

Usage:
    from api.services.infographic_service import infographic_service

    result = infographic_service.generate_from_text(
        content="Client industry background...",
        job_title="ceo",
        perspective="hybrid"
    )
"""
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from api.services.infographic.input_processor import (
    InputProcessor,
    InputType,
    ProcessedInput,
    get_input_processor
)
from api.services.infographic.topic_generator import (
    TopicGenerator,
    Perspective,
    GeneratedTopic,
    get_topic_generator,
    resolve_perspective,
)
from api.services.infographic.prompt_builder import (
    PromptBuilder,
    ColorScheme,
    InfographicSpec,
    get_prompt_builder
)
from api.services.infographic.image_generator import (
    ImageGenerator,
    get_image_generator
)
from api.services.infographic.quality_validator import (
    QualityValidator,
    ValidationResult,
    get_quality_validator
)
from api.services.infographic.industry_researcher import (
    IndustryResearcher,
    get_industry_researcher
)

logger = logging.getLogger(__name__)


class GenerationStatus(Enum):
    """Generation status"""
    PENDING = "pending"
    VALIDATING = "validating"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class GenerationResult:
    """Result of infographic generation"""
    success: bool
    status: GenerationStatus
    topic: str
    prompt: str = ""
    image_url: str = ""
    local_path: str = ""
    validation_result: Optional[ValidationResult] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    message: str = ""
    results: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "status": self.status.value,
            "topic": self.topic,
            "prompt": self.prompt,
            "image_url": self.image_url,
            "local_path": self.local_path,
            "validation": self.validation_result.to_dict() if self.validation_result else None,
            "metadata": self.metadata,
            "error": self.error,
            "message": self.message,
            "results": self.results
        }


class InfographicService:
    """
    Unified Infographic Generation Service

    Orchestrates the complete workflow from input processing to image generation.

    Workflow:
        1. Process input (text/PDF/web) → structured background
        2. Generate topic (CTO/CEO perspective) → content framework
        3. Build prompt (9-section structure) → generation instructions
        4. Validate prompt (sequence check) → quality assurance
        5. Generate image (Novita AI) → final output
        6. Validate image (OCR) → final verification
    """

    def __init__(self):
        """Initialize infographic service"""
        self.input_processor = get_input_processor()
        self.topic_generator = get_topic_generator()
        self.prompt_builder = get_prompt_builder()
        self.image_generator = get_image_generator()
        self.quality_validator = get_quality_validator()
        self.industry_researcher = get_industry_researcher()

        # Pre-import design specification engine (avoid repeated in-loop imports)
        from api.services.infographic.design_specification import get_design_specification_engine
        self.design_engine = get_design_specification_engine()

        # Default configuration
        self.default_color_scheme = ColorScheme.FOREST
        self.default_perspective = Perspective.HYBRID
        self.default_framework = "how-to"

        logger.info("InfographicService initialized")

    def generate_from_text(
        self,
        content: str,
        job_title: str = "ceo",
        perspective: str = "hybrid",
        framework: str = "how-to",
        color_scheme: str = "forest",
        validate_prompt: bool = True,
        save_local: bool = True,
        count: int = 1
    ) -> GenerationResult:
        """
        Generate infographic from text content

        Args:
            content: Industry background/context (NOT the content itself)
            job_title: Target job title
            perspective: Content perspective (cto/ceo/hybrid)
            framework: Content framework (how-to, listicle, comparison)
            color_scheme: Color scheme (forest, ocean, minimal)
            validate_prompt: Whether to validate prompt before generation
            save_local: Whether to save image locally
            count: Number of infographics to generate

        Returns:
            GenerationResult with all outputs (results field contains multiple results)
        """
        try:
            logger.info(f"Starting infographic generation for {job_title}, count={count}")

            # Step 1: Process input
            processed = self.input_processor.process(
                input_data=content,
                input_type=InputType.TEXT
            )

            # Step 2: Generate topics — use safe enum resolution
            perspective_enum = resolve_perspective(perspective)
            topics = self.topic_generator.generate(
                industry_context=processed.raw_content,
                job_title=job_title,
                perspective=perspective_enum,
                framework=framework,
                count=count
            )

            if not topics:
                return GenerationResult(
                    success=False,
                    status=GenerationStatus.FAILED,
                    topic="",
                    error="Failed to generate topics",
                    message="Failed to generate topics from input"
                )

            # Step 2.1: Validate content quality
            logger.info("Validating content quality...")
            for idx, topic in enumerate(topics):
                content_validation = self.prompt_builder.validate_content_quality(topic.key_points)

                if not content_validation["passed"]:
                    logger.warning(f"Content validation failed for topic {idx+1}: {content_validation['issues']}")
                    # Log issues but continue - content can still be useful
                    for issue in content_validation["issues"]:
                        logger.warning(f"  - {issue}")

                if content_validation.get("warnings"):
                    for warning in content_validation["warnings"]:
                        logger.info(f"  - {warning}")

                logger.info(f"Content validation for topic {idx+1}: {content_validation['total_points']} points, {len(content_validation['issues'])} issues, {len(content_validation['warnings'])} warnings")

            # Step 2.5: Industry research for real data and charts
            logger.info("Conducting industry research for real data...")
            research_data = self.industry_researcher.research(
                topic=processed.raw_content[:100],  # First 100 chars as topic hint
                perspective=perspective,
                focus_areas=["market", "trends", "statistics"]
            )
            logger.info(f"Research completed: {len(research_data.get('statistics', []))} stats, {len(research_data.get('charts', []))} charts")

            # Step 3-7: Generate infographics for each topic — run in parallel
            results_map: Dict[int, Dict] = {}
            scheme = ColorScheme[color_scheme.upper()]

            def _generate_single(idx: int, topic) -> Dict[str, Any]:
                """Generate one infographic — runs inside a thread."""
                try:
                    logger.info(f"[Thread-{idx+1}] Generating: {topic.topic}")

                    content_for_analysis = " ".join(topic.key_points)
                    data_characteristics = self.design_engine.analyze_data_characteristics(
                        content_for_analysis, research_data
                    )
                    design_spec = self.design_engine.generate_specification(data_characteristics)

                    prompt = self.prompt_builder.build_from_topic(
                        topic=topic.topic,
                        key_points=topic.key_points,
                        color_scheme=scheme,
                        subtitle="Practical insights and actionable strategies",
                        research_data=research_data,
                        design_specification=design_spec
                    )

                    if validate_prompt:
                        actual_module_count = design_spec.section_count if design_spec else len(topic.key_points)
                        validation = self.quality_validator.validate_prompt(
                            prompt=prompt,
                            expected_module_count=actual_module_count
                        )
                        if not validation.passed:
                            logger.warning(f"[Thread-{idx+1}] Prompt validation failed: {validation.issues}")
                        critical_issues = [i for i in validation.issues if i.get("severity") == "critical"]
                        if critical_issues:
                            return {"success": False, "topic": topic.topic, "error": f"Critical validation issues: {critical_issues}"}

                    image_result = self.image_generator.generate(prompt=prompt, save_local=save_local)
                    if not image_result.get("success"):
                        return {"success": False, "topic": topic.topic, "error": image_result.get("error", "Unknown generation error")}

                    initial_image_path = image_result.get("local_path", "")
                    final_image_path = initial_image_path
                    image_validation = None

                    if save_local and initial_image_path:
                        image_validation = self.quality_validator.validate_image(
                            image_path=final_image_path,
                            expected_module_count=len(topic.key_points)
                        )

                        if image_validation and not image_validation.passed:
                            logger.warning(f"[Thread-{idx+1}] Validation failed — attempting img2img correction")
                            sequence_errors = [i for i in image_validation.issues if "sequence" in i.get("type", "").lower()]
                            if sequence_errors:
                                correction_prompt = (
                                    "Fix all text, spelling, sequence numbers, and background colours in this infographic. "
                                    "Change all module backgrounds to pure white (#FFFFFF). "
                                    "Preserve the layout exactly — only fix text and colour issues."
                                )
                                for attempt in range(2):
                                    correction_result = self.image_generator.edit_image(
                                        image_path=final_image_path,
                                        prompt=correction_prompt,
                                        save_local=True
                                    )
                                    if correction_result.get("success"):
                                        final_image_path = correction_result.get("local_path", final_image_path)
                                        image_validation = self.quality_validator.validate_image(
                                            image_path=final_image_path,
                                            expected_module_count=len(topic.key_points)
                                        )
                                        if image_validation.passed:
                                            break
                                image_result["local_path"] = final_image_path
                                image_result["image_url"] = correction_result.get("image_url", image_result.get("image_url"))

                    image_result["local_path"] = final_image_path
                    return {
                        "success": True,
                        "topic": topic.topic,
                        "prompt": prompt,
                        "image_url": image_result.get("image_url", ""),
                        "local_path": image_result.get("local_path", ""),
                        "validation_result": image_validation,
                        "metadata": {
                            "perspective": perspective,
                            "framework": framework,
                            "color_scheme": color_scheme,
                            "module_count": len(topic.key_points),
                            "job_title": job_title
                        }
                    }
                except Exception as e:
                    logger.error(f"[Thread-{idx+1}] Error: {e}", exc_info=True)
                    return {"success": False, "topic": topic.topic if topic else "Unknown", "error": str(e)}

            # Run all topics in parallel (capped at count threads)
            with ThreadPoolExecutor(max_workers=min(count, 4)) as executor:
                future_to_idx = {executor.submit(_generate_single, i, t): i for i, t in enumerate(topics)}
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    results_map[idx] = future.result()

            # Reassemble in original order
            results = [results_map[i] for i in sorted(results_map)]

            # Return combined results
            successful_count = len([r for r in results if r.get("success")])
            return GenerationResult(
                success=successful_count > 0,
                status=GenerationStatus.COMPLETED if successful_count > 0 else GenerationStatus.FAILED,
                topic=f"Generated {successful_count}/{count} infographics",
                results=results,
                message=f"Successfully generated {successful_count} out of {count} infographics",
                metadata={
                    "total_requested": count,
                    "successful": successful_count,
                    "failed": len(results) - successful_count
                }
            )

        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            return GenerationResult(
                success=False,
                status=GenerationStatus.FAILED,
                topic="",
                error=str(e),
                message=f"Generation error: {str(e)}"
            )

    def generate_from_url(
        self,
        url: str,
        job_title: str = "ceo",
        **kwargs
    ) -> GenerationResult:
        """Generate infographic from web URL"""
        processed = self.input_processor.process(url, InputType.URL)
        return self.generate_from_text(
            content=processed.raw_content,
            job_title=job_title,
            **kwargs
        )

    def generate_from_file(
        self,
        file_content: bytes,
        filename: str,
        job_title: str = "ceo",
        **kwargs
    ) -> GenerationResult:
        """Generate infographic from uploaded file (PDF, TXT, MD)"""
        try:
            # Save to temporary file for processing
            import tempfile
            import os

            # Create temp file with appropriate extension
            suffix = Path(filename).suffix
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=suffix) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name

            try:
                # Process based on file type
                if suffix.lower() == '.pdf':
                    processed = self.input_processor.process(tmp_path, InputType.PDF)
                else:
                    # For TXT, MD, treat as text
                    text_content = file_content.decode('utf-8')
                    processed = self.input_processor.process(text_content, InputType.TEXT)

                return self.generate_from_text(
                    content=processed.raw_content,
                    job_title=job_title,
                    **kwargs
                )
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)
            return GenerationResult(
                success=False,
                status=GenerationStatus.FAILED,
                topic="",
                error=f"File processing error: {str(e)}"
            )

    def generate_from_pdf(
        self,
        pdf_path: str,
        job_title: str = "ceo",
        **kwargs
    ) -> GenerationResult:
        """Generate infographic from PDF file"""
        processed = self.input_processor.process(pdf_path, InputType.PDF)
        return self.generate_from_text(
            content=processed.raw_content,
            job_title=job_title,
            **kwargs
        )

    def generate_dual_perspective(
        self,
        content: str,
        job_title: str = "ceo",
        framework: str = "how-to"
    ) -> Dict[str, GenerationResult]:
        """
        Generate both CTO and CEO perspective infographics

        Returns:
            Dict with "cto" and "ceo" keys
        """
        results = {}

        for perspective_name in ["cto", "ceo"]:
            results[perspective_name] = self.generate_from_text(
                content=content,
                job_title=job_title,
                perspective=perspective_name,
                framework=framework
            )

        return results

    def validate_only(
        self,
        prompt: str,
        expected_module_count: int
    ) -> ValidationResult:
        """
        Validate a prompt without generating

        Useful for testing and debugging.
        """
        return self.quality_validator.validate_prompt(
            prompt=prompt,
            expected_module_count=expected_module_count
        )

    def build_prompt_from_keypoints(
        self,
        title: str,
        key_points: List[str],
        color_scheme: str = "forest",
        subtitle: str = "",
        call_to_action: str = ""
    ) -> str:
        """
        Build a prompt from simple inputs

        Useful for quick testing or external integration.
        """
        scheme = ColorScheme[color_scheme.upper()]
        return self.prompt_builder.build_from_topic(
            topic=title,
            key_points=key_points,
            color_scheme=scheme,
            subtitle=subtitle,
            call_to_action=call_to_action
        )

    def get_color_schemes(self) -> List[str]:
        """Get available color schemes"""
        return [scheme.name.lower() for scheme in ColorScheme]

    def get_perspectives(self) -> List[str]:
        """Get available perspectives"""
        return [perspective.value for perspective in Perspective]

    def get_frameworks(self) -> List[str]:
        """Get available frameworks"""
        return ["how-to", "listicle", "comparison"]


# Global instance
_infographic_service_instance: Optional[InfographicService] = None


def get_infographic_service() -> InfographicService:
    """Get singleton infographic service instance"""
    global _infographic_service_instance
    if _infographic_service_instance is None:
        _infographic_service_instance = InfographicService()
    return _infographic_service_instance


# Export default instance
infographic_service = get_infographic_service()


# Convenience functions for quick access
def generate_infographic(
    content: str,
    job_title: str = "ceo",
    perspective: str = "hybrid",
    **kwargs
) -> GenerationResult:
    """
    Quick access function for infographic generation

    Args:
        content: Industry background/context
        job_title: Target job title
        perspective: Content perspective (cto/ceo/hybrid)
        **kwargs: Additional arguments

    Returns:
        GenerationResult
    """
    return infographic_service.generate_from_text(
        content=content,
        job_title=job_title,
        perspective=perspective,
        **kwargs
    )


def build_prompt(
    title: str,
    key_points: List[str],
    color_scheme: str = "forest"
) -> str:
    """
    Quick access function for prompt building

    Args:
        title: Main title
        key_points: List of content points
        color_scheme: Color scheme name

    Returns:
        Complete prompt string
    """
    return infographic_service.build_prompt_from_keypoints(
        title=title,
        key_points=key_points,
        color_scheme=color_scheme
    )
