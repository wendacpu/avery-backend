# AI + SVG 混合渲染系统 - 集成指南

## 概述

混合渲染系统结合了 AI 生图和 SVG 精确布局的优势，为 Avery 项目提供高质量的信息图生成能力。

### 核心特性

1. **AI 生成创意元素**
   - 动态背景纹理
   - 装饰性图形
   - 主题图标

2. **SVG 精确控制**
   - 像素级文字布局
   - 响应式设计
   - 矢量级质量

3. **智能缓存**
   - 自动缓存 AI 元素
   - 显著降低 API 成本
   - 提升渲染速度

4. **降级机制**
   - AI 服务不可用时自动降级
   - 保证系统稳定性
   - 始终返回可用的 SVG

---

## 快速开始

### 1. 基础使用

```python
from api.services.hybrid_renderer import HybridRenderer

# 准备内容数据
content_data = {
    "title": "10个提升效率的AI工具",
    "subtitle": "2024年最新推荐",
    "sections": [
        {
            "title": "1. ChatGPT",
            "content": "强大的对话式AI助手，支持多种任务"
        },
        {
            "title": "2. Midjourney",
            "content": "专业的AI图像生成工具"
        },
        {
            "title": "3. Notion AI",
            "content": "智能文档写作助手"
        }
    ],
    "footer": "关注获取更多AI工具推荐"
}

# 配置风格
style_config = {
    "width": 1200,
    "height": 1600,
    "background_color": "#F7F4EF",
    "primary_color": "#2D5A3D",
    "secondary_color": "#C9A65C",
    "text_color": "#1F2328",
    "use_ai_background": True,  # 使用AI生成背景
    "theme": "technology and AI tools"
}

# 创建渲染器并渲染
renderer = HybridRenderer()
svg_content = await renderer.render(content_data, style_config)

# 保存到文件
with open("output.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

await renderer.close()
```

### 2. 便捷函数

```python
from api.services.hybrid_renderer import render_infographic

# 一行代码完成渲染
svg_content = await render_infographic(content_data, style_config)
```

---

## 高级配置

### 渲染配置选项

```python
from api.services.hybrid_renderer import RenderConfig

config = RenderConfig(
    width=1200,              # 画布宽度
    height=1600,             # 画布高度
    background_color="#F7F4EF",  # 背景色
    font_family="Arial, sans-serif",  # 字体
    primary_color="#2D5A3D",  # 主色调
    secondary_color="#C9A65C",  # 次要色调
    text_color="#1F2328",    # 文字颜色
    accent_colors=[          # 强调色列表
        "#B8D8BE",
        "#E6F4EA",
        "#FFF2CC"
    ]
)
```

### 风格预设

```python
# 执行风格
EXECUTIVE_STYLE = {
    "background_color": "#F7F4EF",
    "primary_color": "#2D5A3D",
    "secondary_color": "#C9A65C",
    "text_color": "#1F2328",
    "font_family": "Georgia, serif"
}

# 科技风格
TECH_STYLE = {
    "background_color": "#F0F4F8",
    "primary_color": "#0066CC",
    "secondary_color": "#00D4AA",
    "text_color": "#1A202C",
    "font_family": "Inter, system-ui, sans-serif"
}

# 创意风格
CREATIVE_STYLE = {
    "background_color": "#FFF5E6",
    "primary_color": "#FF6B35",
    "secondary_color": "#F7C59F",
    "text_color": "#2D3142",
    "font_family": "Poppins, sans-serif"
}
```

---

## 集成到现有系统

### 1. 在 FastAPI 路由中使用

```python
from fastapi import APIRouter, HTTPException
from api.services.hybrid_renderer import HybridRenderer

router = APIRouter()

@router.post("/api/render-infographic")
async def render_infographic_endpoint(request: dict):
    """渲染信息图 API"""
    try:
        # 提取参数
        content_data = request.get("content_data")
        style_config = request.get("style_config", {})

        # 设置默认值
        style_config.setdefault("use_ai_background", True)
        style_config.setdefault("width", 1200)
        style_config.setdefault("height", 1600)

        # 渲染
        renderer = HybridRenderer()
        svg_content = await renderer.render(content_data, style_config)
        await renderer.close()

        return {
            "success": True,
            "svg": svg_content,
            "size": len(svg_content)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. 与现有内容生成器集成

```python
from api.services.advanced_content_generator import AdvancedContentGenerator
from api.services.hybrid_renderer import HybridRenderer

