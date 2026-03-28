# 🔍 查看生图过程的完整指南

## 📱 前端界面（最直观）

### 生成过程中的实时显示

当你在前端点击"Start Generating"后，会看到一个进度界面：

```
🔄 AI is generating content...
Estimated time: 1-2 minutes

[████████████░░░░░░░░] 60%

Progress: 60%
Current step: Deep Search

✓ Validate Input
✓ Extract Data
✓ Recommend Topics
✓ Analyze Structure
⟳ Deep Search           ← 当前正在进行的步骤
  Synthesize Research
  Infographic Spec
  Generate Content
  Visual Design
  Generate Image
  Complete
```

**关键信息显示：**
- 📊 **进度条**: 显示总体完成百分比
- 📝 **当前步骤**: 显示正在执行的具体步骤
- ✅ **已完成步骤**: 绿色勾号标记
- ⟳ **进行中步骤**: 旋转图标标记

**步骤说明：**
1. **Validate Input** - 验证输入参数
2. **Extract Data** - 提取LinkedIn/公司数据
3. **Recommend Topics** - 推荐内容主题
4. **Analyze Structure** - 分析内容结构
5. **Deep Search** - 深度搜索研究数据
6. **Synthesize Research** - 综合研究成果
7. **Infographic Spec** - 生成信息图规格
8. **Generate Content** - 生成文字内容
9. **Visual Design** - 视觉设计规划
10. **Generate Image** - 生成最终图片
11. **Complete** - 完成

**文件位置：** `frontend/src/app/(dashboard)/generate/page.tsx` (第691-744行)

---

## 💻 后端日志（最详细）

### 方法1: 实时监控脚本（推荐）

```bash
# 在backend目录下运行
./monitor-logs.sh
```

**显示内容：**
```
🎨 2026-03-15 11:30:15 | INFO | 开始内容生成流程
📡 2026-03-15 11:30:15 | INFO | 使用V2定制查询进行Deep Search
📊 2026-03-15 11:30:16 | INFO | Deep Search获得15个结果
📊 2026-03-15 11:30:17 | INFO | 使用V2升级版Research Synthesis
🎨 2026-03-15 11:30:18 | INFO | 生成infographic规格: 12个模块
📡 2026-03-15 11:30:19 | INFO | 使用V2升级版生成文字内容
🎨 2026-03-15 11:30:20 | INFO | 开始调用图片生成API
📡 2026-03-15 11:30:20 | INFO | 调用 Gemini API
✅ 2026-03-15 11:30:22 | INFO | Gemini 图片生成成功
✅ 2026-03-15 11:30:23 | INFO | 内容生成流程完成
```

**特点：**
- ✅ 实时显示
- ✅ emoji标记便于识别
- ✅ 自动过滤关键信息
- ✅ 高亮重要步骤

### 方法2: 使用view-logs.sh脚本

```bash
# 实时跟踪所有日志
./view-logs.sh -f

# 只看错误
./view-logs.sh -e -f

# 搜索特定关键词
./view-logs.sh -s "image" -f
```

### 方法3: 直接使用tail命令

```bash
# 实时查看完整日志
tail -f logs/avery.log

# 只看图片生成相关
tail -f logs/avery.log | grep -E "image|Image|🎨"

# 只看API调用
tail -f logs/avery.log | grep -E "POST|GET|200|404"
```

---

## 🌐 浏览器API日志

### 方法1: 访问日志端点

在浏览器中打开：
```
http://localhost:8000/logs
```

**显示内容：**
- 完整的后端日志
- 支持搜索和过滤
- 可以下载日志文件

### 方法2: 浏览器开发者工具

1. 打开前端页面
2. 按 `F12` 或 `右键 → 检查`
3. 切换到 `Network` 标签
4. 点击"Start Generating"
5. 查看API请求和响应：

```
POST /api/content/extract-and-recommend
Status: 200 OK
Duration: 2.3s

POST /api/content/generate
Status: 200 OK
Duration: 45.2s

GET /api/content/{id}
Status: 200 OK
Response: {
  "status": "completed",
  "progress": 100,
  "generated_content": "...",
  "image_url": "..."
}
```

