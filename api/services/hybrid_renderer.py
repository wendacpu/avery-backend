"""
AI + SVG 混合渲染系统
结合 AI 生图和 SVG 精确布局，生成高质量信息图
"""
import asyncio
import hashlib
import json
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

import httpx
from api.services.image_generator import ImageGenerator
from api.core.config import settings

logger = logging.getLogger(__name__)


class ElementType(Enum):
    """AI 元素类型"""
    BACKGROUND = "background"
    DECORATION = "decoration"
    ICON = "icon"
    ILLUSTRATION = "illustration"


@dataclass
class RenderConfig:
    """渲染配置"""
    width: int = 1200
    height: int = 1600
    background_color: str = "#FFFFFF"
    font_family: str = "Arial, sans-serif"
    primary_color: str = "#2D5A3D"
    secondary_color: str = "#C9A65C"
    text_color: str = "#1F2328"
    accent_colors: List[str] = None

    def __post_init__(self):
        if self.accent_colors is None:
            self.accent_colors = ["#B8D8BE", "#E6F4EA", "#FFF2CC", "#FFE6E6", "#E6F7FA"]


@dataclass
class ContentSection:
    """内容区块"""
    title: str
    content: str
    section_type: str  # header, content, footer
    position: Dict[str, float]  # x, y, width, height


class HybridCache:
    """混合渲染缓存管理器"""

    def __init__(self, redis_client=None):
        """
        初始化缓存管理器

        Args:
            redis_client: Redis 客户端实例（可选）
        """
        self.redis_client = redis_client
        self.memory_cache: Dict[str, Tuple[str, float]] = {}
        self.cache_ttl = 86400  # 24小时

        logger.info("✅ HybridCache initialized")

    def _generate_cache_key(self, element_type: str, params: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 将参数转换为稳定字符串
        params_str = json.dumps(params, sort_keys=True)
        hash_obj = hashlib.md5(params_str.encode())
        return f"hybrid:{element_type}:{hash_obj.hexdigest()}"

    def get_ai_element(self, element_type: str, params: Dict[str, Any]) -> Optional[str]:
        """
        获取缓存的 AI 元素

        Args:
            element_type: 元素类型
            params: 生成参数

        Returns:
            缓存的图片 URL，如果不存在则返回 None
        """
        cache_key = self._generate_cache_key(element_type, params)

        # 优先从内存缓存读取
        if cache_key in self.memory_cache:
            url, timestamp = self.memory_cache[cache_key]
            logger.info(f"✅ Memory cache hit: {cache_key}")
            return url

        # 从 Redis 读取
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    # 同步到内存缓存
                    self.memory_cache[cache_key] = (data["url"], data["timestamp"])
                    logger.info(f"✅ Redis cache hit: {cache_key}")
                    return data["url"]
            except Exception as e:
                logger.warning(f"⚠️  Redis cache read failed: {e}")

        return None

    def set_ai_element(self, element_type: str, params: Dict[str, Any], url: str):
        """
        缓存 AI 元素

        Args:
            element_type: 元素类型
            params: 生成参数
            url: 图片 URL
        """
        import time

        cache_key = self._generate_cache_key(element_type, params)
        timestamp = time.time()

        # 写入内存缓存
        self.memory_cache[cache_key] = (url, timestamp)

        # 写入 Redis
        if self.redis_client:
            try:
                cache_data = {
                    "url": url,
                    "timestamp": timestamp,
                    "element_type": element_type
                }
                self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(cache_data)
                )
                logger.info(f"✅ Cached to Redis: {cache_key}")
            except Exception as e:
                logger.warning(f"⚠️  Redis cache write failed: {e}")

        logger.info(f"✅ Cached AI element: {element_type}")

    def clear_memory_cache(self):
        """清空内存缓存"""
        self.memory_cache.clear()
        logger.info("✅ Memory cache cleared")


