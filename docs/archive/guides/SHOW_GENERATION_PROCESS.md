# 🎯 查看你刚才的生成过程 - 快速指南

## 📌 你刚才的生成记录

**生成时间**: 2026-03-15 03:54:48
**主题**: How Product Managers Use AI to Reconstruct Requirements Analysis
**职位**: Product Manager
**状态**: ✅ 已完成

## 📍 在哪里看？

### 最简单：查看完整记录文件

```bash
cat generation_exports/914d4d4b_20260315_035448.md
```

这会显示：
- ✅ 基本信息
- ✅ 用户输入
- ✅ **完整的文字内容（12个战略支柱）**
- ✅ **图片生成提示词（完整版）**
- ✅ 图片URL
- ✅ Infographic规格（12个模块）
- ✅ 研究摘要和数据

### 查看工具

```bash
# 查看最近生成
python view_simple_history.py

# 列出所有历史
python view_simple_history.py list
```

## 📝 每一步的提示词在哪里？

### 1. Deep Search查询（V2定制）

**位置**: `api/prompts/deep_search_prompts_v2.py`
**行数**: 第157-207行

**你使用的查询**:
```python
"product_manager": [
    "{topic} product development frameworks agile methodology",
    "{topic} user research customer insights data-driven",
    "{topic} product-market fit metrics KPIs dashboards",
    "{topic} feature prioritization frameworks RICE score",
    "{topic} product launch go-to-market strategy case studies"
]
```

### 2. Research Synthesis提示词（V2 Executive级别）

**位置**: `api/prompts/deep_search_prompts_v2.py`
**行数**: 第6-57行
**名称**: `RESEARCH_SYNTHESIS_PROMPT_V2`

**关键要求**:
- Executive级别分析
- 战略洞察（非显而易见）
- 定量数据点
- 市场背景和影响分析

### 3. 内容生成提示词（V2 Professional）

**位置**: `api/prompts/content_generation_prompts_v2.py`
**行数**: 第10-107行
**名称**: `CONTENT_QUALITY_PROMPTS_V2["清单要点型"]["professional"]`

**生成内容**:
- Executive Summary (80-100字)
- 12个战略支柱（每个100-120字）
- 每个包含：框架、案例、数据、实施步骤

### 4. 图片生成提示词

**位置**: `api/services/image_generator.py`
**行数**: 第28-120行

**完整提示词已保存**: 见导出文件第60行

**包含**:
- Infographic规格（12个模块）
- 布局和样式要求
- 图表数据
- 颜色主题

## 🎨 快速查看方法

### 方法1: 查看导出文件（推荐）

```bash
# 打开导出文件
cat generation_exports/914d4d4b_20260315_035448.md

# 或在编辑器中打开
open generation_exports/914d4d4b_20260315_035448.md
```

### 方法2: 查看提示词文件

```bash
# Deep Search提示词
cat api/prompts/deep_search_prompts_v2.py | grep -A 50 "product_manager"

# 内容生成提示词
cat api/prompts/content_generation_prompts_v2.py | grep -A 80 "professional.*\"\"\""
```

### 方法3: 查看后端日志

```bash
# 查看生成过程的日志
grep "914d4d4b" logs/avery.log

# 查看图片生成过程
grep "图片生成\|Novita\|Gemini" logs/avery.log | tail -10
```

## 🔍 提示词详细内容

### Deep Search查询（Product Manager视角）

1. **AI tools product development frameworks agile methodology**
2. **AI tools user research customer insights data-driven**
3. **AI tools product-market fit metrics KPIs dashboards**
4. **AI tools feature prioritization frameworks RICE score**
5. **AI tools product launch go-to-market strategy case studies**

### Research Synthesis要点

- Executive级别分析（非表面信息）
- 深刻洞察（strategic insights）
- 定量数据（key numbers with context）
- 战略影响（implications for stakeholders）

### 内容生成结果（12个战略支柱）

1. AI-Powered Requirements Gathering
2. Machine Learning for Prioritization
3. Predictive Analytics for Forecasting
4. Collaborative Filtering for Requirement Validation
5. Natural Language Generation for Documentation
6. Deep Learning for Sentiment Analysis
7. Topic Modeling for Requirement Clustering
8. Recommendation Systems for Personalization
9. Transfer Learning for Requirement Analysis
10. Explainable AI for Transparency
11. Human-Centered Design for Requirement Validation
12. Continuous Integration for Requirement Refinement

**每个支柱包含**:
- 战略框架/方法
- 真实案例（Amazon, Google, Microsoft等）
- 量化数据（20% improvement, $100K investment等）
- 实施时间线和资源需求
- 风险和注意事项

### 图片生成规格

**12个模块**:
1. AI-Powered Product Discovery
2. Market Context and Trends
3. Strategic Insights for Product Managers
4. Key Numbers and Metrics
5. Strategic Implications for Business Leaders
6. AI Adoption Rate and Trends
7. Revenue Growth and ROI
8. Customer Experience and Satisfaction
9. Product Management Workflow Optimization
10. Best Practices for AI Adoption
11. AI-Powered Product Management Tools
12. Future of Product Management

**图表**: AI Adoption Rate and Revenue Growth (line chart)

## 💡 下次生成时

如果你想看到下次生成的完整过程：

1. **前端**: 观察进度界面（实时步骤）
2. **后端**: 运行 `./monitor-logs.sh`（详细日志）
3. **生成后**: 运行 `python view_simple_history.py`（查看详情）
4. **导出**: 运行 `python view_simple_history.py export <id>`（保存到文件）

## 📚 提示词文件对应表

| 生成步骤 | 提示词文件 | 具体位置 | 名称 |
|---------|-----------|----------|------|
| Deep Search | `deep_search_prompts_v2.py` | 第157-207行 | DEEP_SEARCH_QUERIES_V2 |
| Research Synthesis | `deep_search_prompts_v2.py` | 第6-57行 | RESEARCH_SYNTHESIS_PROMPT_V2 |
| Content Generation | `content_generation_prompts_v2.py` | 第10-107行 | CONTENT_QUALITY_PROMPTS_V2 |
| Image Generation | `image_generator.py` | 第28-120行 | generate_image()方法 |

---

**现在就试试查看你刚才的生成记录：**
```bash
cat generation_exports/914d4d4b_20260315_035448.md
```

**你会看到完整的生成过程，包括每一步的提示词和结果！**
