# 调试指南 - Avery Content Generation System

本指南帮助你诊断和调试内容生成和图片生成问题。

---

## 📋 目录

1. [快速诊断](#快速诊断)
2. [查看后端日志](#查看后端日志)
3. [查看前端错误](#查看前端错误)
4. [数据库调试](#数据库调试)
5. [常见问题](#常见问题)
6. [API 测试](#api-测试)

---

## 🚀 快速诊断

### 第一步：检查后端是否运行

```bash
# 检查后端进程
ps aux | grep uvicorn

# 检查端口是否被占用
lsof -i :8000

# 查看后端日志
tail -f /path/to/backend/logs/app.log
```

### 第二步：检查 API 是否响应

```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试 API 根路径
curl http://localhost:8000/
```

### 第三步：检查数据库连接

```bash
# 进入后端目录
cd /Users/wanting/program/CC/Avery/backend

# 启动 Python 并测试
python3 << 'EOF'
from api.db.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ 数据库连接正常")
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")
EOF
```

---

## 🖥️ 查看后端日志

### 方法1：实时查看日志（推荐）

```bash
# 进入后端目录
cd /Users/wanting/program/CC/Avery/backend

# 如果使用 systemd/supervisord，查看日志
journalctl -u avery-backend -f  # Linux

# 如果直接运行，日志在控制台输出
```

### 方法2：启动时查看详细日志

```bash
# 设置日志级别为 DEBUG
export LOG_LEVEL=DEBUG

# 启动后端
python3 -m uvicorn api.main:app --reload --log-level debug
```

### 方法3：查看日志文件（如果配置了）

```bash
# 查看最近的错误
tail -100 logs/app.log | grep ERROR

# 查看图片生成相关的日志
tail -100 logs/app.log | grep -E "图片|Image|Gemini|Novita"

# 查看 deep search 相关的日志
tail -100 logs/app.log | grep -E "Deep|Tavily|Search"
```

---

## 🌐 查看前端错误

### 方法1：浏览器控制台（最直接）

1. **打开浏览器开发者工具**
   - Chrome/Edge: `F12` 或 `Cmd+Option+I` (Mac)
   - Firefox: `F12` 或 `Cmd+Option+I` (Mac)

2. **查看 Console 标签**
   - 红色错误信息
   - 警告信息
   - 网络请求失败

3. **查看 Network 标签**
   - 找到失败的 API 请求
   - 查看请求参数
   - 查看响应内容
   - 查看 HTTP 状态码

### 方法2：前端页面错误显示

前端会显示错误信息在页面上：

```
┌─────────────────────────────────────┐
│ ❌ [错误消息]                        │
│                                      │
│ 例如：                               │
│ - Generation failed                  │
│ - Failed to extract data            │
│ - Please enter LinkedIn URL         │
└─────────────────────────────────────┘
```

### 方法3：浏览器 Network 标签详细分析

1. 打开 Network 标签
2. 筛选 `fetch/XHR`
3. 找到 `/api/v1/content/generate` 请求
4. 查看：

   **Request Headers:**
   ```
   Content-Type: application/json
   Authorization: Bearer [token]
   ```

   **Request Payload:**
   ```json
   {
     "linkedin_url": "...",
     "job_title": "ceo_founder",
     "selected_topic": "...",
     "output_format": "with_image"
   }
   ```

   **Response:**
   - 状态码：200（成功）、400（参数错误）、500（服务器错误）
   - Response Body：包含 `id`、`status`、`error_message` 等

---

## 🗄️ 数据库调试

### 方法1：直接查询数据库

```bash
# 连接到 PostgreSQL
psql -U avery -d avery -h localhost

# 查看最近的生成记录
SELECT id, status, error_message, created_at, completed_at
FROM content_generations
ORDER BY created_at DESC
LIMIT 10;

# 查看失败的记录
SELECT id, selected_topic, error_message, created_at
FROM content_generations
WHERE status = 'failed'
ORDER BY created_at DESC
LIMIT 10;

# 查看生成的图片
SELECT id, selected_topic, generated_images
FROM content_generations
WHERE generated_images IS NOT NULL
LIMIT 5;
```

### 方法2：使用 Python 脚本

```python
# 文件名: debug_db.py
import sys
sys.path.insert(0, '/Users/wanting/program/CC/Avery/backend')

from api.db.database import SessionLocal
from api.models.content import ContentGeneration

db = SessionLocal()

# 查看最近的记录
records = db.query(ContentGeneration).order_by(
    ContentGeneration.created_at.desc()
).limit(10).all()

for r in records:
    print(f"ID: {r.id}")
    print(f"Status: {r.status}")
    print(f"Topic: {r.selected_topic}")
    print(f"Error: {r.error_message}")
    print(f"Image URL: {r.generated_images[0]['url'] if r.generated_images else 'N/A'}")
    print("---")

db.close()
```

运行：
```bash
python3 debug_db.py
```

---

## ❓ 常见问题

### 问题1：图片生成失败

**症状：**
- 生成过程正常完成，但没有图片
- 前端显示 "Generation completed" 但 `imageUrl` 为空

**诊断步骤：**

1. **检查后端日志**
   ```bash
   # 查找图片生成相关日志
   grep -E "图片|Image|Gemini|Novita" logs/app.log | tail -50
   ```

2. **检查 API Key 配置**
   ```bash
   # 查看 .env 文件
   grep NOVITA_API_KEY .env
   ```

3. **测试 Novita API 连接**
   ```bash
   python3 << 'EOF'
   import httpx

   api_key = "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"
   url = "https://api.novita.ai/v3/gemini-2.5-flash-image-text-to-image"

   response = httpx.post(url, json={
       "api_key": api_key,
       "prompt": "A simple test image",
       "aspect_ratio": "3:4"
   }, timeout=30)

   print(f"Status: {response.status_code}")
   print(f"Response: {response.text[:500]}")
   EOF
   ```

**可能原因：**
- ❌ Novita API key 未配置或无效
- ❌ API 调用超时
- ❌ Prompt 格式错误
- ❌ API 服务暂时不可用

**解决方案：**
1. 检查 `NOVITA_API_KEY` 是否正确配置在 `.env` 文件中
2. 检查后端日志中的详细错误信息
3. 尝试重新生成内容

---

### 问题2：Deep Search 失败

**症状：**
- 生成的内容缺少深度分析
- 没有数据支持
- 信息图没有图表

**诊断步骤：**

1. **检查 Tavily API 配置**
   ```bash
   grep TAVILY_API_KEY .env
   ```

2. **测试 Tavily API**
   ```bash
   python3 << 'EOF'
   import httpx

   api_key = "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"
   url = "https://api.tavily.com/search"

   response = httpx.post(url, json={
       "api_key": api_key,
       "query": "AI trends 2025",
       "max_results": 5
   })

   print(f"Status: {response.status_code}")
   print(f"Results: {len(response.json().get('results', []))}")
   EOF
   ```

3. **查看 Deep Search 日志**
   ```bash
   grep "Deep\|Tavily" logs/app.log | tail -30
   ```

---

### 问题3：前端显示 "Generation failed"

**症状：**
- 前端显示错误消息
- 生成过程中断

**诊断步骤：**

1. **检查浏览器控制台**
   - 打开开发者工具（F12）
   - 查看 Console 标签的错误信息

2. **检查 Network 标签**
   - 找到 `/api/v1/content/generate` 请求
   - 查看 Response 中的 `error_message` 字段

3. **检查后端日志**
   ```bash
   # 查找错误日志
   grep "ERROR\|Exception\|Traceback" logs/app.log | tail -50
   ```

**可能原因：**
- ❌ LinkedIn URL 无效或无法访问
- ❌ 后端服务异常
- ❌ 数据库连接失败
- ❌ API key 未配置

---

## 🧪 API 测试

### 测试内容生成 API

```bash
# 测试内容生成
curl -X POST http://localhost:8000/api/v1/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "linkedin_url": "https://www.linkedin.com/in/test/",
    "job_title": "ceo_founder",
    "content_quality": "advanced",
    "output_format": "with_image",
    "selected_topic": "AI trends 2025",
    "language": "en",
    "include_charts": true,
    "style_id": "modern"
  }'
```

### 测试获取结果

```bash
# 替换 {generation_id} 为实际 ID
curl http://localhost:8000/api/v1/content/{generation_id}
```

### 测试历史记录

```bash
# 获取生成历史
curl http://localhost:8000/api/v1/content/
```

---

## 📊 日志级别说明

### 后端日志级别

- **DEBUG**: 详细的调试信息（请求参数、响应数据）
- **INFO**: 一般信息（流程进度、成功消息）
- **WARNING**: 警告信息（API 未配置、回退到模拟数据）
- **ERROR**: 错误信息（API 调用失败、异常）

### 日志格式示例

```
2026-03-14 19:17:35 INFO     ✅ Novita AI API initialized, using model: gemini-2.5-flash-image
2026-03-14 19:17:35 INFO     📸 API Key prefix: tvly-dev-2...
2026-03-14 19:17:36 INFO     🎨 开始生成图片...
2026-03-14 19:17:36 INFO     📡 调用 Gemini API: https://api.novita.ai/v3/gemini-2.5-flash-image-text-to-image
2026-03-14 19:17:36 ERROR    ❌ HTTP 错误 401
2026-03-14 19:17:36 ERROR    ❌ 响应内容: {"error": "Invalid API key"}
2026-03-14 19:17:36 WARNING  🔄 回退到模拟图片
```

---

## 🔧 开发技巧

### 1. 使用 Python 脚本测试组件

```python
# test_image_gen.py
import sys
sys.path.insert(0, '/Users/wanting/program/CC/Avery/backend')

from api.services.image_generator import image_generator

# 测试图片生成
url = image_generator.generate_image(
    content="Test content",
    topic="AI trends",
    content_type="清单要点型"
)

print(f"Generated URL: {url}")
```

### 2. 使用日志文件分析

```bash
# 查看今天的所有错误
grep "$(date +%Y-%m-%d)" logs/app.log | grep ERROR

# 统计错误类型
grep ERROR logs/app.log | awk '{print $NF}' | sort | uniq -c
```

### 3. 监控数据库变化

```bash
# 实时查看新记录
watch -n 2 'psql -U avery -d avery -c "SELECT id, status, created_at FROM content_generations ORDER BY created_at DESC LIMIT 5"'
```

---

## 📞 获取帮助

如果以上方法都无法解决问题：

1. **收集诊断信息**
   - 后端日志（最近100行）
   - 浏览器控制台截图
   - 数据库记录（失败的生成）

2. **检查系统状态**
   - 后端服务是否运行
   - 数据库是否连接
   - API keys 是否有效

3. **查看文档**
   - API 文档：`http://localhost:8000/docs`
   - 数据库模型：`api/models/content.py`
   - 服务实现：`api/services/`

---

## ✅ 检查清单

生成内容前，确认以下项目：

- [ ] 后端服务正在运行（`http://localhost:8000`）
- [ ] 数据库连接正常
- [ ] `NOVITA_API_KEY` 已配置
- [ ] `TAVILY_API_KEY` 已配置
- [ ] 文本生成 API 已配置（`GROQ_API_KEY` 或 `OPENAI_API_KEY`）
- [ ] 浏览器控制台没有错误
- [ ] Network 标签显示请求成功（200）

---

**最后更新：** 2026-03-14
**版本：** 1.0
