"""
增强版混合渲染器 - 集成所有优化
整合 Prompt 优化、智能缓存、降级策略和内容映射
"""
import asyncio
import logging
from typing import Dict, Any, Optional
import httpx

from api.services.hybrid_renderer import (
    RenderConfig,
    ContentSection,
    SVGBuilder
)
from api.services.prompt_builder import (
    PromptBuilder,
    ContentData as PromptContentData,
    StyleConfig as PromptStyleConfig,
    LayoutType,
    VisualStyle
)
from api.services.fallback_strategy import (
    EnhancedFallbackManager,
    FallbackStrategy,
    RetryConfig
)
from api.services.smart_cache import SmartHybridCache
from api.services.content_mapper import (
    EnhancedContentMapper,
    StructuredContent,
    VisualizationPromptGenerator
)
from api.services.image_generator import ImageGenerator
from api.core.config import settings

logger = logging.getLogger(__name__)


class EnhancedHybridRenderer:
    """增强版混合渲染器"""

    def __init__(self, redis_client=None):
        """
        初始化增强版渲染器

        Args:
            redis_client: Redis 客户端（可选）
        """
        # 优化的组件
        self.cache_manager = SmartHybridCache(redis_client)
        self.fallback_manager = EnhancedFallbackManager()
        self.prompt_builder = PromptBuilder()
        self.content_mapper = EnhancedContentMapper()
        self.viz_prompt_gen = VisualizationPromptGenerator()
        self.svg_builder = SVGBuilder()
        self.image_generator = ImageGenerator()
        self.client = httpx.AsyncClient(timeout=60.0)

        logger.info("✅ EnhancedHybridRenderer initialized with all optimizations")

    async def render(
        self,
        content_data: Dict[str, Any],
        style_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        增强版混合渲染

        Args:
            content_data: 内容数据
            style_config: 风格配置

        Returns:
            渲染结果字典
        """
        try:
            logger.info("🎨 Starting enhanced hybrid rendering...")

            # 1. 提取和映射内容
            logger.info("📝 Step 1: Extracting and mapping content...")
            structured_content = self._extract_content(content_data)

            # 2. 构建优化的 prompt
            logger.info("🎨 Step 2: Building optimized prompt...")
            optimized_prompt = self._build_optimized_prompt(
                structured_content,
                style_config
            )

            # 3. 生成 AI 背景（使用降级策略）
            logger.info("🖼️  Step 3: Generating AI background with fallback...")
            background_result = await self._generate_background_with_fallback(
                structured_content,
                style_config,
                optimized_prompt
            )

            # 4. 构建 SVG 布局
            logger.info("📐 Step 4: Building SVG layout...")
            svg_content = await self._build_svg_layout(
                structured_content,
                style_config,
                background_result.data
            )

            logger.info("✅ Enhanced hybrid rendering completed successfully")

            return {
                "success": True,
                "svg": svg_content,
                "metadata": {
                    "strategy_used": background_result.strategy_used.value,
                    "content_type": structured_content.content_type.value,
                    "prompt_length": len(optimized_prompt),
                    "cache_stats": self.cache_manager.get_stats()
                }
            }

        except Exception as e:
            logger.error(f"❌ Enhanced rendering failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "svg": None
            }

    def _extract_content(self, content_data: Dict[str, Any]) -> StructuredContent:
        """提取结构化内容"""
        # 将内容数据转换为文本
        raw_text = self._content_data_to_text(content_data)

        # 使用增强的映射器提取结构化内容
        topic = content_data.get("title", "Untitled")
        structured = self.content_mapper.extract_structured_content(
            raw_text=raw_text,
            topic=topic
        )

        return structured

    def _content_data_to_text(self, content_data: Dict[str, Any]) -> str:
        """将内容数据转换为文本"""
        parts = []

        # 标题
        if title := content_data.get("title"):
            parts.append(f"# {title}")

        # 副标题
        if subtitle := content_data.get("subtitle"):
            parts.append(subtitle)

        # 章节
        for section in content_data.get("sections", []):
            if section_title := section.get("title"):
                parts.append(f"\n## {section_title}")

            if section_content := section.get("content"):
                parts.append(section_content)

        # 页脚
        if footer := content_data.get("footer"):
            parts.append(f"\n---\n{footer}")

        return "\n".join(parts)

    def _build_optimized_prompt(
        self,
        structured_content: StructuredContent,
        style_config: Dict[str, Any]
    ) -> str:
        """构建优化的 prompt"""
        # 转换为 Prompt Builder 所需的格式
        prompt_content = PromptContentData(
            title=structured_content.title,
            subtitle=structured_content.subtitle,
            key_points=structured_content.key_points[:8]
        )

        # 转换风格配置
        visual_style = self._map_visual_style(style_config)
        prompt_style = PromptStyleConfig(
            primary_color=style_config.get("primary_color", "#2D5A3D"),
            secondary_color=style_config.get("secondary_color", "#C9A65C"),
            background_color=style_config.get("background_color", "#F7F4EF"),
            text_color=style_config.get("text_color", "#1F2328"),
            visual_style=visual_style
        )

        # 选择布局类型
        layout_type = self._select_layout_type(structured_content)

        # 生成 prompt
        return self.prompt_builder.build_infographic_prompt(
            content=prompt_content,
            style=prompt_style,
            layout_type=layout_type
        )

    def _map_visual_style(self, style_config: Dict[str, Any]) -> VisualStyle:
        """映射视觉风格"""
        # 根据配置选择合适的视觉风格
        if "tech" in str(style_config).lower():
            return VisualStyle.TECH
        elif "minimal" in str(style_config).lower():
            return VisualStyle.MINIMALIST
        elif "playful" in str(style_config).lower():
            return VisualStyle.PLAYFUL
        elif "elegant" in str(style_config).lower():
            return VisualStyle.ELEGANT
        else:
            return VisualStyle.PROFESSIONAL

    def _select_layout_type(self, structured_content: StructuredContent) -> LayoutType:
        """选择布局类型"""
        if structured_content.content_type.value == "steps":
            return LayoutType.VERTICAL_FLOW
        elif structured_content.content_type.value == "comparison":
            return LayoutType.COMPARISON
        else:
            return LayoutType.MODULAR_GRID

    async def _generate_background_with_fallback(
        self,
        structured_content: StructuredContent,
        style_config: Dict[str, Any],
        optimized_prompt: str
    ):
        """使用降级策略生成背景"""
        # 定义生成函数
        async def generate_ai_bg():
            # 检查缓存
            cache_key_params = {
                "theme": structured_content.title,
                "type": structured_content.content_type.value
            }

            cached_value = self.cache_manager.get(
                element_type="background",
                params=cache_key_params,
                enable_similarity=True
            )

            if cached_value:
                logger.info("✅ Using cached background")
                return cached_value

            # 使用优化的 prompt 生成
            image_url = self.image_generator.generate_image(
                content=optimized_prompt,
                topic=structured_content.title,
                content_type="custom",
                detailed_prompt=optimized_prompt
            )

            # 缓存结果
            self.cache_manager.set(
                element_type="background",
                params=cache_key_params,
                value=image_url
            )

            return image_url

        # 使用降级策略
        return await self.fallback_manager.generate_with_fallback(
            ai_generator_func=generate_ai_bg,
            style_config=style_config,
            fallback_order=[
                FallbackStrategy.FULL_AI,
                FallbackStrategy.SVG_PATTERN,
                FallbackStrategy.SVG_GRADIENT,
                FallbackStrategy.SOLID_COLOR
            ]
        )

    async def _build_svg_layout(
        self,
        structured_content: StructuredContent,
        style_config: Dict[str, Any],
        background_image: Optional[str]
    ) -> str:
        """构建 SVG 布局"""
        # 创建渲染配置
        config = RenderConfig(
            width=style_config.get("width", 1200),
            height=style_config.get("height", 1600),
            background_color=style_config.get("background_color", "#FFFFFF"),
            font_family=style_config.get("font_family", "Arial, sans-serif"),
            primary_color=style_config.get("primary_color", "#2D5A3D"),
            secondary_color=style_config.get("secondary_color", "#C9A65C"),
            text_color=style_config.get("text_color", "#1F2328")
        )

        # 创建内容区块
        sections = self._create_sections_from_structured(
            structured_content,
            config
        )

        # 构建 SVG
        return self.svg_builder.build_layout(
            sections=sections,
            config=config,
            background_image=background_image
        )

    def _create_sections_from_structured(
        self,
        structured: StructuredContent,
        config: RenderConfig
    ):
        """从结构化内容创建区块"""
        sections = []

        # 计算布局
        header_height = 200
        footer_height = 80
        content_height = config.height - header_height - footer_height

        # 标题区块
        sections.append(ContentSection(
            title=structured.title,
            content=structured.subtitle,
            section_type="header",
            position={
                "x": 40,
                "y": 40,
                "width": config.width - 80,
                "height": header_height - 40
            }
        ))

        # 内容区块
        content_items = structured.key_points or structured.steps or structured.key_points
        num_sections = len(content_items)
        section_height = (content_height - 40) / max(num_sections, 1) if num_sections > 0 else content_height

        for i, item in enumerate(content_items):
            y_pos = header_height + 20 + i * (section_height + 20)

            sections.append(ContentSection(
                title=f"",  # 可以根据需要添加标题
                content=item,
                section_type="content",
                position={
                    "x": 40,
                    "y": y_pos,
                    "width": config.width - 80,
                    "height": section_height
                }
            ))

        return sections

    async def close(self):
        """关闭资源"""
        await self.client.aclose()
        await self.image_generator.client.aclose() if hasattr(self.image_generator, 'client') else None


# 便捷函数
async def render_infographic_enhanced(
    content_data: Dict[str, Any],
    style_config: Dict[str, Any],
    redis_client=None
) -> Dict[str, Any]:
    """
    快速渲染增强版信息图

    Args:
        content_data: 内容数据
        style_config: 风格配置
        redis_client: Redis 客户端（可选）

    Returns:
        渲染结果字典
    """
    renderer = EnhancedHybridRenderer(redis_client)
    try:
        return await renderer.render(content_data, style_config)
    finally:
        await renderer.close()


# 使用示例
if __name__ == "__main__":
    async def example():
        """使用示例"""

        # 内容数据
        content_data = {
            "title": "10个提升效率的AI工具",
            "subtitle": "2024年最新推荐",
            "sections": [
                {
                    "title": "1. ChatGPT",
                    "content": "强大的对话式AI助手，支持多种任务，包括写作、编程、分析等"
                },
                {
                    "title": "2. Midjourney",
                    "content": "专业的AI图像生成工具，创造独特的视觉内容"
                },
                {
                    "title": "3. Notion AI",
                    "content": "智能文档写作助手，提升文档创作效率"
                },
                {
                    "title": "4. GitHub Copilot",
                    "content": "AI编程助手，实时代码补全和建议"
                }
            ],
            "footer": "关注获取更多AI工具推荐"
        }

        # 风格配置
        style_config = {
            "width": 1200,
            "height": 1600,
            "background_color": "#F7F4EF",
            "primary_color": "#2D5A3D",
            "secondary_color": "#C9A65C",
            "text_color": "#1F2328",
            "use_ai_background": True,
            "theme": "AI tools and productivity"
        }

        # 渲染
        result = await render_infographic_enhanced(
            content_data=content_data,
            style_config=style_config
        )

        if result["success"]:
            print("✅ Rendering successful!")
            print(f"Strategy: {result['metadata']['strategy_used']}")
            print(f"Content type: {result['metadata']['content_type']}")
            print(f"SVG size: {len(result['svg'])} bytes")

            # 保存到文件
            output_file = "/Users/wanting/program/CC/Avery/enhanced_output.svg"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result["svg"])
            print(f"✅ Saved to: {output_file}")
        else:
            print(f"❌ Rendering failed: {result['error']}")

    # 运行示例
    asyncio.run(example())
