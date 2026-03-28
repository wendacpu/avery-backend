"""
Prompt Builder Module
Builds 9-section structured prompts for AI image generation.

CRITICAL: This module implements the 9-section prompt structure that ensures
consistent, high-quality infographic generation with proper sequence numbering.

DESIGN SPECIFICATION INTEGRATION:
- Automatically applies design rules (3-5 sections, 14px min font, max 4 colors)
- Generates unique layouts per request (no template repetition)
- Intelligent chart type selection based on data characteristics
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ColorScheme(Enum):
    """Predefined color schemes (max 4 colors per design)"""
    FOREST = {
        "primary": "#2D5A3D",
        "secondary": "#C9A65C",
        "background": "#F7F4EF",
        "accent": "#E6F4EA",
        "accent_2": "#FFF2CC",
        "accent_3": "#FFE6E6",
        "accent_4": "#E6F7FA"
    }
    OCEAN = {
        "primary": "#1E4A6B",
        "secondary": "#D4A574",
        "background": "#F0F4F8",
        "accent": "#E6F2FA",
        "accent_2": "#FFF9E6",
        "accent_3": "#FCE6E6",
        "accent_4": "#F0F9FF"
    }
    MINIMAL = {
        "primary": "#1F2937",
        "secondary": "#6B7280",
        "background": "#FFFFFF",
        "accent": "#F3F4F6",
        "accent_2": "#E5E7EB",
        "accent_3": "#F9FAFB",
        "accent_4": "#F3F4F6"
    }


@dataclass
class ContentModule:
    """Individual content module for the infographic"""
    number: int  # Sequence number (CRITICAL for validation)
    title: str
    content: str
    background_color: str  # Rotating accent colors


@dataclass
class InfographicSpec:
    """Complete infographic specification"""
    title: str
    subtitle: str
    modules: List[ContentModule]
    color_scheme: ColorScheme
    call_to_action: str = ""
    total_modules: int = 0
    research_data: Optional[Dict[str, Any]] = None
    design_specification: Optional[Any] = None  # DesignSpecification from design_specification.py

    def __post_init__(self):
        self.total_modules = len(self.modules)


class PromptBuilder:
    """
    9-Section Prompt Builder

    Builds structured prompts following the 9-section format:
    1. CRITICAL - Core requirements and constraints
    2. LAYOUT - Grid structure and spacing
    3. COLOR - Color palette and usage rules
    4. TYPOGRAPHY - Font hierarchy and sizing
    5. VISUAL - Icons and decorative elements
    6. CONTENT - Actual content to display
    7. CHART - Data visualization specs
    8. EMPHASIS - Highlight rules for key numbers
    9. CHECKLIST - Final validation checklist

    CRITICAL: Ensures proper sequence numbering for validation
    """

    # Module background colors (pure white for premium business style)
    MODULE_COLORS = [
        "white (#FFFFFF)",
        "white (#FFFFFF)",
        "white (#FFFFFF)",
        "white (#FFFFFF)"
    ]

    def __init__(self):
        """Initialize prompt builder"""
        logger.info("PromptBuilder initialized")

    def build(
        self,
        spec: InfographicSpec,
        quality_level: str = "high"
    ) -> str:
        """
        Build complete 9-section prompt

        Args:
            spec: InfographicSpec with all content
            quality_level: Quality level (high/medium/low)

        Returns:
            Complete structured prompt string
        """
        sections = []

        # 1. CRITICAL - Core requirements
        sections.append(self._build_critical_section(spec, quality_level))

        # 2. LAYOUT - Grid structure
        sections.append(self._build_layout_section(spec))

        # 3. COLOR - Color palette
        sections.append(self._build_color_section(spec))

        # 4. TYPOGRAPHY - Font hierarchy
        sections.append(self._build_typography_section())

        # 5. VISUAL - Icons and elements
        sections.append(self._build_visual_section())

        # 6. CONTENT - Actual content (CRITICAL: with sequence numbers)
        sections.append(self._build_content_section(spec))

        # 7. CHART - Data visualization
        sections.append(self._build_chart_section(spec))

        # 8. EMPHASIS - Highlight rules
        sections.append(self._build_emphasis_section())

        # 9. CHECKLIST - Validation checklist
        sections.append(self._build_checklist_section(spec))

        # Combine all sections
        full_prompt = "\n\n".join(sections)

        logger.info(f"Built prompt with {len(spec.modules)} content modules")
        return full_prompt

    def _build_critical_section(self, spec: InfographicSpec, quality_level: str) -> str:
        """Section 1: CRITICAL requirements"""
        return f"""**1. CRITICAL REQUIREMENTS**