async def generate_complete_infographic(topic: str):
    """生成完整的信息图（内容+渲染）"""

    # 1. 生成内容
    content_generator = AdvancedContentGenerator()
    content_result = await content_generator.generate_content(
        topic=topic,
        output_format="infographic"
    )

    # 2. 提取内容数据
    content_data = extract_content_from_result(content_result)

    # 3. 渲染信息图
    renderer = HybridRenderer()
    svg_content = await renderer.render(
        content_data=content_data,
        style_config=EXECUTIVE_STYLE
    )
    await renderer.close()

    return svg_content
```

### 3. 批量渲染

```python
async def batch_render_infographics(topics: list[str]):
    """批量渲染多个信息图"""

    renderer = HybridRenderer()
    results = []

    try:
        for topic in topics:
            # 为每个主题生成内容
            content_data = await generate_content_for_topic(topic)

            # 渲染
            svg = await renderer.render(
                content_data=content_data,
                style_config=EXECUTIVE_STYLE
            )

            results.append({
                "topic": topic,
                "svg": svg,
                "success": True
            })

    finally:
        await renderer.close()

    return results
```

---

## 缓存配置

### 1. 使用 Redis 缓存

```python
import redis
from api.services.hybrid_renderer import HybridRenderer

# 创建 Redis 客户端
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# 使用 Redis 缓存创建渲染器
renderer = HybridRenderer(redis_client=redis_client)
```

### 2. 缓存管理

```python
# 查看缓存状态
def get_cache_stats(renderer):
    """获取缓存统计信息"""
    memory_cache_size = len(renderer.cache_manager.memory_cache)

    return {
        "memory_cache_entries": memory_cache_size,
        "redis_enabled": renderer.cache_manager.redis_client is not None
    }

# 清空缓存
renderer.clear_cache()
```

---

## 错误处理

### 1. 自动降级

系统在 AI 服务不可用时会自动降级到纯 SVG 渲染：

```python
# 即使 AI 服务失败，也能正常渲染
svg_content = await renderer.render(content_data, style_config)
# 如果失败，会返回纯 SVG 版本
```

### 2. 自定义错误处理

```python
try:
    svg_content = await renderer.render(content_data, style_config)
except Exception as e:
    logger.error(f"Rendering failed: {e}")
    # 使用备用方案
    svg_content = await generate_fallback_svg(content_data)
```

---

## 性能优化

### 1. 减少AI调用

```python
# 对于相似主题，复用AI元素
style_config = {
    "use_ai_background": True,
    "theme": "business"  # 相同主题会复用缓存的背景
}
```

### 2. 批量处理

```python
# 复用渲染器实例
renderer = HybridRenderer()

for i in range(10):
    svg = await renderer.render(content_data, style_config)

await renderer.close()  # 最后统一关闭
```

### 3. 异步并发

```python
import asyncio

async def render_concurrent(topics: list[str]):
    """并发渲染多个信息图"""
    tasks = []
    for topic in topics:
        task = render_infographic(content_data, style_config)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results
```

---

## 测试

### 运行测试

```bash
# 运行所有测试
cd backend
pytest tests/test_hybrid_renderer.py -v

# 运行特定测试类
pytest tests/test_hybrid_renderer.py::TestHybridRenderer -v

# 生成覆盖率报告
pytest tests/test_hybrid_renderer.py --cov=api.services.hybrid_renderer --cov-report=html
```

### 测试示例

```python
import pytest
from api.services.hybrid_renderer import render_infographic

