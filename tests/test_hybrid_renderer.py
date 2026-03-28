"""
混合渲染系统测试
遵循 TDD 原则：测试先行
"""
import asyncio
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.services.hybrid_renderer import (
    HybridRenderer,
    HybridCache,
    AIElementGenerator,
    SVGBuilder,
    RenderConfig,
    ContentSection,
    ElementType,
    render_infographic
)


class TestHybridCache:
    """测试缓存管理器"""

    def test_generate_cache_key(self):
        """测试缓存键生成"""
        cache = HybridCache()

        # 相同参数应生成相同的键
        params1 = {"theme": "tech", "style": "minimal"}
        params2 = {"theme": "tech", "style": "minimal"}
        params3 = {"theme": "business", "style": "minimal"}

        key1 = cache._generate_cache_key("background", params1)
        key2 = cache._generate_cache_key("background", params2)
        key3 = cache._generate_cache_key("background", params3)

        assert key1 == key2, "相同参数应生成相同缓存键"
        assert key1 != key3, "不同参数应生成不同缓存键"

    def test_memory_cache_set_get(self):
        """测试内存缓存读写"""
        cache = HybridCache()

        params = {"theme": "tech"}
        url = "https://example.com/image.png"

        # 写入缓存
        cache.set_ai_element("background", params, url)

        # 读取缓存
        cached_url = cache.get_ai_element("background", params)

        assert cached_url == url, "应返回缓存的 URL"

    def test_memory_cache_miss(self):
        """测试缓存未命中"""
        cache = HybridCache()

        params = {"theme": "tech"}
        cached_url = cache.get_ai_element("background", params)

        assert cached_url is None, "未命中时应返回 None"

    def test_clear_memory_cache(self):
        """测试清空内存缓存"""
        cache = HybridCache()

        # 写入缓存
        cache.set_ai_element("background", {"theme": "tech"}, "https://example.com/image.png")

        # 清空缓存
        cache.clear_memory_cache()

        # 验证已清空
        cached_url = cache.get_ai_element("background", {"theme": "tech"})
        assert cached_url is None, "清空后缓存应为空"


class TestSVGBuilder:
    """测试 SVG 构建器"""

    def test_init(self):
        """测试初始化"""
        builder = SVGBuilder()
        assert builder is not None

    def test_add_text_simple(self):
        """测试添加简单文字"""
        builder = SVGBuilder()
        config = RenderConfig()

        text_svg = builder.add_text(
            content="Hello World",
            x=100,
            y=200,
            config=config,
            font_size=16,
            font_weight="normal"
        )

        assert "Hello World" in text_svg
        assert 'x="100"' in text_svg
        assert 'y="200"' in text_svg
        assert 'font-size="16"' in text_svg

    def test_add_text_with_wrapping(self):
        """测试文字换行"""
        builder = SVGBuilder()
        config = RenderConfig()

        long_text = "This is a very long text that should be wrapped into multiple lines"
        text_svg = builder.add_text(
            content=long_text,
            x=100,
            y=200,
            config=config,
            font_size=16,
            max_width=200
        )

        # 应生成多个 text 元素
        assert text_svg.count('<text') > 1, "应生成多行文字"

    def test_embed_ai_image(self):
        """测试嵌入 AI 图片"""
        builder = SVGBuilder()

        image_svg = builder.embed_ai_image(
            ai_image_url="https://example.com/image.png",
            position={"x": 100, "y": 200, "width": 300, "height": 400}
        )

        assert 'https://example.com/image.png' in image_svg
        assert 'x="100"' in image_svg
        assert 'y="200"' in image_svg
        assert 'width="300"' in image_svg
        assert 'height="400"' in image_svg

    def test_embed_ai_image_with_clip_path(self):
        """测试带裁剪路径的图片嵌入"""
        builder = SVGBuilder()

        image_svg = builder.embed_ai_image(
            ai_image_url="https://example.com/image.png",
            position={"x": 100, "y": 200, "width": 300, "height": 400},
            clip_path="clip1"
        )

        assert 'clip-path="url(#clip1)"' in image_svg

    def test_build_layout_simple(self):
        """测试构建简单布局"""
        builder = SVGBuilder()
        config = RenderConfig()

        sections = [
            ContentSection(
                title="Header",
                content="Subtitle",
                section_type="header",
                position={"x": 0, "y": 0, "width": 1200, "height": 200}
            )
        ]

        svg = builder.build_layout(sections, config)

        assert svg.startswith('<svg')
        assert svg.endswith('</svg>')
        assert "Header" in svg
        assert "Subtitle" in svg

    def test_xml_escaping(self):
        """测试 XML 特殊字符转义"""
        builder = SVGBuilder()

        text_with_special_chars = "Text with <tags> & 'quotes' and \"double quotes\""
        escaped = builder._escape_xml(text_with_special_chars)

        assert "&lt;" in escaped
        assert "&gt;" in escaped
        assert "&amp;" in escaped
        assert "&quot;" in escaped
        assert "&apos;" in escaped