---

## 📊 详细过程分解

### 步骤1: 用户输入 → 提取数据

**前端显示：**
```
Validating Input...
Extracting Data...
```

**后端日志：**
```
INFO | 开始提取数据和推荐主题
INFO | 使用V2定制查询进行Deep Search
INFO | Deep Search获得15个结果
```

**查看位置：**
- 前端：进度界面
- 后端：`logs/avery.log` 或 `./monitor-logs.sh`

---

### 步骤2: 主题推荐

**前端显示：**
```
Recommending Topics...
```

**后端日志：**
```
INFO | 生成主题推荐...
INFO | 生成了 4 个主题推荐
```

**对应文件：**
- 前端：`frontend/src/app/(dashboard)/generate/page.tsx:95-111`
- 后端：`api/api/content.py:70-118`

---

### 步骤3: Deep Search（深度搜索）

**前端显示：**
```
Deep Search...
```

**后端日志：**
```
INFO | 使用 5 个专业深度查询
INFO | 使用提供的 5 个定制查询
INFO | 获得 15 个高质量搜索结果
```

**查询内容：**
```
1. AI tools strategic implications C-suite executives 2024-2025
2. AI tools market size CAGR growth projections enterprise
3. AI tools disruption case studies Fortune 500 companies
4. AI tools investment trends venture capital M&A activity
5. AI tools competitive landscape benchmark analysis leaders
```

**对应文件：**
- 查询生成：`api/prompts/deep_search_prompts_v2.py:157-207`
- 搜索执行：`api/services/deep_search.py:61-125`

---

### 步骤4: Research Synthesis（研究综合）

**前端显示：**
```
Synthesizing Research...
```

**后端日志：**
```
INFO | 使用V2升级版Research Synthesis（Executive级别）
INFO | Research Synthesis完成: {
  "summary": "CEOs are leveraging AI tools...",
  "market_context": "Enterprise AI market growing at 19% CAGR...",
  "strategic_insights": [...],
  "key_numbers": [...]
}
```

**对应文件：**
- 执行：`api/services/advanced_content_generator.py:856-935`
- 提示词：`api/prompts/deep_search_prompts_v2.py:6-57`

---

### 步骤5: Infographic Spec（信息图规格）

**前端显示：**
```
Generating Infographic Spec...
```

**后端日志：**
```
INFO | 使用V2升级版生成信息图规格
INFO | Infographic规格生成: 12个模块
```

**规格内容：**
```json
{
  "title": "AI-Driven Decision Making for CEOs",
  "modules": [
    {
      "id": "A-01",
      "title": "AI Adoption and Governance",
      "content": "30-50 words of substantive content...",
      "bullets": ["3-5 key takeaways"],
      "data_point": "77% believe GenAI underhyped"
    }
    // ... 共12个模块
  ]
}
```

**对应文件：**
- 执行：`api/services/advanced_content_generator.py:937-1030`
- 提示词：`api/prompts/deep_search_prompts_v2.py:60-153`

---

### 步骤6: Content Generation（内容生成）

**前端显示：**
```
Generating Content...
```

**后端日志：**
```
INFO | 使用V2升级版生成文字内容（Executive级别）
INFO | 使用V2升级版生成内容 - 主题: AI tools, 质量: professional
INFO | 内容生成完成: {
  "content": "**Executive Summary**\n\nAs CEOs navigate...",
  "content_type": "清单要点型"
}
```

**生成内容结构：**
```
**Executive Summary** (439字符)
- 80-100字总结

**Main Framework** (4372字符)
- 5-7个战略支柱
- 每个支柱100-120字
- 包含框架、案例、数据、实施步骤
```

**对应文件：**
- 执行：`api/services/advanced_content_generator.py:81-200`
- 提示词：`api/prompts/content_generation_prompts_v2.py:10-107`

---

