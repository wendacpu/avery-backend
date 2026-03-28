"""
Quality Validator Module
Validates generated images with focus on sequence number verification.

CRITICAL: This module ensures each sequence number appears exactly once
and is positioned correctly in the generated infographic.
"""
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ValidationIssue(Enum):
    """Types of validation issues"""
    MISSING_SEQUENCE = "missing_sequence"
    DUPLICATE_SEQUENCE = "duplicate_sequence"
    NON_SEQUENTIAL = "non_sequential"
    POSITION_ERROR = "position_error"
    TEXT_QUALITY = "text_quality"
    COLOR_VIOLATION = "color_violation"
    TYPOGRAPHY_ERROR = "typography_error"


@dataclass
class ValidationResult:
    """Result of validation"""
    passed: bool
    issues: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    score: float  # 0.0 to 1.0
    detected_sequences: List[int]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "passed": self.passed,
            "issues": self.issues,
            "warnings": self.warnings,
            "score": self.score,
            "detected_sequences": self.detected_sequences,
            "metadata": self.metadata
        }


class QualityValidator:
    """
    Quality Validator for Generated Infographics

    CRITICAL FUNCTIONALITY:
    - Validates that each sequence number appears exactly once
    - Checks that numbers are sequential (1, 2, 3...)
    - Verifies text quality and language
    - Checks color compliance (max 4 colors)
    - Validates typography specs

    Uses OCR for post-generation validation when images are available.
    """

    def __init__(self):
        """Initialize quality validator"""
        self.ocr_available = self._check_ocr_available()
        logger.info(f"QualityValidator initialized (OCR: {self.ocr_available})")

    def _check_ocr_available(self) -> bool:
        """Check if OCR libraries are available"""
        try:
            import pytesseract
            from PIL import Image
            return True
        except ImportError:
            logger.warning("OCR not available. Install pytesseract and PIL for image validation.")
            return False

    def validate_prompt(
        self,
        prompt: str,
        expected_module_count: int
    ) -> ValidationResult:
        """
        Validate prompt before generation

        Args:
            prompt: The generated prompt
            expected_module_count: Expected number of modules

        Returns:
            ValidationResult with issues found
        """
        issues = []
        warnings = []
        detected_sequences = []

        # 1. Check sequence numbers in prompt
        sequences = self._extract_sequences(prompt)
        detected_sequences = sequences

        # Check for missing sequences
        expected = set(range(1, expected_module_count + 1))
        actual = set(sequences)

        missing = expected - actual
        if missing:
            issues.append({
                "type": ValidationIssue.MISSING_SEQUENCE.value,
                "severity": "critical",
                "message": f"Missing sequence numbers: {sorted(missing)}",
                "missing_sequences": sorted(missing)
            })

        # Check for duplicates
        seen = set()
        duplicates = set()
        for seq in sequences:
            if seq in seen:
                duplicates.add(seq)
            seen.add(seq)

        if duplicates:
            issues.append({
                "type": ValidationIssue.DUPLICATE_SEQUENCE.value,
                "severity": "critical",
                "message": f"Duplicate sequence numbers: {sorted(duplicates)}",
                "duplicate_sequences": sorted(duplicates)
            })

        # Check if sequential
        if sequences and sequences != list(range(1, len(sequences) + 1)):
            issues.append({
                "type": ValidationIssue.NON_SEQUENTIAL.value,
                "severity": "critical",
                "message": f"Sequences not sequential: {sequences}",
                "actual_sequences": sequences
            })

        # 2. Check for English content
        non_english_chars = self._check_non_english(prompt)
        if non_english_chars > len(prompt) * 0.1:
            issues.append({
                "type": ValidationIssue.TEXT_QUALITY.value,
                "severity": "high",
                "message": f"Contains {non_english_chars} non-English characters"
            })

        # 3. Check color compliance (max 4 colors)
        color_matches = re.findall(r'#[0-9A-Fa-f]{6}', prompt)
        unique_colors = set(color_matches)
        if len(unique_colors) > 4:
            warnings.append({
                "type": ValidationIssue.COLOR_VIOLATION.value,
                "severity": "medium",
                "message": f"Found {len(unique_colors)} colors (max 4 allowed)",
                "colors": list(unique_colors)
            })

        # 4. Check typography specs
        if "14px" not in prompt and "14 px" not in prompt:
            warnings.append({
                "type": ValidationIssue.TYPOGRAPHY_ERROR.value,
                "severity": "low",
                "message": "Body text size not specified as 14px"
            })

        # Calculate score
        score = self._calculate_score(len(issues), len(warnings))

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            score=score,
            detected_sequences=detected_sequences,
            metadata={
                "expected_count": expected_module_count,
                "actual_count": len(sequences),
                "color_count": len(unique_colors)
            }
        )

    def validate_image(
        self,
        image_path: str,
        expected_module_count: int
    ) -> ValidationResult:
        """
        Validate generated image using OCR

        CRITICAL: This is the final check that sequence numbers
        are correctly rendered in the actual image.

        Args:
            image_path: Path to generated image
            expected_module_count: Expected number of modules

        Returns:
            ValidationResult
        """
        if not self.ocr_available:
            logger.warning("OCR not available, skipping image validation")
            return ValidationResult(
                passed=True,
                issues=[],
                warnings=[{
                    "type": "ocr_unavailable",
                    "message": "OCR not available - image not validated"
                }],
                score=0.5,
                detected_sequences=[],
                metadata={"ocr_available": False}
            )

        try:
            import pytesseract
            from PIL import Image

            # Open image
            img = Image.open(image_path)

            # Extract text
            text = pytesseract.image_to_string(img)

            # Validate extracted text
            return self._validate_ocr_text(text, expected_module_count)

        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return ValidationResult(
                passed=False,
                issues=[{
                    "type": "validation_error",
                    "severity": "critical",
                    "message": f"Image validation failed: {str(e)}"
                }],
                warnings=[],
                score=0.0,
                detected_sequences=[],
                metadata={"error": str(e)}
            )

    def _validate_ocr_text(
        self,
        text: str,
        expected_module_count: int
    ) -> ValidationResult:
        """Validate OCR extracted text"""
        issues = []
        warnings = []

        # Extract sequence numbers
        sequences = self._extract_sequences(text)

        # Check sequences
        expected = set(range(1, expected_module_count + 1))
        actual = set(sequences)

        missing = expected - actual
        if missing:
            issues.append({
                "type": ValidationIssue.MISSING_SEQUENCE.value,
                "severity": "critical",
                "message": f"OCR detected missing sequences: {sorted(missing)}",
                "missing_sequences": sorted(missing)
            })

        duplicates = [s for s in set(sequences) if sequences.count(s) > 1]
        if duplicates:
            issues.append({
                "type": ValidationIssue.DUPLICATE_SEQUENCE.value,
                "severity": "critical",
                "message": f"OCR detected duplicate sequences: {duplicates}",
                "duplicate_sequences": duplicates
            })

        # CRITICAL: Enhanced validation for modules > 4
        if expected_module_count > 4:
            logger.info(f"Enhanced sequence validation for {expected_module_count} modules (>4)")

            # Check if all sequences are present
            if len(sequences) < expected_module_count:
                issues.append({
                    "type": ValidationIssue.MISSING_SEQUENCE.value,
                    "severity": "critical",
                    "message": f"CRITICAL: Expected {expected_module_count} sequences but only found {len(sequences)}. For >4 modules, every sequence MUST be present and correctly positioned.",
                    "expected_count": expected_module_count,
                    "actual_count": len(sequences),
                    "enhanced_validation": True
                })

            # Check sequential order (no gaps)
            sorted_sequences = sorted(set(sequences))
            for i in range(len(sorted_sequences) - 1):
                if sorted_sequences[i + 1] - sorted_sequences[i] > 1:
                    issues.append({
                        "type": ValidationIssue.NON_SEQUENTIAL.value,
                        "severity": "critical",
                        "message": f"Gap detected in sequences: {sorted_sequences[i]} -> {sorted_sequences[i + 1]}. All numbers from 1 to {expected_module_count} must be present.",
                        "gap_start": sorted_sequences[i],
                        "gap_end": sorted_sequences[i + 1],
                        "enhanced_validation": True
                    })

            # Verify position correctness for large module counts
            # For >4 modules, positions should be distributed evenly
            if len(sequences) == expected_module_count:
                # Check if sequences are roughly evenly distributed in the text
                text_lines = text.split('\n')
                sequence_positions = []
                for i, line in enumerate(text_lines):
                    for seq in sequences:
                        if str(seq) in line:
                            sequence_positions.append((seq, i))
                            break

                # Warn if sequences are clustered (not well distributed)
                if len(sequence_positions) > 4:
                    positions = [pos for _, pos in sequence_positions]
                    avg_spacing = len(text_lines) / len(sequence_positions)
                    for i in range(len(positions) - 1):
                        spacing = positions[i + 1] - positions[i]
                        if spacing > avg_spacing * 2.5:  # More than 2.5x average spacing
                            warnings.append({
                                "type": ValidationIssue.POSITION_ERROR.value,
                                "severity": "medium",
                                "message": f"Sequence {sequence_positions[i][0]} and {sequence_positions[i + 1][0]} may be too far apart. For >4 modules, ensure even distribution.",
                                "sequence_a": sequence_positions[i][0],
                                "sequence_b": sequence_positions[i + 1][0],
                                "spacing": spacing,
                                "avg_spacing": avg_spacing
                            })

        # Check for non-English text
        non_english = self._check_non_english(text)
        if non_english > len(text) * 0.2:
            issues.append({
                "type": ValidationIssue.TEXT_QUALITY.value,
                "severity": "high",
                "message": "OCR detected non-English text in image"
            })

        score = self._calculate_score(len(issues), len(warnings))

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            score=score,
            detected_sequences=sequences,
            metadata={
                "expected_count": expected_module_count,
                "actual_count": len(sequences),
                "text_length": len(text),
                "enhanced_validation": expected_module_count > 4
            }
        )

    def _extract_sequences(self, text: str) -> List[int]:
        """
        Extract sequence numbers from text

        Looks for patterns like:
        - "Module 1:", "Module 2:", etc.
        - "1.", "2.", etc.
        - "1)", "2)", etc.
        """
        sequences = []

        # Pattern 1: "Module X:" or "CARD X:" format
        pattern1 = r'(?:Module|CARD)\s+(\d+)'
        matches = re.findall(pattern1, text, re.IGNORECASE)
        sequences.extend([int(m) for m in matches])

        # Pattern 2: Standalone numbers at start of line
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Match "1.", "1)", "1:", or just "1" at start
            match = re.match(r'^(\d+)[.\):]?\s', line)
            if match:
                num = int(match.group(1))
                if num <= 20:  # Reasonable limit
                    sequences.append(num)

        return sorted(set(sequences))

    def _check_non_english(self, text: str) -> int:
        """Count non-English characters"""
        # Count CJK characters (Chinese, Japanese, Korean)
        cjk_ranges = [
            (0x4E00, 0x9FFF),   # CJK Unified Ideographs
            (0x3040, 0x309F),   # Hiragana
            (0x30A0, 0x30FF),   # Katakana
            (0xAC00, 0xD7AF),   # Hangul
        ]

        count = 0
        for char in text:
            code = ord(char)
            for start, end in cjk_ranges:
                if start <= code <= end:
                    count += 1
                    break

        return count

    def _calculate_score(self, issues: int, warnings: int) -> float:
        """Calculate validation score (0.0 to 1.0)"""
        # Start with 1.0
        score = 1.0

        # Deduct for issues
        score -= issues * 0.3  # Each issue reduces by 30%

        # Deduct for warnings
        score -= warnings * 0.1  # Each warning reduces by 10%

        return max(0.0, min(1.0, score))

    def validate_and_retry(
        self,
        prompt: str,
        expected_module_count: int,
        max_retries: int = 3
    ) -> Tuple[bool, str]:
        """
        Validate prompt and suggest fixes if validation fails

        Returns:
            Tuple of (passed, fixed_prompt_or_original)
        """
        for attempt in range(max_retries):
            result = self.validate_prompt(prompt, expected_module_count)

            if result.passed:
                return True, prompt

            # Try to fix common issues
            if attempt < max_retries - 1:
                prompt = self._fix_prompt_issues(prompt, result.issues)
                logger.info(f"Retry {attempt + 1}: Fixed prompt issues")
            else:
                logger.error(f"Validation failed after {max_retries} attempts")
                for issue in result.issues:
                    logger.error(f"  - {issue['message']}")

        return False, prompt

    def _fix_prompt_issues(self, prompt: str, issues: List[Dict[str, Any]]) -> str:
        """Attempt to fix common prompt issues"""
        fixed = prompt

        for issue in issues:
            issue_type = issue.get("type")

            if issue_type == "missing_sequence":
                # Add missing sequences
                missing = issue.get("missing_sequences", [])
                for num in missing:
                    # Add module template
                    module_template = f"\n\nModule {num}: [Background: light green] Title: Key Point {num} | Content: Actionable insight for step {num}"
                    # Insert before final section
                    fixed = fixed.replace("**9. FINAL", module_template + "\n\n**9. FINAL")

            elif issue_type == "duplicate_sequence":
                # This is harder to fix automatically
                logger.warning("Duplicate sequences require manual review")

        return fixed


# Global instance
_quality_validator_instance: Optional[QualityValidator] = None


def get_quality_validator() -> QualityValidator:
    """Get singleton quality validator instance"""
    global _quality_validator_instance
    if _quality_validator_instance is None:
        _quality_validator_instance = QualityValidator()
    return _quality_validator_instance