class AIElementGenerator:
    """AI 元素生成器"""

    def __init__(self, cache_manager: HybridCache = None):
        """
        初始化 AI 元素生成器

        Args:
            cache_manager: 缓存管理器实例
        """
        self.image_generator = ImageGenerator()
        self.cache = cache_manager or HybridCache()
        self.client = httpx.AsyncClient(timeout=60.0)

        logger.info("✅ AIElementGenerator initialized")

    async def generate_background(
        self,
        style: Dict[str, Any],
        theme: str = ""
    ) -> str:
        """
        生成背景图片（AI）

        Args:
            style: 风格配置（颜色、纹理等）
            theme: 主题描述

        Returns:
            背景图片 URL
        """
        # 检查缓存
        cache_params = {"style": style, "theme": theme}
        cached_url = self.cache.get_ai_element(ElementType.BACKGROUND.value, cache_params)
        if cached_url:
            return cached_url

        # 构建提示词
        prompt = self._build_background_prompt(style, theme)

        try:
            # 生成图片
            image_url = await self._generate_image_async(prompt, theme)

            # 缓存结果
            self.cache.set_ai_element(ElementType.BACKGROUND.value, cache_params, image_url)

            return image_url

        except Exception as e:
            logger.error(f"❌ Background generation failed: {e}")
            # 返回纯色背景的 SVG
            return self._generate_solid_color_background(style.get("background_color", "#FFFFFF"))

    async def generate_decoration(
        self,
        theme: str,
        style: str = "minimal"
    ) -> str:
        """
        生成装饰元素（AI）

        Args:
            theme: 主题描述
            style: 装饰风格（minimal, artistic, geometric）

        Returns:
            装饰元素图片 URL
        """
        # 检查缓存
        cache_params = {"theme": theme, "style": style}
        cached_url = self.cache.get_ai_element(ElementType.DECORATION.value, cache_params)
        if cached_url:
            return cached_url

        # 构建提示词
        prompt = self._build_decoration_prompt(theme, style)

        try:
            # 生成图片
            image_url = await self._generate_image_async(prompt, f"decoration_{theme}")

            # 缓存结果
            self.cache.set_ai_element(ElementType.DECORATION.value, cache_params, image_url)

            return image_url

        except Exception as e:
            logger.error(f"❌ Decoration generation failed: {e}")
            # 返回简单的 SVG 装饰
            return self._generate_simple_decoration()

    async def generate_icon(
        self,
        concept: str,
        style: str = "outline"
    ) -> str:
        """
        生成图标（AI）

        Args:
            concept: 图标概念
            style: 图标风格（outline, filled, colorful）

        Returns:
            图标图片 URL
        """
        # 检查缓存
        cache_params = {"concept": concept, "style": style}
        cached_url = self.cache.get_ai_element(ElementType.ICON.value, cache_params)
        if cached_url:
            return cached_url

        # 构建提示词
        prompt = self._build_icon_prompt(concept, style)

        try:
            # 生成图片
            image_url = await self._generate_image_async(prompt, f"icon_{concept}")

            # 缓存结果
            self.cache.set_ai_element(ElementType.ICON.value, cache_params, image_url)

            return image_url

        except Exception as e:
            logger.error(f"❌ Icon generation failed: {e}")
            # 返回简单的 SVG 图标
            return self._generate_simple_icon(concept)

    def _build_background_prompt(self, style: Dict[str, Any], theme: str) -> str:
        """构建背景生成提示词"""
        bg_color = style.get("background_color", "#FFFFFF")
        primary_color = style.get("primary_color", "#2D5A3D")

        prompt = f"""Create a subtle, professional background image for a business infographic.

Theme: {theme}

Color scheme:
- Base: {bg_color}
- Accent: {primary_color}

Style requirements:
- Subtle texture or gradient (no harsh patterns)
- Professional and clean
- High resolution, seamless
- Suitable for text overlay (low contrast)
- Minimal distraction from content

Output: Square format, high resolution."""

        return prompt

    def _build_decoration_prompt(self, theme: str, style: str) -> str:
        """构建装饰元素提示词"""
        style_map = {
            "minimal": "clean lines, geometric shapes, minimal",
            "artistic": "elegant curves, artistic flair, sophisticated",
            "geometric": "angular shapes, symmetrical, modern"
        }

        style_desc = style_map.get(style, "clean and professional")

        prompt = f"""Create a decorative element for a business infographic.

Theme: {theme}
Style: {style_desc}

Requirements:
- Transparent background
- Scalable vector-style design
- Professional aesthetic
- Subtle and elegant
- Can be used as corner decoration or divider

Output: High resolution, PNG with transparency."""

        return prompt

    def _build_icon_prompt(self, concept: str, style: str) -> str:
        """构建图标提示词"""
        style_map = {
            "outline": "line art, outline style, clean strokes",
            "filled": "solid filled, bold design",
            "colorful": "vibrant colors, modern flat design"
        }

        style_desc = style_map.get(style, "outline style")

        prompt = f"""Create a professional icon representing: {concept}

Style: {style_desc}

Requirements:
- Simple and recognizable
- Professional business aesthetic
- Transparent background
- Scalable design
- High resolution

Output: 512x512 PNG with transparency."""

        return prompt

    async def _generate_image_async(self, prompt: str, topic: str) -> str:
        """异步生成图片"""
        # 在实际实现中，这里会调用 AI 图片生成 API
        # 目前使用同步的 ImageGenerator
        loop = asyncio.get_event_loop()
        image_url = await loop.run_in_executor(
            None,
            lambda: self.image_generator.generate_image(
                content=topic,
                topic=topic,
                content_type="custom",
                detailed_prompt=prompt
            )
        )
        return image_url

    def _generate_solid_color_background(self, color: str) -> str:
        """生成纯色背景 SVG（作为 data URI）"""
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600">
            <rect width="100%" height="100%" fill="{color}"/>
        </svg>'''
        return f"data:image/svg+xml;base64,{svg.encode().hex()}"

    def _generate_simple_decoration(self) -> str:
        """生成简单装饰 SVG"""
        svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
            <circle cx="100" cy="100" r="80" fill="none" stroke="#2D5A3D" stroke-width="2"/>
            <circle cx="100" cy="100" r="60" fill="none" stroke="#C9A65C" stroke-width="1"/>
        </svg>'''
        return f"data:image/svg+xml;base64,{svg.encode().hex()}"

    def _generate_simple_icon(self, concept: str) -> str:
        """生成简单图标 SVG"""
        # 简单的圆形图标
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">
            <circle cx="32" cy="32" r="28" fill="#2D5A3D" opacity="0.2"/>
            <circle cx="32" cy="32" r="24" fill="none" stroke="#2D5A3D" stroke-width="2"/>
            <text x="32" y="40" font-family="Arial" font-size="20" text-anchor="middle" fill="#2D5A3D">{concept[0].upper()}</text>
        </svg>'''
        return f"data:image/svg+xml;base64,{svg.encode().hex()}"

    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


class SVGBuilder:
    """SVG 构建器 - 精确控制布局和文字"""

    def __init__(self):
        logger.info("✅ SVGBuilder initialized")

    def build_layout(
        self,
        sections: List[ContentSection],
        config: RenderConfig,
        background_image: Optional[str] = None
    ) -> str:
        """
        构建 SVG 布局结构

        Args:
            sections: 内容区块列表
            config: 渲染配置
            background_image: 背景图片 URL（可选）

        Returns:
            完整的 SVG 字符串
        """
        # 构建 SVG 头部
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{config.width}" height="{config.height}" '
            f'viewBox="0 0 {config.width} {config.height}">'
        ]

        # 添加背景
        if background_image:
            svg_parts.append(self._embed_background(background_image, config))
        else:
            svg_parts.append(f'<rect width="100%" height="100%" fill="{config.background_color}"/>')

        # 添加内容区块
        for section in sections:
            if section.section_type == "header":
                svg_parts.append(self._build_header_section(section, config))
            elif section.section_type == "content":
                svg_parts.append(self._build_content_section(section, config))
            elif section.section_type == "footer":
                svg_parts.append(self._build_footer_section(section, config))

        # 闭合 SVG
        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)

    def add_text(
        self,
        content: str,
        x: float,
        y: float,
        config: RenderConfig,
        font_size: int = 16,
        font_weight: str = "normal",
        color: Optional[str] = None,
        max_width: Optional[float] = None
    ) -> str:
        """
        添加精确控制的文字

        Args:
            content: 文字内容
            x: X 坐标
            y: Y 坐标
            config: 渲染配置
            font_size: 字体大小
            font_weight: 字体粗细
            color: 文字颜色（可选，默认使用配置）
            max_width: 最大宽度（用于换行）

        Returns:
            SVG 文字元素
        """
        text_color = color or config.text_color

        if max_width:
            # 需要换行
            lines = self._wrap_text(content, font_size, max_width)
            text_elements = []
            for i, line in enumerate(lines):
                text_elements.append(
                    f'<text x="{x}" y="{y + i * font_size * 1.2}" '
                    f'font-family="{config.font_family}" '
                    f'font-size="{font_size}" '
                    f'font-weight="{font_weight}" '
                    f'fill="{text_color}">{self._escape_xml(line)}</text>'
                )
            return '\n'.join(text_elements)
        else:
            return (
                f'<text x="{x}" y="{y}" '
                f'font-family="{config.font_family}" '
                f'font-size="{font_size}" '
                f'font-weight="{font_weight}" '
                f'fill="{text_color}">{self._escape_xml(content)}</text>'
            )

    def embed_ai_image(
        self,
        ai_image_url: str,
        position: Dict[str, float],
        clip_path: Optional[str] = None
    ) -> str:
        """
        嵌入 AI 生成的图片

        Args:
            ai_image_url: AI 图片 URL
            position: 位置和尺寸 (x, y, width, height)
            clip_path: 裁剪路径 ID（可选）

        Returns:
            SVG image 元素
        """
        attrs = [
            f'xlink:href="{ai_image_url}"',
            f'x="{position["x"]}"',
            f'y="{position["y"]}"',
            f'width="{position["width"]}"',
            f'height="{position["height"]}"'
        ]

        if clip_path:
            attrs.append(f'clip-path="url(#{clip_path})"')

        return f'<image {" ".join(attrs)} xmlns:xlink="http://www.w3.org/1999/xlink"/>'

    def _build_header_section(self, section: ContentSection, config: RenderConfig) -> str:
        """构建标题区块"""
        parts = []

        # 添加标题背景
        parts.append(f'''
        <rect x="{section.position['x']}" y="{section.position['y']}"
              width="{section.position['width']}" height="{section.position['height']}"
              fill="{config.primary_color}" opacity="0.1"/>
        ''')

        # 添加主标题
        parts.append(self.add_text(
            section.title,
            section.position['x'] + 40,
            section.position['y'] + 60,
            config,
            font_size=48,
            font_weight="bold",
            color=config.primary_color
        ))

        # 添加副标题（如果有内容）
        if section.content:
            parts.append(self.add_text(
                section.content,
                section.position['x'] + 40,
                section.position['y'] + 120,
                config,
                font_size=24,
                font_weight="normal",
                color=config.text_color
            ))

        return '\n'.join(parts)

    def _build_content_section(self, section: ContentSection, config: RenderConfig) -> str:
        """构建内容区块"""
        parts = []

        # 添加区块背景（卡片效果）
        parts.append(f'''
        <rect x="{section.position['x']}" y="{section.position['y']}"
              width="{section.position['width']}" height="{section.position['height']}"
              fill="#FFFFFF" stroke="#E0E0E0" stroke-width="1" rx="8"/>
        ''')

        # 添加区块标题
        parts.append(self.add_text(
            section.title,
            section.position['x'] + 20,
            section.position['y'] + 35,
            config,
            font_size=20,
            font_weight="bold",
            color=config.primary_color
        ))

        # 添加内容（带换行）
        content_max_width = section.position['width'] - 40
        parts.append(self.add_text(
            section.content,
            section.position['x'] + 20,
            section.position['y'] + 70,
            config,
            font_size=16,
            font_weight="normal",
            color=config.text_color,
            max_width=content_max_width
        ))

        return '\n'.join(parts)

    def _build_footer_section(self, section: ContentSection, config: RenderConfig) -> str:
        """构建页脚区块"""
        parts = []

        # 添加分隔线
        parts.append(f'''
        <line x1="{section.position['x']}" y1="{section.position['y']}"
              x2="{section.position['x'] + section.position['width']}"
              y2="{section.position['y']}"
              stroke="{config.secondary_color}" stroke-width="2"/>
        ''')

        # 添加页脚文字
        parts.append(self.add_text(
            section.content,
            section.position['x'] + section.position['width'] / 2,
            section.position['y'] + 40,
            config,
            font_size=14,
            font_weight="normal",
            color=config.text_color
        ))

        return '\n'.join(parts)

    def _embed_background(self, background_url: str, config: RenderConfig) -> str:
        """嵌入背景图片"""
        return f'''
        <image xlink:href="{background_url}"
               x="0" y="0"
               width="{config.width}" height="{config.height}"
               xmlns:xlink="http://www.w3.org/1999/xlink"
               opacity="0.3"/>
        '''

    def _wrap_text(self, text: str, font_size: int, max_width: float) -> List[str]:
        """简单的文字换行"""
        # 粗略估计：每个字符约为字体大小的 0.6 倍
        avg_char_width = font_size * 0.6
        max_chars = int(max_width / avg_char_width)

        words = text.split()
        lines = []
        current_line = []

        for word in words:
            if len(' '.join(current_line + [word])) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]

    def _escape_xml(self, text: str) -> str:
        """转义 XML 特殊字符"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))


class HybridRenderer:
    """混合渲染器 - 主入口"""

    def __init__(self, redis_client=None):
        """
        初始化混合渲染器

        Args:
            redis_client: Redis 客户端（可选，用于缓存）
        """
        self.cache_manager = HybridCache(redis_client)
        self.ai_generator = AIElementGenerator(self.cache_manager)
        self.svg_builder = SVGBuilder()

        logger.info("✅ HybridRenderer initialized")

    async def render(
        self,
        content_data: Dict[str, Any],
        style_config: Dict[str, Any]
    ) -> str:
        """
        混合渲染主函数

        Args:
            content_data: 内容数据
                {
                    "title": "主标题",
                    "subtitle": "副标题",
                    "sections": [
                        {"title": "区块1", "content": "内容1", "type": "content"},
                        ...
                    ],
                    "footer": "页脚文字"
                }
            style_config: 风格配置
                {
                    "width": 1200,
                    "height": 1600,
                    "background_color": "#FFFFFF",
                    "primary_color": "#2D5A3D",
                    "use_ai_background": true,
                    "theme": "technology"
                }

        Returns:
            最终渲染的 SVG 字符串
        """
        try:
            logger.info("🎨 Starting hybrid rendering...")

            # 1. 创建渲染配置
            config = self._create_render_config(style_config)

            # 2. 生成 AI 背景图片（如果需要）
            background_image = None
            if style_config.get("use_ai_background", False):
                theme = style_config.get("theme", "business")
                background_image = await self.ai_generator.generate_background(
                    style=style_config,
                    theme=theme
                )
                logger.info(f"✅ AI background generated: {background_image[:50]}...")

            # 3. 构建内容区块
            sections = self._create_content_sections(content_data, config)

            # 4. 使用 SVG 构建器组合所有元素
            svg_content = self.svg_builder.build_layout(
                sections=sections,
                config=config,
                background_image=background_image
            )

            logger.info("✅ Hybrid rendering completed successfully")

            return svg_content

        except Exception as e:
            logger.error(f"❌ Hybrid rendering failed: {e}", exc_info=True)
            # 返回纯 SVG 版本（不使用 AI）
            return self._render_fallback_svg(content_data, style_config)

    def _create_render_config(self, style_config: Dict[str, Any]) -> RenderConfig:
        """从风格配置创建渲染配置"""
        return RenderConfig(
            width=style_config.get("width", 1200),
            height=style_config.get("height", 1600),
            background_color=style_config.get("background_color", "#FFFFFF"),
            font_family=style_config.get("font_family", "Arial, sans-serif"),
            primary_color=style_config.get("primary_color", "#2D5A3D"),
            secondary_color=style_config.get("secondary_color", "#C9A65C"),
            text_color=style_config.get("text_color", "#1F2328"),
            accent_colors=style_config.get("accent_colors")
        )

    def _create_content_sections(
        self,
        content_data: Dict[str, Any],
        config: RenderConfig
    ) -> List[ContentSection]:
        """创建内容区块列表"""
        sections = []

        # 计算布局
        header_height = 200
        footer_height = 80
        content_height = config.height - header_height - footer_height

        # 标题区块
        sections.append(ContentSection(
            title=content_data.get("title", "Untitled"),
            content=content_data.get("subtitle", ""),
            section_type="header",
            position={
                "x": 40,
                "y": 40,
                "width": config.width - 80,
                "height": header_height - 40
            }
        ))

        # 内容区块
        content_sections = content_data.get("sections", [])
        num_sections = len(content_sections)
        section_height = (content_height - 40) / max(num_sections, 1) if num_sections > 0 else content_height

        for i, section_data in enumerate(content_sections):
            y_pos = header_height + 20 + i * (section_height + 20)

            sections.append(ContentSection(
                title=section_data.get("title", f"Section {i+1}"),
                content=section_data.get("content", ""),
                section_type="content",
                position={
                    "x": 40,
                    "y": y_pos,
                    "width": config.width - 80,
                    "height": section_height
                }
            ))

        # 页脚区块
        if content_data.get("footer"):
            sections.append(ContentSection(
                title="",
                content=content_data["footer"],
                section_type="footer",
                position={
                    "x": 0,
                    "y": config.height - footer_height,
                    "width": config.width,
                    "height": footer_height
                }
            ))

        return sections

    def _render_fallback_svg(
        self,
        content_data: Dict[str, Any],
        style_config: Dict[str, Any]
    ) -> str:
        """降级到纯 SVG 渲染（不使用 AI）"""
        logger.info("🔄 Using fallback SVG rendering")

        config = self._create_render_config(style_config)
        sections = self._create_content_sections(content_data, config)

        return self.svg_builder.build_layout(
            sections=sections,
            config=config,
            background_image=None
        )

    def clear_cache(self):
        """清空缓存"""
        self.cache_manager.clear_memory_cache()
        logger.info("✅ Cache cleared")

    async def close(self):
        """关闭资源"""
        await self.ai_generator.close()


# 便捷函数
async def render_infographic(
    content_data: Dict[str, Any],
    style_config: Dict[str, Any],
    redis_client=None
) -> str:
    """
    快速渲染信息图

    Args:
        content_data: 内容数据
        style_config: 风格配置
        redis_client: Redis 客户端（可选）

    Returns:
        SVG 字符串
    """
    renderer = HybridRenderer(redis_client)
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
            "title": "AI 驱动的混合渲染系统",
            "subtitle": "结合 AI 创意与 SVG 精确控制",
            "sections": [
                {
                    "title": "1. AI 背景生成",
                    "content": "使用 AI 生成独特的背景纹理和视觉元素，为信息图增添创意和专业感。"
                },
                {
                    "title": "2. SVG 精确布局",
                    "content": "使用 SVG 实现像素级精确的文本和布局控制，确保内容清晰易读。"
                },
                {
                    "title": "3. 智能缓存",
                    "content": "自动缓存 AI 生成的元素，显著降低 API 调用成本和等待时间。"
                },
                {
                    "title": "4. 降级机制",
                    "content": "即使 AI 服务不可用，仍能通过纯 SVG 生成高质量信息图。"
                }
            ],
            "footer": "Generated by Avery Hybrid Rendering System"
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
            "theme": "technology and innovation"
        }

        # 渲染
        renderer = HybridRenderer()
        svg_content = await renderer.render(content_data, style_config)

        # 保存到文件
        output_file = "/Users/wanting/program/CC/Avery/output_example.svg"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        print(f"✅ SVG saved to: {output_file}")
        print(f"📊 SVG size: {len(svg_content)} bytes")

        await renderer.close()

    # 运行示例
    import asyncio
    asyncio.run(example())
