# 📁 查看你的生成过程 - 完整指南

## 🎯 你刚才的生成记录

**基本信息：**
- **ID**: 914d4d4b-a1ef-4834-9a79-ec057f627d94
- **主题**: How Product Managers Use AI to Reconstruct Requirements Analysis
- **职位**: Product Manager
- **质量**: Professional
- **状态**: 已完成 ✅

## 📍 在哪里看过程？

### 方法1: 查看最近生成（最快）

```bash
python view_simple_history.py
```

**你会看到：**
- ✅ 完整的基本信息
- ✅ 用户输入
- ✅ 文字内容（4976字符）
- ✅ 图片信息（URL和提示词）
- ✅ 生成时间线

### 方法2: 导出完整记录（推荐）

```bash
python view_simple_history.py export 914d4d4b-a1ef-4834-9a79-ec057f627d94
```

**会创建文件：**
```
generation_exports/914d4d4b_20260315_035448.md
```

**文件包含：**
- 📋 基本信息
- 👤 用户输入
- ✍️ 完整文字内容
- 🖼️ 图片URL和提示词

### 方法3: 列出所有历史生成

```bash
python view_simple_history.py list
```

**显示最近10次生成：**
- ID、主题、职位、时间
- 内容长度
- 是否有图片

## 📊 记录中的信息详解

### 1. 基本信息
```json
{
  "ID": "914d4d4b-a1ef-4834-9a79-ec057f627d94",
  "主题": "How Product Managers Use AI to Reconstruct Requirements Analysis",
  "职位": "Product Manager",
  "质量": "Professional",
  "状态": "已完成"
}
```

### 2. 文字内容
- **长度**: 4976字符
- **类型**: 清单要点型
- **结构**:
  - Executive Summary (摘要)
  - Main Framework (5-7个战略支柱)
  - 每个支柱包含：
    - 战略框架
    - 真实案例
    - 数据支持
    - 实施指导

### 3. 图片信息
- **图片URL**: S3存储链接
- **图片提示词**: 完整的生成提示词
- **生成时间**: 2026-03-15 03:55:32

## 🔍 如何查看详细提示词？

### 当前系统中的提示词

提示词分布在以下文件中：

#### Deep Search提示词
**文件**: `api/prompts/deep_search_prompts_v2.py`
- **位置**: 第157-207行
- **内容**: 6种职位的定制查询
- **你的生成使用**: Product Manager查询
  ```
  - AI tools product development frameworks agile methodology
  - AI tools user research customer insights data-driven
  - AI tools product-market fit metrics KPIs dashboards
  - AI tools feature prioritization frameworks RICE score
  - AI tools product launch go-to-market strategy case studies
  ```

#### Research Synthesis提示词
**文件**: `api/prompts/deep_search_prompts_v2.py`
- **位置**: 第6-57行
- **内容**: RESEARCH_SYNTHESIS_PROMPT_V2
- **用途**: 将搜索结果综合为Executive级别分析

#### Content Generation提示词
**文件**: `api/prompts/content_generation_prompts_v2.py`
- **位置**: 第10-107行
- **内容**: CONTENT_QUALITY_PROMPTS_V2
- **用途**: 生成5-7个战略支柱，每个100-120字

#### Image Generation提示词
**文件**: `api/services/image_generator.py`
- **位置**: 第28-120行
- **内容**: 图片生成逻辑和prompt构建
- **用途**: 根据infographic规格生成图片

## 📝 查看具体提示词内容

### 方法1: 直接查看提示词文件

```bash
# 查看Deep Search提示词
cat api/prompts/deep_search_prompts_v2.py | grep -A 50 "DEEP_SEARCH_QUERIES_V2"

# 查看内容生成提示词
cat api/prompts/content_generation_prompts_v2.py | grep -A 50 "professional"

# 查看infographic提示词
cat api/prompts/deep_search_prompts_v2.py | grep -A 100 "INFOGRAPHIC_SPEC_PROMPT_V2"
```

### 方法2: 查看后端日志

```bash
# 查看最近生成的日志
grep "914d4d4b" logs/avery.log

# 查看提示词使用
grep "提示词\|prompt\|Prompt" logs/avery.log | tail -20
```

### 方法3: 运行端到端测试

```bash
python test_end_to_end.py
```

这会显示每一步的提示词和结果。

## 🚀 增强版记录系统（新功能）

我已经创建了一个增强版记录系统，可以自动保存每次生成的完整信息。

### 启用增强记录

需要在 `api/api/content.py` 中添加记录代码：

```python
from api.services.generation_recorder import generation_recorder

# 在生成开始时
record_id = generation_recorder.start_generation(
    generation_id=response.id,
    user_input={
        "topic": request.selected_topic,
        "job_title": request.job_title,
        "linkedin_url": request.linkedin_url,
        "company_url": request.company_url
    }
)

# 在Deep Search后
generation_recorder.save_intermediate_result(
    record_id,
    "deep_search",
    {"query_count": 5, "result_count": 15, "queries": queries}
)

# 在内容生成后
generation_recorder.save_prompt(
    record_id,
    "content_generation",
    content_prompt,
    {"model": "Llama 3.3", "tokens": 1500}
)

# 在完成后
generation_recorder.export_to_markdown(record_id)
```

## 📋 现在可以做什么

### 1. 查看你刚才的生成

```bash
python view_simple_history.py
```

### 2. 导出到文件

```bash
python view_simple_history.py export 914d4d4b-a1ef-4834-9a79-ec057f627d94
cat generation_exports/914d4d4b_20260315_035448.md
```

### 3. 查看所有历史

```bash
python view_simple_history.py list
```

## 🔧 下一步改进

如果你想要更详细的记录，我可以：

1. **启用增强记录系统**
   - 自动保存每个提示词
   - 保存所有中间结果
   - 生成完整的Markdown报告

2. **添加Web界面**
   - 在前端添加"查看详情"按钮
   - 显示生成过程的可视化时间线
   - 直接在浏览器中查看提示词

3. **创建搜索功能**
   - 按主题搜索历史生成
   - 按职位类型筛选
   - 按时间范围查询

## 💡 快速参考

| 想要 | 命令 |
|------|------|
| 查看最近生成 | `python view_simple_history.py` |
| 导出特定生成 | `python view_simple_history.py export <id>` |
| 列出所有历史 | `python view_simple_history.py list` |
| 查看提示词文件 | `cat api/prompts/*.py` |
| 查看日志记录 | `tail -100 logs/avery.log` |

---

**现在就试试：`python view_simple_history.py` 查看你刚才的生成！**
