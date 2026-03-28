"""
Design Specification Module
固化infographic设计规范，确保每次生成符合商务标准且不重复

设计原则（基于第一性原理分析）：
1. 3-5个板块 - 认知负荷理论：工作记忆容量7±2，3-5个最优平衡信息密度和可读性
2. 14px最小字号 - 视觉科学：低于14px在标准屏幕上可读性下降20%
3. 最多4种颜色 - 色彩理论：超过4种增加认知负荷，降低专业感
4. 5种布局 - 视觉流变：避免单调，保持注意力，适应不同内容类型
5. 智能图表选择 - 数据可视化最佳实践：根据数据类型自动选择最优图表
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import random

logger = logging.getLogger(__name__)


class LayoutType(Enum):
    """4种布局类型 - 避免重复"""
    LEFT_TEXT_RIGHT_IMAGE = "left-text-right-image"  # 左文右图
    LEFT_IMAGE_RIGHT_TEXT = "left-image-right-text"  # 左图右文
    TOP_TEXT_BOTTOM_IMAGE = "top-text-bottom-image"  # 上文下图
    VERTICAL_FLOW = "vertical-flow"                   # 垂直流向（经典）


class ChartType(Enum):
    """图表类型 - 根据数据特性智能选择"""
    BAR = "bar"           # 柱状图 - 用于对比
    LINE = "line"         # 折线图 - 用于趋势
    PIE = "pie"           # 饼状图 - 用于分布/占比
    NONE = "none"         # 无图表 - 纯文字内容


@dataclass
class ColorPalette:
    """商务风配色方案 - 最多4种颜色"""
    primary: str      # 主色 - 用于标题、重点
    secondary: str    # 辅色 - 用于副标题、标签
    background: str   # 背景色 - 用于画布
    accent: str       # 强调色 - 用于图表、高亮

    def to_list(self) -> List[str]:
        """转换为颜色列表"""
        return [self.primary, self.secondary, self.background, self.accent]


@dataclass
class TypographySpec:
    """字体规范 - 确保可读性"""
    title_min_size: int = 48       # 主标题最小字号
    subtitle_min_size: int = 24    # 副标题最小字号
    body_min_size: int = 14        # 正文字号（硬性要求，不小于14px）
    caption_min_size: int = 12     # 说明文字号

    font_family: str = "Inter, Roboto, Arial, sans-serif"


@dataclass
class LayoutConstraints:
    """布局约束"""
    min_sections: int = 3    # 最少3个板块
    max_sections: int = 5    # 最多5个板块
    preferred_sections: int = 4  # 偏好4个板块


@dataclass
class DesignSpecification:
    """完整设计规范"""
    layout_type: LayoutType
    color_palette: ColorPalette
    typography: TypographySpec
    layout_constraints: LayoutConstraints
    section_count: int
    chart_recommendations: List[ChartType] = field(default_factory=list)

    def to_prompt_section(self) -> str:
        """转换为prompt中的设计规范部分"""
        return f"""
**2. LAYOUT STRUCTURE**
Layout Pattern: {self.layout_type.value}
Sections: {self.section_count} (strictly between {self.layout_constraints.min_sections}-{self.layout_constraints.max_sections})

Layout Description:
{self._get_layout_description()}