@pytest.mark.asyncio
async def test_basic_rendering():
    """测试基础渲染功能"""
    content_data = {
        "title": "Test",
        "sections": [{"title": "Section 1", "content": "Content"}]
    }
    style_config = {"use_ai_background": False}

    svg = await render_infographic(content_data, style_config)

    assert svg.startswith('<svg')
    assert "Test" in svg
```

---

## 常见问题

### Q: 如何自定义布局？

A: 可以通过修改 `content_data` 中的区块结构来自定义布局：

```python
content_data = {
    "title": "自定义标题",
    "sections": [
        {
            "title": "区块1",
            "content": "内容1",
            "custom_position": {"x": 100, "y": 200}  # 自定义位置
        }
    ]
}
```

### Q: 如何添加自定义图形？

A: 可以直接在生成的 SVG 中添加自定义元素：

```python
svg_content = await renderer.render(content_data, style_config)

# 在 SVG 中插入自定义图形
custom_shape = '<circle cx="100" cy="100" r="50" fill="#FF0000"/>'
svg_content = svg_content.replace('</svg>', f'{custom_shape}</svg>')
```

### Q: 如何导出为PNG？

A: 使用第三方库将 SVG 转换为 PNG：

```python
from cairosvg import svg2png

svg_content = await renderer.render(content_data, style_config)
png_bytes = svg2png(bytestring=svg_content.encode())

with open("output.png", "wb") as f:
    f.write(png_bytes)
```

### Q: 缓存会占用多少空间？

A: 默认情况下，缓存在24小时后自动过期。可以通过 `cache_ttl` 参数调整：

```python
from api.services.hybrid_renderer import HybridCache

cache = HybridCache()
cache.cache_ttl = 172800  # 48小时
```

---

## 最佳实践

1. **复用渲染器实例**
   ```python
   # ✅ 好 - 复用实例
   renderer = HybridRenderer()
   for topic in topics:
       svg = await renderer.render(content_data, style_config)
   await renderer.close()

   # ❌ 差 - 每次创建新实例
   for topic in topics:
       renderer = HybridRenderer()
       svg = await renderer.render(content_data, style_config)
   ```

2. **启用缓存**
   ```python
   # 生产环境建议启用 Redis
   renderer = HybridRenderer(redis_client=redis_client)
   ```

3. **设置合理的超时**
   ```python
   # AI 生图可能需要较长时间
   import asyncio
   svg = await asyncio.wait_for(
       renderer.render(content_data, style_config),
       timeout=120.0  # 2分钟超时
   )
   ```

4. **监控性能**
   ```python
   import time

   start = time.time()
   svg = await renderer.render(content_data, style_config)
   duration = time.time() - start

   logger.info(f"Rendering took {duration:.2f}s")
   ```

---

## 扩展开发

### 添加新的AI元素类型

```python
from api.services.hybrid_renderer import ElementType

# 添加新的元素类型
class ElementType(Enum):
    BACKGROUND = "background"
    DECORATION = "decoration"
    ICON = "icon"
    ILLUSTRATION = "illustration"
    CHART = "chart"  # 新增：图表类型

# 在 AIElementGenerator 中添加生成方法
async def generate_chart(self, data: dict) -> str:
    """生成AI图表"""
    # 实现图表生成逻辑
    pass
```

### 自定义布局策略

```python
class CustomLayoutBuilder:
    """自定义布局构建器"""

    def build_layout(self, content_data, config):
        # 实现自定义布局逻辑
        pass

# 在 HybridRenderer 中使用
renderer = HybridRenderer()
renderer.svg_builder = CustomLayoutBuilder()
```

---

## 参考资源

- [SVG 规范](https://www.w3.org/TR/SVG/)
- [FastAPI 异步编程](https://fastapi.tiangolo.com/async/)
- [Redis Python 客户端](https://redis-py.readthedocs.io/)
- [CairoSVG 转换工具](https://cairosvg.org/)

---

## 更新日志

### v1.0.0 (2025-01-15)
- 初始版本发布
- 支持AI背景生成
- SVG精确布局控制
- 智能缓存机制
- 自动降级处理
- 完整测试覆盖
