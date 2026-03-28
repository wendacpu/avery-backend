"""
Input Processor Module
Multi-source input processing for the infographic generation system.

Handles: Text, PDF, and Web content → Unified structured background
"""
import logging
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import httpx

logger = logging.getLogger(__name__)


class InputType(Enum):
    """Input source types"""
    TEXT = "text"
    PDF = "pdf"
    URL = "url"
    FILE = "file"


@dataclass
class ProcessedInput:
    """Unified structured background data"""
    raw_content: str
    title: str
    industry: str = ""
    key_themes: List[str] = field(default_factory=list)
    target_audience: str = ""
    extracted_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "raw_content": self.raw_content,
            "title": self.title,
            "industry": self.industry,
            "key_themes": self.key_themes,
            "target_audience": self.target_audience,
            "extracted_data": self.extracted_data
        }


class InputProcessor:
    """
    Multi-source input processor

    Converts various input sources (text, PDF, web) into
    unified structured background information.

    Key Principle: Client files = industry background, NOT content source
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize input processor

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        logger.info("InputProcessor initialized")

    def process(
        self,
        input_data: Union[str, Dict[str, Any], Path],
        input_type: Optional[InputType] = None
    ) -> ProcessedInput:
        """
        Process input data into structured format

        Args:
            input_data: Raw input (text string, dict, file path, or URL)
            input_type: Type of input (auto-detected if None)

        Returns:
            ProcessedInput with structured data
        """
        # Auto-detect input type if not specified
        if input_type is None:
            input_type = self._detect_input_type(input_data)

        logger.info(f"Processing input as {input_type.value}")

        # Route to appropriate processor
        if input_type == InputType.TEXT:
            return self._process_text(input_data)
        elif input_type == InputType.URL:
            return self._process_url(input_data)
        elif input_type == InputType.PDF:
            return self._process_pdf(input_data)
        elif input_type == InputType.FILE:
            return self._process_file(input_data)
        else:
            raise ValueError(f"Unsupported input type: {input_type}")

    def _detect_input_type(self, input_data: Any) -> InputType:
        """Auto-detect input type from data"""
        if isinstance(input_data, str):
            if input_data.startswith(("http://", "https://")):
                return InputType.URL
            if len(input_data) > 100:  # Likely raw text content
                return InputType.TEXT
            return InputType.TEXT
        elif isinstance(input_data, Path) or isinstance(input_data, str):
            str_path = str(input_data)
            if str_path.endswith(".pdf"):
                return InputType.PDF
            return InputType.FILE
        elif isinstance(input_data, dict):
            # Extract content from dict
            if "url" in input_data:
                return InputType.URL
            if "content" in input_data or "text" in input_data:
                return InputType.TEXT
        return InputType.TEXT

    def _process_text(self, text: str) -> ProcessedInput:
        """Process raw text input"""
        # Clean and normalize text
        cleaned = self._clean_text(text)

        # Extract metadata
        title = self._extract_title(cleaned)
        key_themes = self._extract_themes(cleaned)

        return ProcessedInput(
            raw_content=cleaned,
            title=title,
            key_themes=key_themes
        )

    def _process_url(self, url: str) -> ProcessedInput:
        """Process web URL content"""
        try:
            response = self.client.get(url)
            response.raise_for_status()

            # Extract text content from HTML
            from html.parser import HTMLParser

            class TextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text_parts = []
                    self.in_script = False

                def handle_starttag(self, tag, attrs):
                    if tag in ["script", "style", "nav", "footer"]:
                        self.in_script = True

                def handle_endtag(self, tag):
                    if tag in ["script", "style", "nav", "footer"]:
                        self.in_script = False

                def handle_data(self, data):
                    if not self.in_script:
                        stripped = data.strip()
                        if stripped and len(stripped) > 3:
                            self.text_parts.append(stripped)

            parser = TextExtractor()
            parser.feed(response.text)

            # Join and clean extracted text
            raw_text = " ".join(parser.text_parts)
            cleaned = self._clean_text(raw_text)

            # Extract title from URL or content
            title = self._extract_title(cleaned)
            if not title:
                title = url.split("/")[-1].replace("-", " ").title()

            return ProcessedInput(
                raw_content=cleaned,
                title=title
            )

        except Exception as e:
            logger.error(f"Failed to process URL {url}: {e}")
            raise

    def _process_pdf(self, pdf_path: Union[str, Path]) -> ProcessedInput:
        """Process PDF file content"""
        try:
            # Try to import PDF processing libraries
            try:
                import PyPDF2
            except ImportError:
                logger.warning("PyPDF2 not installed, using basic extraction")
                return self._process_file(pdf_path)

            path = Path(pdf_path)
            text_parts = []

            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

            raw_text = "\n".join(text_parts)
            cleaned = self._clean_text(raw_text)

            return ProcessedInput(
                raw_content=cleaned,
                title=self._extract_title(cleaned) or path.stem
            )

        except Exception as e:
            logger.error(f"Failed to process PDF {pdf_path}: {e}")
            raise

    def _process_file(self, file_path: Union[str, Path]) -> ProcessedInput:
        """Process generic text file"""
        path = Path(file_path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            return self._process_text(content)

        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(path, "r", encoding="latin-1") as f:
                    content = f.read()
                return self._process_text(content)
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")
                raise

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters that might cause issues
        text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]", "", text)

        # Normalize line breaks
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _extract_title(self, text: str) -> str:
        """Extract title from text"""
        lines = text.split("\n")

        # Look for markdown headers or title-like lines
        for line in lines[:5]:
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("#").strip()
            if 10 < len(line) < 80:
                return line

        return ""

    def _extract_themes(self, text: str) -> List[str]:
        """Extract key themes/topics from text"""
        # Simple keyword-based extraction
        themes = []

        # Common business/tech themes
        theme_patterns = [
            r"\b(AI|artificial intelligence|machine learning)\b",
            r"\b(SaaS|B2B|B2C)\b",
            r"\b(product|development|engineering)\b",
            r"\b(marketing|sales|revenue)\b",
            r"\b(growth|strategy|leadership)\b",
            r"\b(data|analytics|insights)\b",
            r"\b(customer|user|experience)\b",
            r"\b(operations|efficiency|automation)\b",
        ]

        text_lower = text.lower()
        for pattern in theme_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                theme = match.lower()
                if theme not in themes:
                    themes.append(theme)

        return themes[:5]  # Return top 5 themes

    def close(self):
        """Close HTTP client"""
        if self.client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Global instance
_input_processor_instance: Optional[InputProcessor] = None


def get_input_processor() -> InputProcessor:
    """Get singleton input processor instance"""
    global _input_processor_instance
    if _input_processor_instance is None:
        _input_processor_instance = InputProcessor()
    return _input_processor_instance
