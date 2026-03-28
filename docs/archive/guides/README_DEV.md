# Avery Content Generation - 开发指南

## 🚀 快速启动

### 1. 启动后端服务

```bash
cd /Users/wanting/program/CC/Avery/backend

# 方式1：使用启动脚本（推荐）
./start.sh

# 方式2：手动启动
source venv/bin/activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 诊断系统状态

```bash
# 运行完整诊断
./diagnose.sh
```

### 3. 访问服务

- 🌐 **API 文档**: http://localhost:8000/docs
- 📚 **调试指南**: [DEBUG_GUIDE.md](DEBUG_GUIDE.md)
- 🔍 **API Root**: http://localhost:8000/

---

## 📁 脚本说明

### `start.sh` - 启动后端服务

**功能：**
- ✓ 自动激活虚拟环境
- ✓ 检查端口占用
- ✓ 显示启动信息
- ✓ 设置环境变量
- ✓ 启动 uvicorn 服务器

**使用：**
```bash
./start.sh
```

**输出示例：**
```
✓ 已激活虚拟环境

=== Avery Content Generation - 后端启动 ===

📡 启动信息:
   虚拟环境: /Users/wanting/program/CC/Avery/backend/venv
   Python: /Users/wanting/program/CC/Avery/backend/venv/bin/python
   版本: Python 3.12.2
   ...

🌐 服务地址:
   API: http://localhost:8000
   文档: http://localhost:8000/docs
```

### `diagnose.sh` - 系统诊断

**功能：**
- ✓ 检查后端服务状态
- ✓ 测试数据库连接
- ✓ 验证 API 配置
- ✓ 测试 Tavily API 连接
- ✓ 显示最近生成记录
- ✓ 测试 Deep Search 流程

**使用：**
```bash
./diagnose.sh
```

**诊断项目：**
1. 后端服务运行状态
2. 数据库连接
3. API 配置（Novita、Tavily、Groq/OpenAI）
4. API 连接测试
5. 生成记录查看
6. Deep Search + Research Synthesis 测试

---

## 🔧 常用命令

### 激活虚拟环境

```bash
# 方式1：使用脚本
source venv/bin/activate

# 方式2：在脚本中自动激活（推荐）
./start.sh  # 自动激活
./diagnose.sh  # 自动激活
```

### 检查 Python 环境

```bash
# 检查当前使用的 Python
which python

# 检查 Python 版本
python --version

# 检查已安装的包
pip list | grep -E "fastapi|uvicorn|pydantic"
```

### 查看后端日志

```bash
# 如果使用日志文件
tail -f logs/app.log

# 过滤错误日志
grep ERROR logs/app.log | tail -50

# 查看图片生成相关日志
grep -E "图片|Image|Gemini|Novita" logs/app.log | tail -30
```

### 数据库操作

```bash
# 连接数据库
psql -U avery -d avery -h localhost

# 查看最近的生成记录
psql -U avery -d avery -c "SELECT id, status, selected_topic, created_at FROM content_generations ORDER BY created_at DESC LIMIT 10;"

# 查看失败的记录
psql -U avery -d avery -c "SELECT id, selected_topic, error_message FROM content_generations WHERE status = 'failed' ORDER BY created_at DESC LIMIT 5;"
```

---

## 🐛 调试步骤

### 问题：生图失败

**步骤1：运行诊断**
```bash
./diagnose.sh
```

**步骤2：检查后端日志**
```bash
# 查看实时日志
./start.sh  # 观察启动和运行日志

# 或查看日志文件
tail -f logs/app.log
```

**步骤3：检查浏览器**
- 打开开发者工具（F12）
- 查看 Console 标签的错误信息
- 查看 Network 标签的 API 响应

**步骤4：检查数据库记录**
```bash
python << 'EOF'
from api.db.database import SessionLocal
from api.models.content import ContentGeneration

db = SessionLocal()
failed = db.query(ContentGeneration).filter(
    ContentGeneration.status == 'failed'
).order_by(ContentGeneration.created_at.desc()).first()

if failed:
    print(f"失败主题: {failed.selected_topic}")
    print(f"错误信息: {failed.error_message}")

db.close()
EOF
```

---

## 📊 最近的修复

### 2026-03-15：修复 Deep Search Prompt 格式化问题

**问题：**
- Research Synthesis 失败，错误：`KeyError: '\n  "summary"'`
- 原因：Prompt 中的 JSON schema 使用了 `{}`，被 `.format()` 误解析

**修复：**
- 修改 `api/prompts/deep_search_prompts.py`
- 将 JSON schema 中的 `{}` 转义为 `{{}}`

**影响：**
- ✅ Deep Search 现在可以正常工作
- ✅ Research Synthesis 可以生成研究摘要
- ✅ Infographic Spec 可以正常生成

**验证：**
```bash
./diagnose.sh  # 运行诊断，查看测试结果
```

---

## 🔄 重新生成内容

由于之前的生成可能受到 bug 影响，建议重新生成：

1. **清理旧数据（可选）**
```bash
# 删除失败的记录
psql -U avery -d avery -c "DELETE FROM content_generations WHERE status = 'failed';"
```

2. **在前端重新生成**
- 打开前端页面
- 选择相同的主题和参数
- 点击生成

3. **观察日志**
```bash
# 在另一个终端窗口运行
./start.sh

# 观察图片生成的详细日志
```

---

## 📝 环境配置

### 必需的 API Keys

在 `.env` 文件中配置：

```bash
# 图片生成（必需）
NOVITA_API_KEY=sk_...

# Deep Search（必需）
TAVILY_API_KEY=tvly-dev-...

# 文本生成（必需，选择一个）
GROQ_API_KEY=gsk_...        # 推荐（免费）
OPENAI_API_KEY=sk-...       # 或使用 OpenAI
ZHIPU_API_KEY=...           # 或使用智谱 AI
```

### 数据库配置

```bash
DATABASE_URL=postgresql://avery:avery_dev_password@localhost:5432/avery
REDIS_URL=redis://localhost:6379/0
```

---

## 🎯 下一步

1. **验证修复**：运行 `./diagnose.sh` 确认所有组件正常
2. **重新生成**：在前端重新生成之前失败的内容
3. **观察日志**：使用 `./start.sh` 启动后端，观察详细的日志输出
4. **查看文档**：访问 http://localhost:8000/docs 查看 API 文档

---

## 📞 获取帮助

如果遇到问题：

1. **查看调试指南**：`cat DEBUG_GUIDE.md`
2. **运行诊断**：`./diagnose.sh`
3. **查看日志**：观察 `./start.sh` 的输出
4. **检查数据库**：查看生成记录和错误信息

---

**最后更新**：2026-03-15
**维护者**：送送 🤖
