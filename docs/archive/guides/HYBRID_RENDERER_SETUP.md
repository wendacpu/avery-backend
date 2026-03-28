# AI + SVG 混合渲染系统 - 环境配置

## 依赖包

混合渲染系统需要以下 Python 包：

```txt
# 核心依赖
httpx>=0.24.0
redis>=4.5.0

# 可选依赖（用于测试）
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0

# 可选依赖（用于SVG转PNG）
cairosvg>=2.6.0

# 现有系统依赖
pydantic>=2.0.0
pydantic-settings>=2.0.0
openai>=1.0.0
```

## 安装步骤

### 1. 安装核心依赖

```bash
cd backend
pip install httpx redis
```

### 2. 安装测试依赖（可选）

```bash
pip install pytest pytest-asyncio pytest-cov
```

### 3. 安装 SVG 转 PNG 工具（可选）

```bash
# macOS
brew install cairo

pip install cairosvg

# Ubuntu/Debian
sudo apt-get install libcairo2-dev
pip install cairosvg
```

## 配置

### 1. 环境变量

在 `.env` 文件中添加：

```env
# Redis 配置（可选，用于缓存）
REDIS_URL=redis://localhost:6379/0

# AI API 配置
NOVITA_API_KEY=your-novita-api-key-here
GROQ_API_KEY=your-groq-api-key-here
```

### 2. Redis 配置（可选）

如果使用 Redis 缓存：

```bash
# 启动 Redis
docker run -d -p 6379:6379 redis:latest

# 或使用本地安装
redis-server
```

## 快速测试

### 1. 测试 SVG 生成

```python
from api.services.hybrid_renderer import HybridRenderer

async def test():
    renderer = HybridRenderer()

    content_data = {
        "title": "测试标题",
        "subtitle": "测试副标题",
        "sections": [
            {"title": "区块1", "content": "内容1"}
        ],
        "footer": "页脚"
    }

    style_config = {
        "use_ai_background": False,
        "width": 1200,
        "height": 1600
    }

    svg = await renderer.render(content_data, style_config)

    with open("test.svg", "w") as f:
        f.write(svg)

    await renderer.close()

import asyncio
asyncio.run(test())
```

### 2. 运行完整测试套件

```bash
cd backend
pytest tests/test_hybrid_renderer.py -v
```

### 3. 运行示例

```bash
cd backend
python api/services/hybrid_renderer.py
```

## 故障排除

### 问题 1: ModuleNotFoundError

**错误**: `ModuleNotFoundError: No module named 'pydantic_settings'`

**解决**:
```bash
pip install pydantic-settings
```

### 问题 2: Redis 连接失败

**错误**: `redis.exceptions.ConnectionError`

**解决**:
- 检查 Redis 是否运行: `redis-cli ping`
- 不使用 Redis: 创建渲染器时不传 `redis_client` 参数

### 问题 3: AI API 调用失败

**错误**: `Novita API Key 未配置`

**解决**:
- 在 `.env` 中配置 API 密钥
- 或设置 `use_ai_background=False` 使用纯 SVG 模式

## 性能优化建议

### 1. 使用 Redis 缓存

```python
import redis
from api.services.hybrid_renderer import HybridRenderer

redis_client = redis.Redis(host='localhost', port=6379, db=0)
renderer = HybridRenderer(redis_client=redis_client)
```

### 2. 批量处理时复用渲染器

```python
renderer = HybridRenderer()

for topic in topics:
    svg = await renderer.render(content_data, style_config)

await renderer.close()
```

### 3. 禁用 AI 背景以加快速度

```python
style_config["use_ai_background"] = False
```

## 监控和日志

### 启用详细日志

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api.services.hybrid_renderer")
logger.setLevel(logging.DEBUG)
```

### 性能监控

```python
import time

start = time.time()
svg = await renderer.render(content_data, style_config)
duration = time.time() - start

logger.info(f"Rendering took {duration:.2f}s, SVG size: {len(svg)} bytes")
```

## 生产环境部署

### 1. 使用 Gunicorn

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app
```

### 2. 配置 Redis 持久化

```bash
# redis.conf
save 900 1
save 300 10
save 60 10000
```

### 3. 设置合理的超时

```python
import asyncio

svg = await asyncio.wait_for(
    renderer.render(content_data, style_config),
    timeout=120.0  # 2分钟
)
```

## 更新和维护

### 查看缓存统计

```python
def get_cache_stats(renderer):
    return {
        "memory_cache_entries": len(renderer.cache_manager.memory_cache),
        "redis_enabled": renderer.cache_manager.redis_client is not None
    }
```

### 清空缓存

```python
renderer.clear_cache()
```

### 更新风格库

编辑 `api/prompts/infographic_styles.py` 添加新风格。

## 支持和帮助

- 查看文档: `backend/HYBRID_RENDERER_GUIDE.md`
- 查看示例: `backend/api/services/hybrid_renderer.py` (底部的 `if __name__ == "__main__"` 部分)
- 查看集成示例: `backend/api/services/hybrid_renderer_integration.py`