class TestAIElementGenerator:
    """测试 AI 元素生成器"""

    @pytest.fixture
    def generator(self):
        """创建生成器实例"""
        cache = HybridCache()
        return AIElementGenerator(cache)

    def test_init(self, generator):
        """测试初始化"""
        assert generator is not None
        assert generator.cache is not None
        assert generator.image_generator is not None

    def test_build_background_prompt(self, generator):
        """测试背景提示词构建"""
        style = {
            "background_color": "#FFFFFF",
            "primary_color": "#2D5A3D"
        }

        prompt = generator._build_background_prompt(style, "technology")

        assert "technology" in prompt
        assert "#FFFFFF" in prompt
        assert "#2D5A3D" in prompt
        assert "subtle" in prompt.lower()

    def test_build_icon_prompt(self, generator):
        """测试图标提示词构建"""
        prompt = generator._build_icon_prompt("analytics", "outline")

        assert "analytics" in prompt
        assert "outline" in prompt
        assert "professional" in prompt

    def test_generate_solid_color_background(self, generator):
        """测试生成纯色背景"""
        background_svg = generator._generate_solid_color_background("#FFFFFF")

        assert "data:image/svg+xml" in background_svg
        assert "#FFFFFF" in background_svg

    def test_generate_simple_decoration(self, generator):
        """测试生成简单装饰"""
        decoration_svg = generator._generate_simple_decoration()

        assert "data:image/svg+xml" in decoration_svg
        assert "circle" in decoration_svg

    def test_generate_simple_icon(self, generator):
        """测试生成简单图标"""
        icon_svg = generator._generate_simple_icon("Test")

        assert "data:image/svg+xml" in icon_svg
        assert "T" in icon_svg  # 首字母


class TestHybridRenderer:
    """测试混合渲染器"""

    @pytest.fixture
    def renderer(self):
        """创建渲染器实例"""
        return HybridRenderer()

    @pytest.fixture
    def sample_content_data(self):
        """示例内容数据"""
        return {
            "title": "Test Title",
            "subtitle": "Test Subtitle",
            "sections": [
                {
                    "title": "Section 1",
                    "content": "Content for section 1"
                },
                {
                    "title": "Section 2",
                    "content": "Content for section 2"
                }
            ],
            "footer": "Test Footer"
        }

    @pytest.fixture
    def sample_style_config(self):
        """示例风格配置"""
        return {
            "width": 1200,
            "height": 1600,
            "background_color": "#FFFFFF",
            "primary_color": "#2D5A3D",
            "use_ai_background": False
        }

    def test_init(self, renderer):
        """测试初始化"""
        assert renderer is not None
        assert renderer.cache_manager is not None
        assert renderer.ai_generator is not None
        assert renderer.svg_builder is not None

    def test_create_render_config(self, renderer, sample_style_config):
        """测试创建渲染配置"""
        config = renderer._create_render_config(sample_style_config)

        assert isinstance(config, RenderConfig)
        assert config.width == 1200
        assert config.height == 1600
        assert config.background_color == "#FFFFFF"
        assert config.primary_color == "#2D5A3D"

    def test_create_content_sections(self, renderer, sample_content_data):
        """测试创建内容区块"""
        config = RenderConfig()
        sections = renderer._create_content_sections(sample_content_data, config)

        assert len(sections) == 4  # 1 header + 2 content + 1 footer
        assert sections[0].section_type == "header"
        assert sections[1].section_type == "content"
        assert sections[2].section_type == "content"
        assert sections[3].section_type == "footer"

    def test_render_fallback_svg(self, renderer, sample_content_data, sample_style_config):
        """测试降级 SVG 渲染"""
        svg = renderer._render_fallback_svg(sample_content_data, sample_style_config)

        assert svg.startswith('<svg')
        assert svg.endswith('</svg>')
        assert "Test Title" in svg
        assert "Section 1" in svg
        assert "Test Footer" in svg

    @pytest.mark.asyncio
    async def test_render_without_ai(self, renderer, sample_content_data, sample_style_config):
        """测试不使用 AI 的渲染"""
        # 禁用 AI 背景
        sample_style_config["use_ai_background"] = False

        svg = await renderer.render(sample_content_data, sample_style_config)

        assert svg.startswith('<svg')
        assert svg.endswith('</svg>')
        assert "Test Title" in svg
        assert len(svg) > 1000  # SVG 应该有一定大小

    @pytest.mark.asyncio
    async def test_render_with_ai_mock(self, renderer, sample_content_data, sample_style_config):
        """测试使用 AI 的渲染（模拟）"""
        # 启用 AI 背景
        sample_style_config["use_ai_background"] = True

        # Mock AI 生成器
        with patch.object(renderer.ai_generator, 'generate_background', return_value="https://mock.ai/bg.png"):
            svg = await renderer.render(sample_content_data, sample_style_config)

            assert svg.startswith('<svg')
            assert svg.endswith('</svg>')
            assert "Test Title" in svg

    def test_clear_cache(self, renderer):
        """测试清空缓存"""
        # 添加一些缓存
        renderer.cache_manager.set_ai_element("test", {"key": "value"}, "https://example.com")

        # 清空缓存
        renderer.clear_cache()

        # 验证已清空
        cached = renderer.cache_manager.get_ai_element("test", {"key": "value"})
        assert cached is None