**3. COLOR PALETTE (Maximum 4 colors)**
Primary: {self.color_palette.primary} - Titles, headings
Secondary: {self.color_palette.secondary} - Subtitles, labels
Background: {self.color_palette.background} - Canvas
Accent: {self.color_palette.accent} - Charts, highlights
Text: Dark charcoal (#1F2328) - Maximum legibility

COLOR RULES:
- Use ONLY these 4 colors
- High contrast for readability
- No additional colors

**4. TYPOGRAPHY**
Font Family: {self.typography.font_family}
Title: {self.typography.title_min_size}px, Bold, Primary Color
Subtitle: {self.typography.subtitle_min_size}px, Bold, Secondary Color
Body Text: {self.typography.body_min_size}px, Regular, Text Color (MINIMUM - NO EXCEPTIONS)
Caption: {self.typography.caption_min_size}px, Regular, Text Color

CRITICAL: Body text MUST be exactly {self.typography.body_min_size}px - no smaller
"""

    def _get_layout_description(self) -> str:
        """获取布局描述"""
        descriptions = {
            LayoutType.LEFT_TEXT_RIGHT_IMAGE: "Left side: Text content (60%), Right side: Visual/Chart (40%). Use for analytical content.",
            LayoutType.LEFT_IMAGE_RIGHT_TEXT: "Left side: Visual/Chart (40%), Right side: Text content (60%). Use for visual-first explanations.",
            LayoutType.TOP_TEXT_BOTTOM_IMAGE: "Top: Text introduction (30%), Bottom: Main content with visual (70%). Use for storytelling flow.",
            LayoutType.VERTICAL_FLOW: "Classic vertical flow: Top to bottom, alternating text and visuals. Use for step-by-step processes."
        }
        return descriptions.get(self.layout_type, "Vertical flow layout")


class DesignSpecificationEngine:
    """
    设计规范引擎

    功能：
    1. 管理设计规范库
    2. 生成多样化设计（避免重复）
    3. 智能图表类型推荐
    4. 板块数量控制
    """

    def __init__(self):
        """初始化设计规范引擎"""
        self.recent_layouts = []  # 记录最近使用的布局（避免重复）
        self.max_history = 10      # 最多记录10次

        # 商务风配色方案库（蓝白/绿白/紫白风格）
        self.color_palettes = [
            # 蓝白风格
            ColorPalette(
                primary="#1E4A6B",      # 深蓝
                secondary="#6B9ABD",    # 中蓝
                background="#FFFFFF",   # 纯白
                accent="#E6F2FA"        # 浅蓝
            ),
            ColorPalette(
                primary="#2C5282",      # 海军蓝
                secondary="#4299E1",    # 亮蓝
                background="#F7FAFC",   # 灰白
                accent="#EBF8FF"        # 浅蓝白
            ),
            # 绿白风格
            ColorPalette(
                primary="#2D5A3D",      # 深绿
                secondary="#68D391",    # 亮绿
                background="#FFFFFF",   # 纯白
                accent="#E6FFED"        # 浅绿
            ),
            ColorPalette(
                primary="#276749",      # 森林绿
                secondary="#48BB78",    # 中绿
                background="#F0FFF4",   # 淡绿白
                accent="#C6F6D5"        # 浅绿白
            ),
            # 紫白风格
            ColorPalette(
                primary="#553C9A",      # 深紫
                secondary="#9F7AEA",    # 亮紫
                background="#FFFFFF",   # 纯白
                accent="#E9D8FD"        # 浅紫
            ),
            ColorPalette(
                primary="#6B46C1",      # 紫罗兰
                secondary="#8B5CF6",    # 亮紫罗兰
                background="#FAF5FF",   # 淡紫白
                accent="#E9D8FD"        # 浅紫白
            )
        ]

        logger.info("DesignSpecificationEngine initialized")

    def generate_specification(
        self,
        data_characteristics: Optional[Dict[str, Any]] = None
    ) -> DesignSpecification:
        """
        生成设计规范

        Args:
            data_characteristics: 数据特性（用于图表推荐）
                - has_time_series: 是否有时间序列数据（推荐折线图）
                - has_comparison: 是否有对比数据（推荐柱状图）
                - has_distribution: 是否有分布数据（推荐饼图）

        Returns:
            DesignSpecification: 完整设计规范
        """
        # 1. 选择布局（避免最近使用的）
        layout_type = self._select_unique_layout()

        # 2. 选择配色方案（纯白背景100%优先）
        # 优先选择background="#FFFFFF"的配色方案
        white_background_palettes = [p for p in self.color_palettes if p.background == "#FFFFFF"]

        if white_background_palettes:
            # 80%概率使用纯白背景，20%使用其他（避免过度单调）
            if random.random() < 0.8:
                color_palette = random.choice(white_background_palettes)
            else:
                non_white_palettes = [p for p in self.color_palettes if p.background != "#FFFFFF"]
                color_palette = random.choice(non_white_palettes) if non_white_palettes else random.choice(white_background_palettes)
        else:
            color_palette = random.choice(self.color_palettes)

        # 3. 字体规范（固定）
        typography = TypographySpec()

        # 4. 确定板块数量（3-5个，偏好4个）
        section_count = self._determine_section_count()

        # 5. 布局约束
        layout_constraints = LayoutConstraints()

        # 6. 智能图表推荐
        chart_recommendations = self._recommend_charts(
            data_characteristics or {},
            section_count
        )

        spec = DesignSpecification(
            layout_type=layout_type,
            color_palette=color_palette,
            typography=typography,
            layout_constraints=layout_constraints,
            section_count=section_count,
            chart_recommendations=chart_recommendations
        )

        # 记录此次使用的布局
        self._record_layout(layout_type)

        logger.info(f"Generated spec: layout={layout_type.value}, sections={section_count}, charts={chart_recommendations}")

        return spec

    def _select_unique_layout(self) -> LayoutType:
        """选择布局（避免重复）"""
        available = [l for l in LayoutType if l not in self.recent_layouts]

        if not available:
            # 如果所有布局都最近用过，清空历史重新开始
            self.recent_layouts = []
            available = list(LayoutType)

        return random.choice(available)

    def _determine_section_count(self) -> int:
        """确定板块数量（3-5个，偏好4个）"""
        # 70%概率使用4个板块，15%使用3个，15%使用5个
        rand = random.random()
        if rand < 0.7:
            return 4
        elif rand < 0.85:
            return 3
        else:
            return 5

    def _recommend_charts(
        self,
        data_characteristics: Dict[str, Any],
        section_count: int
    ) -> List[ChartType]:
        """
        智能推荐图表类型

        规则：
        - has_time_series (时间趋势) → 折线图
        - has_comparison (对比数据) → 柱状图
        - has_distribution (分布/占比) → 饼图
        """
        recommendations = []

        # 基于数据特性推荐
        if data_characteristics.get("has_time_series"):
            recommendations.append(ChartType.LINE)

        if data_characteristics.get("has_comparison"):
            recommendations.append(ChartType.BAR)

        if data_characteristics.get("has_distribution"):
            recommendations.append(ChartType.PIE)

        # 如果没有明确的数据特性，随机推荐1-2种
        if not recommendations:
            recommendations = random.sample([
                ChartType.BAR, ChartType.LINE, ChartType.PIE
            ], k=random.randint(1, 2))

        # 限制图表数量，不超过板块数量的一半
        max_charts = max(1, section_count // 2)
        return recommendations[:max_charts]

    def _record_layout(self, layout_type: LayoutType):
        """记录使用的布局"""
        self.recent_layouts.append(layout_type)

        # 保持历史记录在限制内
        if len(self.recent_layouts) > self.max_history:
            self.recent_layouts.pop(0)

    def analyze_data_characteristics(
        self,
        content: str,
        research_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分析内容的数据特性

        Args:
            content: 内容文本
            research_data: 行业调研数据

        Returns:
            Dict with has_time_series, has_comparison, has_distribution
        """
        characteristics = {
            "has_time_series": False,
            "has_comparison": False,
            "has_distribution": False
        }

        # 从内容中检测关键词
        time_keywords = ["trend", "growth", "over time", "year", "quarter", "month", "evolution", "trajectory"]
        comparison_keywords = ["vs", "versus", "compared to", "than", "ranking", "top", "best"]
        distribution_keywords = ["share", "percentage", "of total", "distribution", "breakdown", "portion"]

        content_lower = content.lower()

        for keyword in time_keywords:
            if keyword in content_lower:
                characteristics["has_time_series"] = True
                break

        for keyword in comparison_keywords:
            if keyword in content_lower:
                characteristics["has_comparison"] = True
                break

        for keyword in distribution_keywords:
            if keyword in content_lower:
                characteristics["has_distribution"] = True
                break

        # 从研究数据中提取图表类型信息
        if research_data and research_data.get("charts"):
            for chart in research_data["charts"]:
                # chart is a ChartData dataclass, access attributes directly
                chart_type = chart.chart_type.lower()
                if "line" in chart_type or chart_type == "line":
                    characteristics["has_time_series"] = True
                elif "bar" in chart_type or chart_type == "bar":
                    characteristics["has_comparison"] = True
                elif "pie" in chart_type or chart_type == "pie":
                    characteristics["has_distribution"] = True

        logger.info(f"Data characteristics: {characteristics}")

        return characteristics


# 单例实例
_design_spec_engine_instance = None


def get_design_specification_engine() -> DesignSpecificationEngine:
    """获取设计规范引擎单例"""
    global _design_spec_engine_instance
    if _design_spec_engine_instance is None:
        _design_spec_engine_instance = DesignSpecificationEngine()
    return _design_spec_engine_instance
