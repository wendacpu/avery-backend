"""
AI 图片生成 Prompt 构建器 - 优化版
提供结构化、高质量的 prompt 构建能力
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LayoutType(Enum):
    """布局类型"""
    MODULAR_GRID = "modular_grid"  # 模块化网格
    VERTICAL_FLOW = "vertical_flow"  # 垂直流
    COMPARISON = "comparison"  # 对比式
    TIMELINE = "timeline"  # 时间线
    CIRCULAR = "circular"  # 圆形布局


class VisualStyle(Enum):
    """视觉风格"""
    MINIMALIST = "minimalist"  # 极简主义
    PROFESSIONAL = "professional"  # 专业商务
    PLAYFUL = "playful"  # 活泼创意
    TECH = "tech"  # 科技感
    ELEGANT = "elegant"  # 优雅精致


@dataclass
class ContentData:
    """结构化内容数据"""
    title: str
    subtitle: str = ""
    key_points: List[str] = None
    statistics: List[str] = None
    examples: List[str] = None
    call_to_action: str = ""

    def __post_init__(self):
        if self.key_points is None:
            self.key_points = []
        if self.statistics is None:
            self.statistics = []
        if self.examples is None:
            self.examples = []


@dataclass
class StyleConfig:
    """风格配置"""
    primary_color: str
    secondary_color: str
    background_color: str
    text_color: str
    accent_colors: List[str] = None
    visual_style: VisualStyle = VisualStyle.PROFESSIONAL

    def __post_init__(self):
        if self.accent_colors is None:
            self.accent_colors = []


class PromptBuilder:
    """Prompt 构建器 - 生成高质量的 AI 图片提示词"""

    def __init__(self):
        """初始化 Prompt 构建器"""
        logger.info("✅ PromptBuilder initialized")

    def build_infographic_prompt(
        self,
        content: ContentData,
        style: StyleConfig,
        layout_type: LayoutType = LayoutType.MODULAR_GRID,
        quality_level: str = "high"
    ) -> str:
        """
        构建信息图生成提示词

        Args:
            content: 结构化内容数据
            style: 风格配置
            layout_type: 布局类型
            quality_level: 质量等级 (high/medium/low)

        Returns:
            结构化的 prompt 字符串
        """
        # 构建 prompt 各部分
        sections = []

        # 1. 基础指令
        sections.append(self._build_base_instruction(content.title, quality_level))

        # 2. 布局规范
        sections.append(self._build_layout_spec(layout_type, content))

        # 3. 色彩方案
        sections.append(self._build_color_palette(style))

        # 4. 排版规范
        sections.append(self._build_typography_spec(style.visual_style))

        # 5. 视觉元素
        sections.append(self._build_visual_elements(style.visual_style))

        # 6. 内容详情
        sections.append(self._build_content_details(content))

        # 7. 风格关键词
        sections.append(self._build_style_keywords(style.visual_style, layout_type))

        # 组合所有部分
        full_prompt = "\n\n".join(sections)

        logger.info(f"📝 Built infographic prompt ({len(full_prompt)} chars)")
        return full_prompt

    def _build_base_instruction(self, title: str, quality_level: str) -> str:
        """构建基础指令"""
        quality_map = {
            "high": "ultra-high quality, professional grade",
            "medium": "good quality, clear and readable",
            "low": "simple design, functional"
        }

        quality_desc = quality_map.get(quality_level, "high quality")

        return f"""**TASK:** Create a professional infographic about "{title}"

**QUALITY:** {quality_desc}
**FORMAT:** Vertical aspect ratio (3:4), suitable for LinkedIn/social media
**REQUIREMENT:** All text must be clear, readable, and professionally arranged"""

    def _build_layout_spec(self, layout_type: LayoutType, content: ContentData) -> str:
        """构建布局规范"""
        layout_specs = {
            LayoutType.MODULAR_GRID: """**LAYOUT STRUCTURE:**
- Tri-zone hierarchy: Header → Content Grid → Footer
- Modular card layout: Information organized in rounded rectangular cards
- Multi-column grid (2-3 columns based on content)
- Consistent spacing between modules (20-30px)
- White space: ~30% of canvas for breathing room""",
            LayoutType.VERTICAL_FLOW: """**LAYOUT STRUCTURE:**
- Vertical flow design: Top-to-bottom narrative
- Progressive disclosure: Information unfolds naturally
- Connected sections: Visual flow indicators (arrows, lines)
- Clear section breaks: Subtle dividers between content blocks
- Generous vertical spacing for readability""",
            LayoutType.COMPARISON: """**LAYOUT STRUCTURE:**
- Side-by-side comparison: Two-column layout
- Central divider: Clear visual separation
- Mirror structure: Parallel information organization
- Comparison indicators: VS, arrows, or checkmarks
- Balanced visual weight between sides""",
            LayoutType.TIMELINE: """**LAYOUT STRUCTURE:**