class TestRenderInfographic:
    """测试便捷渲染函数"""

    @pytest.mark.asyncio
    async def test_render_infographic_basic(self):
        """测试基本信息图渲染"""
        content_data = {
            "title": "Quick Test",
            "subtitle": "Testing the convenience function",
            "sections": [
                {"title": "Point 1", "content": "First point"}
            ],
            "footer": "End"
        }

        style_config = {
            "width": 800,
            "height": 1000,
            "use_ai_background": False
        }

        svg = await render_infographic(content_data, style_config)

        assert svg.startswith('<svg')
        assert "Quick Test" in svg
        assert "Point 1" in svg


class TestIntegration:
    """集成测试"""

    @pytest.mark.asyncio
    async def test_full_rendering_pipeline(self):
        """测试完整渲染流程"""
        content_data = {
            "title": "AI + SVG Hybrid Rendering",
            "subtitle": "Best of both worlds",
            "sections": [
                {
                    "title": "AI Elements",
                    "content": "Backgrounds, decorations, and icons generated by AI"
                },
                {
                    "title": "SVG Precision",
                    "content": "Text and layout controlled with pixel-perfect accuracy"
                },
                {
                    "title": "Smart Caching",
                    "content": "Reduce API calls and improve performance"
                }
            ],
            "footer": "Generated by Avery Hybrid Renderer"
        }

        style_config = {
            "width": 1200,
            "height": 1600,
            "background_color": "#F7F4EF",
            "primary_color": "#2D5A3D",
            "secondary_color": "#C9A65C",
            "text_color": "#1F2328",
            "use_ai_background": False,  # 使用纯 SVG 进行快速测试
            "theme": "technology"
        }

        renderer = HybridRenderer()

        try:
            # 执行渲染
            svg = await renderer.render(content_data, style_config)

            # 验证结果
            assert len(svg) > 5000, "SVG 应该有足够的内容"
            assert "AI + SVG Hybrid Rendering" in svg
            assert "AI Elements" in svg
            assert "SVG Precision" in svg
            assert "Smart Caching" in svg
            assert "Generated by Avery Hybrid Renderer" in svg

            # 验证 SVG 结构
            assert '<svg' in svg
            assert '</svg>' in svg
            assert 'xmlns="http://www.w3.org/2000/svg"' in svg

            # 验证区块数量
            assert "AI Elements" in svg
            assert "SVG Precision" in svg
            assert "Smart Caching" in svg

            print(f"✅ Integration test passed!")
            print(f"📊 Generated SVG size: {len(svg)} bytes")
            print(f"📝 Contains {svg.count('<text')} text elements")
            print(f"🎨 Contains {svg.count('<rect')} rectangle elements")

        finally:
            await renderer.close()


class TestErrorHandling:
    """错误处理测试"""

    @pytest.mark.asyncio
    async def test_ai_failure_fallback(self):
        """测试 AI 失败时的降级处理"""
        content_data = {
            "title": "Error Handling Test",
            "subtitle": "Should fallback to SVG only",
            "sections": [
                {"title": "Section 1", "content": "Content"}
            ]
        }

        style_config = {
            "use_ai_background": True,
            "theme": "test"
        }

        renderer = HybridRenderer()

        # Mock AI 生成器抛出异常
        async def mock_generate_failure(*args, **kwargs):
            raise Exception("AI service unavailable")

        with patch.object(renderer.ai_generator, 'generate_background', mock_generate_failure):
            # 应该降级到纯 SVG，不抛出异常
            svg = await renderer.render(content_data, style_config)

            assert svg is not None
            assert len(svg) > 0
            assert "Error Handling Test" in svg

        await renderer.close()

    def test_empty_content_data(self):
        """测试空内容数据"""
        renderer = HybridRenderer()

        empty_content = {
            "title": "",
            "sections": []
        }

        style_config = {
            "width": 1200,
            "height": 1600
        }

        config = renderer._create_render_config(style_config)
        sections = renderer._create_content_sections(empty_content, config)

        # 应该至少有 header
        assert len(sections) >= 1


# 运行测试的便捷函数
def run_tests():
    """运行所有测试"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