TASK: Create a professional infographic for LinkedIn
TITLE: {spec.title}
QUALITY: {quality_level.upper()} quality - professional grade
FORMAT: Vertical aspect ratio (3:4) - optimized for LinkedIn feed

MANDATORY RULES:
- ALL TEXT IN ENGLISH ONLY
- High information density - no wasted space
- Clean business style - no decorative elements
- Each numbered module must appear EXACTLY ONCE
- Sequence numbers (1, 2, 3...) must be clearly visible
- Maximum 4 colors total in the entire design

CONTENT REQUIREMENTS (CRITICAL):
- Each section MUST have: Title + Detailed Body Content (3-5 lines or multiple bullet points)
- Focus on "HOW-TO" actionable steps, NOT "why" explanations
- Provide specific, implementable guidance in each section
- Ensure factual accuracy - no logical errors or contradictions
- Content must be detailed and substantial, not generic statements"""

    def _build_layout_section(self, spec: InfographicSpec) -> str:
        """Section 2: LAYOUT structure (Strategic Professional Architecture)"""
        return f"""**2. LAYOUT STRUCTURE: STRATEGIC PROFESSIONAL ARCHITECTURE**

ARCHITECTURAL INTENT: Select the most professional layout based on content characteristics:
- IF STEP-BY-STEP: Use a clear "Waterfall" or "Stage-Gate" vertical flow (like a Capability Ladder).
- IF COMPARISON: Use a "Dual-Pane" or "A/B" split layout.
- IF COMPONENTS: Use a "Central-Hub" or "Core-Architecture" diagram (like Memory Architecture).
- IF HIERARCHY: Use a "Pyramid" or "Layered" stack.

MANDATORY LAYOUT RULES:
- High Information Density: Maximize canvas usage (aspect ratio 3:4).
- Clear Visual Hierarchy: Establish a clear "Entry Point" for the eye.
- Primary Visual Anchor: One high-impact Master Data Visualization must be integrated.
- Professional Spacing: 24-32px margins between all major logical blocks.
- Clean Borders: Use 1px sharp borders or solid color blocks for structure.
"""

    def _build_color_section(self, spec: InfographicSpec) -> str:
        """Section 3: COLOR palette"""
        colors = spec.color_scheme.value
        return f"""**3. COLOR PALETTE (Maximum 4 colors)**

PRIMARY COLOR: {colors['primary']}
- Usage: Main title, key headings
- Purpose: Establish visual hierarchy

SECONDARY COLOR: {colors['secondary']}
- Usage: Subtitles, tags, labels
- Purpose: Secondary emphasis

BACKGROUND COLOR: {colors['background']}
- Usage: Canvas background
- Purpose: Clean base layer