- Linear timeline: Left-to-right or top-to-bottom progression
- Milestone markers: Clear time-point indicators
- Flow connectors: Arrows or lines showing sequence
- Chronological spacing: Even distribution of time periods
- Era/period labels: Clear time divisions""",
            LayoutType.CIRCULAR: """**LAYOUT STRUCTURE:**
- Central focal point: Main concept in center
- Radial organization: Content arranged around center
- Connected segments: Lines or curves linking related items
- Balanced distribution: Even spacing around circle
- Layered information: Core → Secondary → Tertiary"""
        }

        base_spec = layout_specs.get(layout_type, layout_specs[LayoutType.MODULAR_GRID])

        # 添加内容密度信息
        module_count = len(content.key_points) + len(content.statistics)
        density_note = f"\n- Content density: {module_count} information modules"

        return base_spec + density_note

    def _build_color_palette(self, style: StyleConfig) -> str:
        """构建色彩方案"""
        return f"""**COLOR PALETTE:**
- Background: {style.background_color} (base layer)
- Primary accent: {style.primary_color} (headers, key titles)
- Secondary accent: {style.secondary_color} (subtitles, tags)
- Text: {style.text_color} (main content for readability)
- Additional accents: {', '.join(style.accent_colors[:3])} (module backgrounds, highlights)

**COLOR USAGE:**
- Headers: Primary color, bold weight
- Module backgrounds: Cycle through accent colors (soft pastel tones)
- Text: High contrast for readability (dark on light)
- Call-to-action: Secondary color for visual prominence"""

    def _build_typography_spec(self, visual_style: VisualStyle) -> str:
        """构建排版规范"""
        base_spec = """**TYPOGRAPHY HIERARCHY:**
- Main Title: 48-56px, Extra Bold, Primary Color
- Subtitle: 24-28px, Bold, Text Color
- Section Titles: 20-24px, Bold, Accent Colors
- Body Text: 16-18px, Regular, Text Color
- Labels/Tags: 14px, Bold, Secondary Color
- Footer/CTA: 14-16px, Medium, Secondary Color

**ALIGNMENT:**
- Most text: Left-aligned for natural reading flow
- Titles and headers: Left-aligned or centered (based on design)
- Numerical data: Right-aligned for comparison
- Center alignment: Reserved for single-line emphasis"""

        # 根据风格调整
        style_adjustments = {
            VisualStyle.MINIMALIST: "\n**MINIMALIST TOUCH:** Use generous white space, clean sans-serif fonts (Helvetica, Inter)",
            VisualStyle.PROFESSIONAL: "\n**PROFESSIONAL TOUCH:** Use trusted fonts (Arial, Georgia), maintain formal spacing",
            VisualStyle.PLAYFUL: "\n**PLAYFUL TOUCH:** Use friendly rounded fonts (Poppins, Nunito), varied weights",
            VisualStyle.TECH: "\n**TECH TOUCH:** Use modern tech fonts (Roboto, Mono), precise alignment",
            VisualStyle.ELEGANT: "\n**ELEGANT TOUCH:** Use refined serif fonts (Georgia, Playfair), generous leading"
        }

        return base_spec + style_adjustments.get(visual_style, "")

    def _build_visual_elements(self, visual_style: VisualStyle) -> str:
        """构建视觉元素规范"""
        base_elements = """**VISUAL ELEMENTS:**
- Icons: Simple outline style, consistent sizing (24-32px)
- Decorations: Subtle geometric shapes (circles, lines)
- Dividers: Thin lines or dashed separators
- Background patterns: Minimal texture, low opacity
- Illustrations: Contextual small graphics per module"""

        style_specific = {
            VisualStyle.MINIMALIST: """
**MINIMALIST ELEMENTS:**
- Clean lines, no unnecessary decoration
- Abundant white space
- Simple geometric shapes only
- Flat design, no gradients""",
            VisualStyle.PROFESSIONAL: """
**PROFESSIONAL ELEMENTS:**
- Subtle charts/graphs for data
- Business-appropriate icons
- Clean borders and frames
- Understated decorative accents""",
            VisualStyle.PLAYFUL: """
**PLAYFUL ELEMENTS:**
- Vibrant accent colors
- Rounded corners (8-12px)
- Friendly illustrations
- Dynamic shapes and curves""",
            VisualStyle.TECH: """
**TECH ELEMENTS:**
- Circuit/tech-inspired patterns
- Data visualization elements
- Futuristic iconography
- Grid/matrix backgrounds""",
            VisualStyle.ELEGANT: """
**ELEGANT ELEMENTS:**
- Refined border patterns
- Decorative dividers
- Sophisticated color transitions
- Ornate but subtle accents"""
        }

        return base_elements + style_specific.get(visual_style, "")

    def _build_content_details(self, content: ContentData) -> str:
        """构建内容详情"""
        sections = []

        # 标题区
        sections.append(f"""
