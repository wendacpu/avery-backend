#!/usr/bin/env python3
"""
Infographic Service Usage Examples

Demonstrates how to use the infographic generation system.
"""
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the service
from api.services.infographic_service import (
    infographic_service,
    generate_infographic,
    build_prompt
)

logger = logging.getLogger(__name__)


def example_1_basic_generation():
    """Example 1: Basic infographic generation from text"""
    print("\n" + "="*60)
    print("Example 1: Basic Infographic Generation")
    print("="*60)

    # Client industry background (NOT the content itself)
    industry_context = """
    The AI industry is experiencing rapid growth with enterprises
    adopting machine learning solutions for automation and efficiency.
    Key trends include large language models, computer vision applications,
    and predictive analytics for business intelligence.
    """

    result = infographic_service.generate_from_text(
        content=industry_context,
        job_title="ceo",
        perspective="hybrid",
        framework="how-to"
    )

    if result.success:
        print(f"Success! Generated: {result.topic}")
        print(f"Image URL: {result.image_url}")
        print(f"Local path: {result.local_path}")
    else:
        print(f"Failed: {result.error}")


def example_2_custom_keypoints():
    """Example 2: Generate from custom key points"""
    print("\n" + "="*60)
    print("Example 2: Custom Key Points")
    print("="*60)

    title = "How to Implement AI in Your Business"
    key_points = [
        "Assess current capabilities: Audit existing data and infrastructure",
        "Define clear objectives: Set specific, measurable business goals",
        "Build cross-functional team: Assemble technical and domain experts",
        "Start with pilot project: Test on small, high-impact use case",
        "Measure ROI continuously: Track metrics against baseline",
        "Scale successful patterns: Expand proven solutions organization-wide",
        "Address ethical considerations: Implement responsible AI guidelines"
    ]

    # Build the prompt
    prompt = infographic_service.build_prompt_from_keypoints(
        title=title,
        key_points=key_points,
        color_scheme="forest",
        subtitle="A Practical Implementation Guide",
        call_to_action="Download the complete AI implementation checklist"
    )

    print(f"Generated prompt ({len(prompt)} characters)")
    print(f"First 500 chars:\n{prompt[:500]}...")

    # If you want to generate the image:
    # result = infographic_service.image_generator.generate(prompt)


def example_3_dual_perspective():
    """Example 3: Generate both CTO and CEO perspectives"""
    print("\n" + "="*60)
    print("Example 3: Dual Perspective Generation")
    print("="*60)

    industry_context = """
    SaaS companies are increasingly adopting microservices architecture
    to improve scalability and developer productivity.
    """

    results = infographic_service.generate_dual_perspective(
        content=industry_context,
        job_title="cto",  # Target CTOs as the audience
        framework="how-to"
    )

    for perspective, result in results.items():
        status = "SUCCESS" if result.success else "FAILED"
        print(f"\n{perspective.upper()}: {status}")
        if result.success:
            print(f"  Topic: {result.topic}")
            print(f"  URL: {result.image_url}")


def example_4_validation():
    """Example 4: Validate a prompt before generation"""
    print("\n" + "="*60)
    print("Example 4: Prompt Validation")
    print("="*60)

    # Build a prompt
    prompt = infographic_service.build_prompt_from_keypoints(
        title="Sample Topic",
        key_points=[
            "Point 1: First important thing",
            "Point 2: Second important thing",
            "Point 3: Third important thing"
        ]
    )

    # Validate it
    validation = infographic_service.validate_only(
        prompt=prompt,
        expected_module_count=3
    )

    print(f"Validation passed: {validation.passed}")
    print(f"Score: {validation.score:.2f}")
    print(f"Detected sequences: {validation.detected_sequences}")

    if validation.issues:
        print("\nIssues found:")
        for issue in validation.issues:
            print(f"  - [{issue['severity']}] {issue['message']}")

    if validation.warnings:
        print("\nWarnings:")
        for warning in validation.warnings:
            print(f"  - {warning['message']}")


def example_5_color_schemes():
    """Example 5: Explore available color schemes"""
    print("\n" + "="*60)
    print("Example 5: Available Color Schemes")
    print("="*60)

    schemes = infographic_service.get_color_schemes()
    print(f"Available schemes: {schemes}")

    for scheme_name in schemes:
        prompt = infographic_service.build_prompt_from_keypoints(
            title=f"Sample with {scheme_name} colors",
            key_points=["Point 1", "Point 2", "Point 3"],
            color_scheme=scheme_name
        )
        print(f"{scheme_name}: prompt built ({len(prompt)} chars)")


def example_6_from_url():
    """Example 6: Generate from a web URL"""
    print("\n" + "="*60)
    print("Example 6: Generation from URL")
    print("="*60)

    # URL to industry article or blog post
    url = "https://example.com/industry-trends"

    # Note: This will fail with a real URL without internet access
    # Uncomment to test with a real URL:
    # result = infographic_service.generate_from_url(
    #     url=url,
    #     job_title="product_manager",
    #     perspective="cto"
    # )
    # print(f"Result: {result.success}")


def example_7_quick_function():
    """Example 7: Using the quick access function"""
    print("\n" + "="*60)
    print("Example 7: Quick Access Function")
    print("="*60)

    result = generate_infographic(
        content="Cloud computing trends for enterprise",
        job_title="ceo",
        perspective="ceo",
        color_scheme="ocean"
    )

    if result.success:
        print(f"Generated: {result.topic}")
    else:
        print(f"Failed: {result.error}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("INFOGRAPHIC SERVICE USAGE EXAMPLES")
    print("="*60)

    # Run examples
    example_1_basic_generation()
    example_2_custom_keypoints()
    example_3_dual_perspective()
    example_4_validation()
    example_5_color_schemes()
    # example_6_from_url()  # Requires internet
    example_7_quick_function()

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