### 步骤7: Image Generation（图片生成）

**前端显示：**
```
Generating Image...
```

**后端日志：**
```
INFO | 开始调用图片生成API
INFO | 调用 Gemini API
INFO | 生成参数: model="gemini-2.0-flash-exp"
INFO | Gemini 图片生成成功: https://novita-img...
INFO | 保存图片URL到数据库
```

**生成过程：**
```
📡 调用 Novita AI API
   URL: https://api.novita.ai/v1/images/generations
   Model: gemini-2.0-flash-exp

🎨 处理infographic规格
   模块数量: 12
   布局: 2-column
   样式: executive_clean

✅ 图片生成成功
   URL: https://novita-img.com/...
   格式: JPG
   尺寸: 800x600
```

**对应文件：**
- 执行：`api/services/image_generator.py:28-120`
- API调用：`Novita AI API`

---

## 🎯 快速查看不同信息

### 查看搜索查询
```bash
grep "定制查询\|custom queries" logs/avery.log | tail -5
```

### 查看搜索结果数量
```bash
grep "获得.*结果\|search results" logs/avery.log | tail -3
```

### 查看研究摘要
```bash
grep -A 10 "Research Synthesis完成" logs/avery.log | tail -15
```

### 查看内容长度
```bash
grep "内容生成完成\|Content generation" logs/avery.log | tail -3
```

### 查看图片URL
```bash
grep "图片生成成功\|image URL" logs/avery.log | tail -3
```

---

## 🚨 错误诊断

### 如果生成失败

**1. 查看错误信息**
```bash
grep "ERROR\|❌\|失败" logs/avery.log | tail -20
```

**2. 查看完整上下文**
```bash
grep -B 5 -A 5 "ERROR" logs/avery.log | tail -30
```

**3. 查看特定步骤**
```bash
# Deep Search问题
grep "Deep Search\|Tavily" logs/avery.log | tail -10

# 内容生成问题
grep "内容生成\|Groq\|LLM" logs/avery.log | tail -10

# 图片生成问题
grep "图片生成\|Novita\|Gemini" logs/avery.log | tail -10
```

---

## 💡 推荐的查看流程

### 开发调试时：

**终端1（启动后端）：**
```bash
./start.sh
```

**终端2（监控日志）：**
```bash
./monitor-logs.sh
```

**浏览器（前端操作）：**
1. 打开 `http://localhost:3000/generate`
2. 填写表单
3. 点击"Start Generating"
4. 观察前端进度界面
5. 在终端2查看详细日志

---

### 生产环境：

```bash
# 后台启动
./start-background.sh

# 定期查看日志
tail -f logs/avery.log

# 搜索错误
grep ERROR logs/avery.log
```

---

## 📊 信息查看对比表

| 查看方式 | 详细程度 | 实时性 | 主要用途 |
|---------|---------|--------|----------|
| **前端进度** | ⭐⭐ | ⭐⭐⭐ | 用户界面，总体进度 |
| **monitor-logs.sh** | ⭐⭐⭐ | ⭐⭐⭐ | 开发调试，推荐 |
| **view-logs.sh** | ⭐⭐⭐⭐ | ⭐⭐⭐ | 详细日志分析 |
| **tail -f** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 最详细的实时查看 |
| **浏览器 /logs** | ⭐⭐⭐⭐ | ⭐ | 历史日志查看 |
| **Network标签** | ⭐⭐⭐ | ⭐⭐ | API请求调试 |

---

## 🎁 快速参考卡片

### 立即查看生成过程：

**最简单（前端）：**
- 打开 `http://localhost:3000/generate`
- 点击"Start Generating"
- 观察进度界面

**最详细（推荐）：**
```bash
./monitor-logs.sh
```

**最灵活：**
```bash
tail -f logs/avery.log | grep "🎨\|📡\|✅"
```

**快速诊断：**
```bash
grep "ERROR\|❌" logs/avery.log | tail -10
```

---

**选择最适合你的方式，随时查看生成过程！**