**HEADER SECTION:**
- Main Title: {content.title}
- Subtitle: {content.subtitle or "Practical insights and actionable tips"}
- Tagline: {"Professional guidance" if not content.call_to_action else content.call_to_action}""")

        # 内容模块
        if content.key_points:
            sections.append("\n**CONTENT MODULES:**")
            for i, point in enumerate(content.key_points[:8], 1):  # 最多8个要点
                bg_color = ["light green", "pale yellow", "soft pink", "sky blue"][i % 4]
                sections.append(f"Module {i} [Background: {bg_color}]: {point}")

        # 数据统计
        if content.statistics:
            sections.append("\n**DATA HIGHLIGHTS:**")
            for stat in content.statistics[:3]:  # 最多3个数据
                sections.append(f"- Highlight: {stat}")

        # 示例
        if content.examples:
            sections.append("\n**EXAMPLES/ILLUSTRATIONS:**")
            for example in content.examples[:2]:  # 最多2个示例
                sections.append(f"- Example: {example}")

        # 页脚 CTA
        if content.call_to_action:
            sections.append(f"""
**FOOTER/CTA:**
- Call to Action: {content.call_to_action}
- Style: Prominent, visually distinct""")

        return "\n".join(sections)

    def _build_style_keywords(self, visual_style: VisualStyle, layout_type: LayoutType) -> str:
        """构建风格关键词"""
        base_keywords = [
            "professional infographic",
            "clean design",
            "high resolution",
            "vector-style graphics",
            "modern layout",
            "business-appropriate",
            "readable typography",
            "balanced composition"
        ]

        style_keywords = {
            VisualStyle.MINIMALIST: ["minimalist", "clean", "simple", "white space", "clutter-free"],
            VisualStyle.PROFESSIONAL: ["corporate", "business", "formal", "polished", "trustworthy"],
            VisualStyle.PLAYFUL: ["vibrant", "friendly", "dynamic", "colorful", "engaging"],
            VisualStyle.TECH: ["futuristic", "digital", "modern", "innovative", "cutting-edge"],
            VisualStyle.ELEGANT: ["sophisticated", "refined", "premium", "luxurious", "artistic"]
        }

        layout_keywords = {
            LayoutType.MODULAR_GRID: ["grid layout", "modular cards", "organized sections"],
            LayoutType.VERTICAL_FLOW: ["vertical flow", "narrative", "progressive"],
            LayoutType.COMPARISON: ["comparison", "side-by-side", "contrast"],
            LayoutType.TIMELINE: ["timeline", "chronological", "sequential"],
            LayoutType.CIRCULAR: ["radial", "circular", "central focus"]
        }

        # 组合关键词
        all_keywords = base_keywords + style_keywords.get(visual_style, []) + layout_keywords.get(layout_type, [])

        return f"""**STYLE KEYWORDS:**
{', '.join(all_keywords[:15])}

**OUTPUT REQUIREMENT:**
Generate this as a clean, professional infographic with English text only. Ensure all text is legible, well-organized, and free of technical specifications."""


# 便捷函数
def build_enhanced_prompt(
    title: str,
    key_points: List[str],
    primary_color: str = "#2D5A3D",
    secondary_color: str = "#C9A65C",
    background_color: str = "#F7F4EF",
    visual_style: str = "professional"
) -> str:
    """
    快速构建增强版 prompt

    Args:
        title: 信息图标题
        key_points: 关键点列表
        primary_color: 主色调
        secondary_color: 次要色调
        background_color: 背景色
        visual_style: 视觉风格 (minimalist/professional/playful/tech/elegant)

    Returns:
        完整的 prompt 字符串
    """
    builder = PromptBuilder()

    # 构建内容数据
    content = ContentData(
        title=title,
        subtitle="Key insights and takeaways",
        key_points=key_points
    )

    # 构建风格配置
    style = StyleConfig(
        primary_color=primary_color,
        secondary_color=secondary_color,
        background_color=background_color,
        text_color="#1F2328",
        visual_style=VisualStyle(visual_style)
    )

    # 生成 prompt
    return builder.build_infographic_prompt(
        content=content,
        style=style,
        layout_type=LayoutType.MODULAR_GRID
    )


# 使用示例
if __name__ == "__main__":
    # 示例1: 专业商务风格
    prompt1 = build_enhanced_prompt(
        title="10 Productivity Hacks for Remote Work",
        key_points=[
            "Set clear boundaries between work and personal time",
            "Use time-blocking for focused work sessions",
            "Minimize meetings and maximize async communication",
            "Create a dedicated workspace",
            "Take regular breaks to maintain energy",
            "Leverage productivity tools and automation",
            "Prioritize tasks using the Eisenhower Matrix",
            "Maintain regular communication with your team"
        ],
        visual_style="professional"
    )

    print("=== Professional Style Prompt ===")
    print(prompt1[:500] + "...")
    print("\n")

    # 示例2: 科技风格
    prompt2 = build_enhanced_prompt(
        title="AI in Healthcare: 5 Key Applications",
        key_points=[
            "Diagnostic assistance and medical imaging",
            "Drug discovery and development acceleration",
            "Personalized treatment recommendations",
            "Remote patient monitoring and predictive analytics",
            "Administrative workflow automation"
        ],
        visual_style="tech"
    )

    print("=== Tech Style Prompt ===")
    print(prompt2[:500] + "...")