ACCENT COLORS (for module elements - use sparingly):
- Accent 1: {colors['primary']} (Module numbers, primary emphasis)
- Accent 2: {colors['secondary']} (Secondary icons, labels)
- Background: {colors['background']} (Card surface - MUST be pure white #FFFFFF)

TEXT COLOR: Dark charcoal (#1F2328) - maximum legibility

COLOR RULES:
- Use ONLY colors listed above
- Maximum 4 distinct colors in final design
- High contrast for readability"""

    def _build_typography_section(self) -> str:
        """Section 4: TYPOGRAPHY hierarchy"""
        return """**4. TYPOGRAPHY HIERARCHY**

FONT SIZES:
- Main Title: 48-56px, Extra Bold, Primary Color
- Subtitle: 24-28px, Bold, Text Color
- Module Numbers: 32-40px, Extra Bold, Accent Color (in circles)
- Module Titles: 20-24px, Bold, Accent Colors
- Body Text: 14px, Regular, Text Color (FIXED SIZE - no exceptions)
- Footer/CTA: 14-16px, Medium, Secondary Color

FONT FAMILY:
- Primary: Inter, Roboto, or Arial (clean sans-serif)
- Fallback: System sans-serif fonts

ALIGNMENT:
- Titles: Left-aligned (natural reading flow)
- Body text: Left-aligned
- Module numbers: In colored circles, left of content
- Numbers: Right-aligned for comparison

CRITICAL RULES:
- Body text MUST be 14px - no larger, no smaller
- DO NOT display font sizes, layout specs, or design instructions in the image
- NO text like "14px", "bold", "padding", "margin" should appear in final image
- Keep only the actual content, no technical specifications"""

    def _build_visual_section(self) -> str:
        """Section 5: VISUAL elements"""
        return """**5. VISUAL ELEMENTS**

ICONS:
- Simple outline style
- Consistent sizing (24-32px)
- Contextual to each module content
- Minimal detail - clean and professional

MODULE NUMBERING:
- Large circle (40-48px diameter)
- Accent color background
- White or dark text number
- Positioned at top-left of each module
- MUST be clearly visible

CHART PLACEMENT (CRITICAL):
- Charts MUST be positioned to avoid overlapping with text content
- Maintain minimum 20px spacing between charts and text
- Use separate zones within modules: text in one area, chart in another
- NEVER overlay charts directly on body text
- Ensure all text remains fully readable and unobstructed

DECORATIVE ELEMENTS:
- Thin divider lines (1-2px)
- Dashed separators for grouping
- Subtle geometric shapes ONLY if functional
- NO decorative flourishes or ornaments

ILLUSTRATIONS:
- One small illustration per module maximum
- Relevant to module content
- Simple, flat style
- Consistent visual language"""

    def _build_content_section(self, spec: InfographicSpec) -> str:
        """Section 6: ACTUAL CONTENT (Master Accuracy & Precision)"""
        lines = [
            "**6. ACTUAL CONTENT TO DISPLAY**",
            "",
            "CORE REQUIREMENTS:",
            "- ACCURACY (CRITICAL): Double-check all spellings and numeric values. No typos permitted.",
            "- NUMBERING: Each card/step MUST have a prominent unique number circles (1, 2, 3...).",
            "- LANGUAGE: English only. Professional business terminology.",
            "",
            "HEADER ZONE:",
            f"Title: {spec.title}",
            f"Subtitle: {spec.subtitle}",
            "**STRATEGIC INSIGHT LINE (BIG TEXT):** Create a powerful summary line (e.g., 'Targeting 847% Growth' or '58% Stuck at Inefficiency').",
            "",
            f"CONTENT MODULES ({len(spec.modules)} TOTAL):"
        ]

        for module in spec.modules:
            lines.append(
                f"- CARD {module.number}: "
                f"Title: {module.title} | "
                f"Content: {module.content}"
            )

        # SELECT ONE MASTER CHART BASED ON RESEARCH
        lines.append("")
        if spec.research_data and spec.research_data.get("charts"):
            chart = spec.research_data["charts"][0]
            lines.extend([
                "**MASTER DATA VISUALIZATION (RIGHT OR BOTTOM POSITIONED):**",
                f"CHART TYPE: {chart.chart_type.upper()} CHART",
                f"CHART TITLE: {chart.title}",
                f"CHART DATA: Using actual industry points to ensure precision and trust."
            ])
        
        lines.extend([
            "",
            "FOOTER ZONE:",
            "- SUCCESS FACTORS: List 3 actionable key terms.",
            "- **THE BENCHMARK (BIG NUM):** One terminal target metric.",
            "  (e.g., '18 Month Horizon' or 'ROI: 3.2x')"
        ])

        return "\n".join(lines)

    def _build_chart_section(self, spec: InfographicSpec) -> str:
        """Section 7: CHART visualization"""
        # Use design specification chart recommendations if available
        if spec.design_specification and spec.design_specification.chart_recommendations:
            chart_section = "**7. DATA VISUALIZATION**\n\n"
            chart_section += "Include the following chart types based on data characteristics:\n\n"

            chart_type_descriptions = {
                "bar": "BAR CHART - Use for comparisons between categories",
                "line": "LINE CHART - Use for trends over time or progressions",
                "pie": "PIE CHART - Use for distributions or part-to-whole relationships"
            }

            for i, chart_type in enumerate(spec.design_specification.chart_recommendations, 1):
                chart_section += f"Chart {i}: {chart_type_descriptions.get(chart_type.value, chart_type.value.upper())}\n"

            # Add integration guidance
            chart_section += "\nChart Integration Rules:\n"
            chart_section += "- Place charts strategically within content modules\n"
            chart_section += "- Use research data from industry analysis\n"
            chart_section += "- Ensure chart colors match the 4-color palette\n"
            chart_section += "- Keep chart labels readable (minimum 14px)\n"

            return chart_section
        else:
            # Fallback to original behavior
            stats = []
            for module in spec.modules:
                import re
                numbers = re.findall(r'\d+[%。，,]|\d+倍|\d+\+?\s*个?', module.content)
                if numbers:
                    stats.extend(numbers[:2])  # Max 2 stats per module

            chart_section = "**7. DATA VISUALIZATION**\n\n"

            if stats:
                chart_section += "Include the following data visualizations:\n"
                for i, stat in enumerate(stats[:5], 1):
                    chart_section += f"- Chart {i}: Display '{stat}' with appropriate chart type\n"
            else:
                chart_section += "No specific statistics provided. Use generic chart icons if appropriate for content.\n"

            return chart_section

    def _build_emphasis_section(self) -> str:
        """Section 8: EMPHASIS rules for key numbers"""
        return """**8. EMPHASIS RULES**

KEY NUMBERS (32-48px):
- Display key metrics or statistics prominently
- Use bold weight
- Color: Primary or accent color
- Position: Top of relevant module
- Background highlight: Small colored rectangle

HIGHLIGHT TECHNIQUES:
- Bold weight for important terms
- Color accent for key phrases
- Larger size for main statistics ONLY
- Underline for critical takeaways

DO NOT:
- Highlight everything (defeats the purpose)
- Use multiple emphasis techniques together
- Highlight more than 10% of text"""

    def _build_checklist_section(self, spec: InfographicSpec) -> str:
        """Section 9: CHECKLIST for validation"""
        return f"""**9. FINAL VALIDATION CHECKLIST**

Before finalizing, verify:
□ All text is in English
□ Body text is exactly 14px
□ No more than 4 colors used
□ All {len(spec.modules)} modules are present
□ Each module number appears EXACTLY ONCE
□ Numbers are sequential: 1, 2, 3, ... {len(spec.modules)}
□ Title is clear and prominent
□ White space is ~30% of canvas
□ No decorative elements (clean business style)
□ High information density maintained

OUTPUT INSTRUCTION:
Generate this infographic as a clean, professional, business-appropriate design.
All text must be legible and well-organized.
No technical specifications should be visible in the final output."""

    def build_from_topic(
        self,
        topic: str,
        key_points: List[str],
        color_scheme: ColorScheme = ColorScheme.FOREST,
        subtitle: str = "",
        call_to_action: str = "",
        research_data: Optional[Dict[str, Any]] = None,
        design_specification: Optional[Any] = None  # DesignSpecification from design_specification.py
    ) -> str:
        """
        Convenience method: build prompt from simple inputs

        Args:
            topic: Main title
            key_points: List of content points (will become modules)
            color_scheme: Color scheme to use (deprecated, using design_spec engine instead)
            subtitle: Optional subtitle
            call_to_action: Optional CTA text
            research_data: Optional industry research data with statistics and charts

        Returns:
            Complete prompt string
        """
        # Import design specification engine
        from api.services.infographic.design_specification import get_design_specification_engine

        # Analyze data characteristics for intelligent chart selection
        design_engine = get_design_specification_engine()

        # Build content string for analysis
        content_for_analysis = " ".join(key_points)
        data_characteristics = design_engine.analyze_data_characteristics(
            content_for_analysis,
            research_data
        )

        # Generate unique design specification (ensures no template repetition)
        design_spec = design_engine.generate_specification(data_characteristics)

        # Adjust key_points count to match design spec section count
        target_section_count = design_spec.section_count
        adjusted_points = self._adjust_section_count(key_points, target_section_count)

        # Enhance key_points with research data if available
        enhanced_points = self._enhance_with_research(adjusted_points, research_data)

        # Convert key_points to ContentModules
        modules = []
        for i, point in enumerate(enhanced_points, 1):
            # Split point into title/content if it contains a colon
            if ":" in point:
                title, content = point.split(":", 1)
                title = title.strip()
                content = content.strip()
            else:
                # Use first few words as title
                words = point.split()
                title = " ".join(words[:5])
                content = point

            modules.append(ContentModule(
                number=i,
                title=title,
                content=content,
                background_color=self.MODULE_COLORS[(i - 1) % len(self.MODULE_COLORS)]
            ))

        # Convert key_points to ContentModules
        modules = []

        # 确保最终modules数量正好等于design_spec.section_count
        final_section_count = design_spec.section_count
        enhanced_points = self._enhance_with_research(adjusted_points, research_data)

        # 如果增强后的点数仍不足，补充通用点
        while len(enhanced_points) < final_section_count:
            enhanced_points.append(f"Section {len(enhanced_points)+1}: Strategic insight and actionable recommendation")

        # 如果点数过多，截取到目标数量
        enhanced_points = enhanced_points[:final_section_count]

        for i, point in enumerate(enhanced_points, 1):
            # Split point into title/content if it contains a colon
            if ":" in point:
                title, content = point.split(":", 1)
                title = title.strip()
                content = content.strip()
            else:
                # Use first few words as title
                words = point.split()
                title = " ".join(words[:5])
                content = point

            modules.append(ContentModule(
                number=i,
                title=title,
                content=content,
                background_color=self.MODULE_COLORS[(i - 1) % len(self.MODULE_COLORS)]
            ))

        # Build spec with design specification integrated
        spec = InfographicSpec(
            title=topic,
            subtitle=subtitle or "Practical insights and actionable strategies",
            modules=modules,
            color_scheme=color_scheme,
            call_to_action=call_to_action or "Follow for more insights",
            research_data=research_data,
            design_specification=design_spec  # Pass design spec
        )

        return self.build(spec)

    def _adjust_section_count(self, key_points: List[str], target_count: int) -> List[str]:
        """调整key_points数量以匹配目标板块数"""
        current_count = len(key_points)

        if current_count == target_count:
            return key_points
        elif current_count > target_count:
            # 如果太多，截取到目标数量
            return key_points[:target_count]
        else:
            # 如果太少，保持原样（后面会补充）
            return key_points

    def _enhance_with_research(
        self,
        key_points: List[str],
        research_data: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Enhance key points with real industry data"""
        if not research_data:
            return key_points

        enhanced = []

        # Add statistics from research
        statistics = research_data.get("statistics", [])
        charts = research_data.get("charts", [])

        for i, point in enumerate(key_points):
            # Add relevant statistics to content
            if i < len(statistics) and statistics[i]:
                stat = statistics[i]
                enhanced_point = f"{point} | Data: {stat.value} - {stat.context}"
                enhanced.append(enhanced_point)
            else:
                enhanced.append(point)

        # 注意：图表数据不再作为额外的content modules
        # 图表信息在_build_content_section中单独处理
        # 这样可以确保板块数量符合设计规范要求

        return enhanced

    def validate_content_quality(self, key_points: List[str]) -> Dict[str, Any]:
        """
        Validate content quality before generation

        Checks for:
        - Content length (each point should be detailed, 3-5 sentences)
        - "How-to" focus vs "why" explanations
        - Factual/logical error patterns
        - Generic or vague statements

        Returns:
            Dict with validation results
        """
        issues = []
        warnings = []

        for idx, point in enumerate(key_points, 1):
            # Check content length
            word_count = len(point.split())
            if word_count < 15:
                issues.append(f"Point {idx}: Too short ({word_count} words). Should be 3-5 detailed sentences (30+ words).")
            elif word_count < 30:
                warnings.append(f"Point {idx}: Could be more detailed ({word_count} words). Aim for 3-5 sentences.")

            # Check for "why" language patterns
            why_patterns = ["why is", "why should", "importance of", "benefits of", "advantage of"]
            if any(pattern in point.lower() for pattern in why_patterns):
                warnings.append(f"Point {idx}: May focus on 'why' instead of 'how-to'. Consider rephrasing to actionable steps.")

            # Check for generic/vague patterns
            vague_patterns = ["effectively", "efficiently", "successfully", "properly", "appropriate"]
            if any(pattern in point.lower() for pattern in vague_patterns):
                if not any(specific in point.lower() for specific in ["step", "implement", "set up", "create", "build", "use", "configure"]):
                    issues.append(f"Point {idx}: Contains vague terms without specific actionable steps.")

            # Check for logical contradictions
            if "but" in point.lower() and "however" in point.lower():
                issues.append(f"Point {idx}: May contain logical contradictions (both 'but' and 'however').")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_points": len(key_points)
        }


# Global instance
_prompt_builder_instance: Optional[PromptBuilder] = None


def get_prompt_builder() -> PromptBuilder:
    """Get singleton prompt builder instance"""
    global _prompt_builder_instance
    if _prompt_builder_instance is None:
        _prompt_builder_instance = PromptBuilder()
    return _prompt_builder_instance
