"""
内容到图片映射 - 增强版
使用 NLP 技术提升内容提取精度和结构化能力
"""
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """内容类型"""
    LIST = "list"  # 列表
    STEPS = "steps"  # 步骤流程
    COMPARISON = "comparison"  # 对比
    DATA = "data"  # 数据/统计
    CONCEPTS = "concepts"  # 概念解释
    TIPS = "tips"  # 技巧/建议


@dataclass
class StructuredContent:
    """结构化内容"""
    title: str
    subtitle: str = ""
    content_type: ContentType = ContentType.LIST
    key_points: List[str] = None
    statistics: List[Dict[str, Any]] = None
    comparisons: List[Dict[str, str]] = None
    steps: List[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.key_points is None:
            self.key_points = []
        if self.statistics is None:
            self.statistics = []
        if self.comparisons is None:
            self.comparisons = []
        if self.steps is None:
            self.steps = []
        if self.tags is None:
            self.tags = []


class EnhancedContentMapper:
    """增强的内容映射器"""

    def __init__(self):
        """初始化内容映射器"""
        # 数字模式
        self.number_pattern = re.compile(r'\d+[%。，,]|\d+倍|\d+\+?\s*个?|\d+/\d+')
        # 百分比模式
        self.percent_pattern = re.compile(r'\d+%\s*(?:的|of)?')
        # 步骤模式
        self.step_pattern = re.compile(r'^(?:第)?\s*[一二三四五六七八九十\d]+\s*[、.步期]|^\d+\.')
        # 对比模式
        self.comparison_pattern = re.compile(
            r'(?:相比|对比|比较|vs|VS|versus|和|与| versus )',
            re.IGNORECASE
        )

        logger.info("✅ EnhancedContentMapper initialized")

    def extract_structured_content(
        self,
        raw_content: str,
        topic: str
    ) -> StructuredContent:
        """
        提取结构化内容

        Args:
            raw_content: 原始文本内容
            topic: 主题

        Returns:
            结构化内容对象
        """
        logger.info("🔍 Extracting structured content...")

        # 1. 提取标题
        title, subtitle = self._extract_title_subtitle(raw_content, topic)

        # 2. 识别内容类型
        content_type = self._identify_content_type(raw_content)

        # 3. 根据类型提取内容
        structured = StructuredContent(
            title=title,
            subtitle=subtitle,
            content_type=content_type
        )

        if content_type == ContentType.LIST:
            structured.key_points = self._extract_list_items(raw_content)
        elif content_type == ContentType.STEPS:
            structured.steps = self._extract_steps(raw_content)
        elif content_type == ContentType.COMPARISON:
            structured.comparisons = self._extract_comparisons(raw_content)
        elif content_type == ContentType.DATA:
            structured.statistics = self._extract_statistics(raw_content)
            structured.key_points = self._extract_list_items(raw_content)
        else:
            structured.key_points = self._extract_key_concepts(raw_content)

        # 4. 提取标签
        structured.tags = self._extract_tags(raw_content)

        logger.info(
            f"✅ Extracted: {content_type.value}, "
            f"{len(structured.key_points)} points, "
            f"{len(structured.statistics)} stats"
        )

        return structured

    def _extract_title_subtitle(
        self,
        content: str,
        topic: str
    ) -> Tuple[str, str]:
        """提取标题和副标题"""
        lines = content.split('\n')

        title = topic
        subtitle = ""

        # 查找标题
        for i, line in enumerate(lines[:20]):
            line = line.strip()

            # Markdown 标题
            if line.startswith('#'):
                title = line.lstrip('#').strip()
                # 检查下一行是否是副标题
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('#'):
                        subtitle = next_line
                break

            # 短行作为标题
            elif 10 < len(line) < 80 and not line.startswith(('-', '*', '•')):
                if not title or title == topic:
                    title = line

        return title, subtitle

    def _identify_content_type(self, content: str) -> ContentType:
        """识别内容类型"""
        content_lower = content.lower()

        # 步骤流程
        step_keywords = ['步骤', 'step', '阶段', '流程', '第一阶段', '首先', '然后', '最后', '1.', '2.', '3.']
        if any(keyword in content_lower for keyword in step_keywords):
            return ContentType.STEPS

        # 对比
        comparison_keywords = ['对比', '比较', 'vs', 'difference', '优缺点', 'pros and cons']
        if self.comparison_pattern.search(content) or \
           any(keyword in content_lower for keyword in comparison_keywords):
            return ContentType.COMPARISON

        # 数据统计
        data_keywords = ['数据', '统计', '研究', '调查', '%', 'percent', '增长', '下降']
        stat_count = len(self.number_pattern.findall(content))
        if stat_count >= 3 or any(keyword in content_lower for keyword in data_keywords):
            return ContentType.DATA

        # 技巧建议
        tips_keywords = ['技巧', '建议', '方法', '策略', 'tip', 'how to', '最佳实践']
        if any(keyword in content_lower for keyword in tips_keywords):
            return ContentType.TIPS

        # 默认为列表
        return ContentType.LIST

    def _extract_list_items(self, content: str) -> List[str]:
        """提取列表项"""
        items = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            # 匹配列表项
            if line.startswith(('-', '*', '•', '○')):
                item = line.lstrip('-*•○').strip()
                if 5 < len(item) < 200:
                    items.append(item)

            # 匹配数字列表
            elif re.match(r'^\d+[.、)\s]', line):
                item = re.sub(r'^\d+[.、)\s]\s*', '', line).strip()
                if 5 < len(item) < 200:
                    items.append(item)

        return items[:10]  # 最多返回10项

    def _extract_steps(self, content: str) -> List[str]:
        """提取步骤"""
        steps = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            # 匹配步骤行
            if self.step_pattern.search(line):
                step_text = self.step_pattern.sub('', line).strip()
                if step_text:
                    steps.append(step_text)

            # 或者是数字列表
            elif re.match(r'^\d+[.、]\s*\w', line):
                step_text = re.sub(r'^\d+[.、]\s*', '', line).strip()
                if step_text:
                    steps.append(step_text)

        return steps[:8]  # 最多返回8个步骤

    def _extract_comparisons(self, content: str) -> List[Dict[str, str]]:
        """提取对比内容"""
        comparisons = []

        # 简化实现:查找对比关键词附近的内容
        lines = content.split('\n')

        for i, line in enumerate(lines):
            if self.comparison_pattern.search(line):
                # 提取对比的关键词
                parts = self.comparison_pattern.split(line, maxsplit=1)
                if len(parts) >= 2:
                    comparisons.append({
                        "subject1": parts[0].strip(),
                        "subject2": parts[1].strip() if len(parts) > 1 else "",
                        "context": line
                    })

        return comparisons[:5]  # 最多返回5组对比

    def _extract_statistics(self, content: str) -> List[Dict[str, Any]]:
        """提取统计数据"""
        stats = []

        # 查找所有数字和百分比
        matches = self.number_pattern.findall(content)

        for match in matches[:10]:  # 最多10个数据
            # 提取数据上下文
            context = self._extract_stat_context(content, match)

            stats.append({
                "value": match,
                "context": context
            })

        return stats

    def _extract_stat_context(self, content: str, stat: str) -> str:
        """提取数据的上下文"""
        # 查找数据所在的句子
        sentences = re.split(r'[。！？.!?]', content)

        for sentence in sentences:
            if stat in sentence:
                # 清理句子
                context = sentence.strip()
                if 10 < len(context) < 150:
                    return context

        return stat  # 如果找不到上下文,返回数据本身

    def _extract_key_concepts(self, content: str) -> List[str]:
        """提取关键概念"""
        concepts = []

        # 提取加粗或强调的文本
        bold_pattern = re.compile(r'\*\*(.+?)\*\*|__(.+?)__')
        bold_matches = bold_pattern.findall(content)

        for match in bold_matches:
            concept = match[0] if match[0] else match[1]
            concepts.append(concept.strip())

        # 如果没有加粗文本,提取列表项
        if not concepts:
            concepts = self._extract_list_items(content)

        return concepts[:8]

    def _extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        tags = []

        # 常见标签关键词
        tag_keywords = [
            'AI', '人工智能', '机器学习', '深度学习',
            'Python', '编程', '开发',
            '数据', '分析', '可视化',
            '产品', '管理', '营销',
            '工具', '效率', '方法',
            '科技', '创新', '趋势'
        ]

        content_lower = content.lower()

        for keyword in tag_keywords:
            if keyword.lower() in content_lower:
                tags.append(keyword)

        return list(set(tags))[:5]  # 最多5个标签


class VisualizationPromptGenerator:
    """可视化提示词生成器"""

    def __init__(self):
        """初始化提示词生成器"""
        logger.info("✅ VisualizationPromptGenerator initialized")

    def generate_data_viz_prompt(
        self,
        statistics: List[Dict[str, Any]],
        style: Dict[str, Any]
    ) -> str:
        """
        生成数据可视化提示词

        Args:
            statistics: 统计数据列表
            style: 风格配置

        Returns:
            数据可视化提示词
        """
        if not statistics:
            return ""

        primary_color = style.get("primary_color", "#2D5A3D")

        prompt_parts = [
            "**DATA VISUALIZATION:**",
            f"Create professional charts and graphs using primary color: {primary_color}",
            ""
        ]

        for i, stat in enumerate(statistics[:5], 1):
            value = stat.get("value", "")
            context = stat.get("context", "")

            # 根据数据类型选择图表
            if '%' in value:
                chart_type = "pie chart or donut chart"
            elif '倍' in value or '+' in value:
                chart_type = "bar chart or growth indicator"
            else:
                chart_type = "simple statistic card"

            prompt_parts.append(
                f"Chart {i}: {chart_type} - {value} ({context})"
            )

        return "\n".join(prompt_parts)

    def generate_comparison_prompt(
        self,
        comparisons: List[Dict[str, str]],
        style: Dict[str, Any]
    ) -> str:
        """
        生成对比提示词

        Args:
            comparisons: 对比数据列表
            style: 风格配置

        Returns:
            对比提示词
        """
        if not comparisons:
            return ""

        prompt_parts = [
            "**COMPARISON LAYOUT:**",
            "Side-by-side comparison with clear visual separation",
            ""
        ]

        for i, comp in enumerate(comparisons[:3], 1):
            subject1 = comp.get("subject1", "")
            subject2 = comp.get("subject2", "")

            prompt_parts.append(
                f"Comparison {i}: {subject1} vs {subject2}"
            )

        return "\n".join(prompt_parts)


# 便捷函数
def extract_and_map_content(
    raw_content: str,
    topic: str
) -> StructuredContent:
    """
    快速提取和映射内容

    Args:
        raw_content: 原始内容
        topic: 主题

    Returns:
        结构化内容
    """
    mapper = EnhancedContentMapper()
    return mapper.extract_structured_content(raw_content, topic)


# 使用示例
if __name__ == "__main__":
    # 示例内容
    sample_content = """
# 10个提升效率的AI工具

## 2024年最新推荐

1. **ChatGPT** - 强大的对话式AI助手，支持多种任务
2. **Midjourney** - 专业的AI图像生成工具
3. **Notion AI** - 智能文档写作助手

根据研究，使用AI工具可以提高40%的工作效率。数据显示，85%的用户认为AI工具显著改善了他们的工作流程。

步骤:
1. 确定你的需求
2. 选择合适的工具
3. 学习使用方法
4. 持续优化工作流
    """

    # 提取结构化内容
    structured = extract_and_map_content(
        raw_content=sample_content,
        topic="AI效率工具"
    )

    print(f"Title: {structured.title}")
    print(f"Type: {structured.content_type.value}")
    print(f"Key Points: {len(structured.key_points)}")
    print(f"Statistics: {len(structured.statistics)}")
    print(f"Steps: {len(structured.steps)}")
    print(f"Tags: {structured.tags}")
