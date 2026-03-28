# 🚀 Avery系统重构指南 - Executive级别内容生成

## 📋 重构总结

本次重构将系统从"基础内容生成"升级到"高管级别内容生成"，主要改进：

### 1. 简化输入流程 ✅
**之前：** LinkedIn URL + 公司URL + 主题 → 爬虫 + 推荐
**现在：** 职位选择 + 主题输入 + 公司网站（可选）→ 直接生成

**好处：**
- 更快速（无需等待爬虫）
- 更可靠（避免爬虫失败）
- 更直接（用户明确意图）

---

### 2. Deep Search深度升级 ✅

**之前的查询：**
```
"{topic} market size CAGR statistics"
"{topic} benchmarks key metrics"
"{topic} case study enterprise adoption"
```

**现在的查询（V2）：**
```
"{topic} strategic implications C-suite executives 2024-2025"
"{topic} market size CAGR growth projections enterprise"
"{topic} disruption case studies Fortune 500 companies"
"{topic} investment trends venture capital M&A activity"
"{topic} competitive landscape benchmark analysis leaders"
```

**根据职位定制：**
- CEO/Founder: 战略、并购、投资视角
- Marketing Leader: ROI、CAC、营销技术栈
- Product Manager: 产品框架、用户研究、PMF指标
- Sales Director: 销售方法论、配额、成交周期

---

### 3. Research Synthesis升级 ✅

**之前：** 简单摘要 + 关键洞察 + 基础数据

**现在：**
- **Market Context**（60-80字）- 市场动态和演变时间线
- **Strategic Insights**（3-5个，每个40-60字）- 非显而易见的模式
- **Critical Data Points**（5-7个）- 带行业基准的具体指标
- **Strategic Implications**（3-4个）- 对不同利益相关者的影响
- **Chart Candidates**（2-3个）- 数据丰富的可视化
- **Expert Quotes** - 专家观点和引用

---

### 4. 内容密度大幅提升 ✅

**之前的bullet points：**
- 15-25字，简单描述
- 2-3个字段 × 15-25字

**现在的bullet points（Professional级别）：**
- **60-80字**，详细且可执行
- **10-12个模块**
- 每个模块包含：
  - 可操作的洞察
  - 具体框架/方法论
  - 数据支持（百分比、基准）
  - 实际案例参考
  - 实施注意事项
  - 常见陷阱

**示例对比：**

**之前：**
```
• 建立清晰的OKR体系，确保团队目标对齐
• 定期进行1-on-1沟通，了解团队需求
• 使用数据驱动的方法优化流程
```

**现在：**
```
• **建立双层OKR体系对齐战略**（70字）
  采用Objectives and Key Results框架，将公司级OKR分解到团队级，每季度评审一次。Google使用此方法后，目标对齐度提升45%，执行速度提高35%。关键：确保每个KR都可量化，设置红黄绿三级里程碑，每月跟踪进度。避免设定过多OKR（建议3-5个），保持聚焦和可执行性。

• **实施结构化1-on-1沟通机制**（75字）
  双周1-on-1，每次45分钟，使用GROW模型（Goal-Reality-Options-Way-forward）。准备具体讨论清单，而非随意闲聊。LinkedIn数据显示，定期1-on-1的经理，团队保留率提高28%，绩效提升15%。关键：不仅谈工作，更要关注职业发展和个人障碍。建立信任的私密对话空间。

• **构建数据驱动的决策仪表盘**（68字）
  集成North Star Metric（如月度活跃用户）和15-20个关键指标，使用A/B测试验证假设。Netflix通过数据驱动决策，用户留存率提升40%。建立实时监控看板（Tableau/Mixpanel），设置自动告警阈值。关键：数据只是工具，需结合业务直觉和用户反馈。
```

---

### 5. 信息图优化 ✅

**模块数量：**
- Normal: 6-7个 → **7-8个**（增加1-2个）
- Advanced: 7-8个 → **9-10个**（增加1-2个）
- Professional: 9-10个 → **11-13个**（增加2-3个）

**每个模块内容：**
- **之前：** 15-25字
- **现在：** 30-50字 substantive content

**排版优化：**
- 更紧凑的spacing（20% white space，不是30%）
- 更大的信息密度
- 专业的颜色方案（navy/forest green）
- 清晰的typography hierarchy

---

### 6. 修复图表竖排文字bug ✅

**问题：** 图表中竖排文字导致图片生成失败

**解决方案：**
1. 在prompt中明确要求所有标签horizontal
2. 限制x轴标签长度（最多10个字符）
3. 对于长标签，使用缩写或换行
4. 优先使用bar chart（而不是pie chart，更容易处理标签）

**在prompt中添加：**
```
**Chart Constraints:**
- ALL text labels must be horizontal (never vertical or rotated)
- X-axis labels: max 10 characters, use abbreviations if needed
- Y-axis labels: max 15 characters, clear and concise
- Chart title: 8-12 words, horizontal orientation
- No text overlapping - ensure readability
```

---

## 🔧 实施步骤

### 步骤1：更新依赖和导入

在`advanced_content_generator.py`中：

```python
# 添加V2提示词导入
from api.prompts.deep_search_prompts_v2 import (
    RESEARCH_SYNTHESIS_PROMPT_V2,
    INFOGRAPHIC_SPEC_PROMPT_V2,
    get_deep_search_queries
)
from api.prompts.content_generation_prompts_v2 import CONTENT_QUALITY_PROMPTS_V2
```

### 步骤2：更新Deep Search调用

在`api/api/content.py`或创建新的简化API：

```python
# 生成专业搜索查询
queries = get_deep_search_queries(
    job_title=request.job_title.value,
    topic=request.selected_topic,
    company_info=company_info  # 可选
)

# 执行搜索
deep_search_results = deep_search_service.search(
    topic=request.selected_topic,
    queries=queries,  # 使用定制查询
    max_results_per_query=5
)
```

### 步骤3：使用V2提示词

```python
# Research Synthesis使用V2
research_summary = advanced_content_generator.synthesize_research_v2(
    topic=request.selected_topic,
    sources=deep_search_results,
    target_audience=target_audience,
    include_charts=include_charts,
    language=request.language
)

# Infographic Spec使用V2
infographic_spec = advanced_content_generator.generate_infographic_spec_v2(
    topic=request.selected_topic,
    research_summary=research_summary,
    content_quality=request.content_quality.value,
    include_charts=include_charts,
    style_id=request.style_id,
    language=request.language
)

# 内容生成使用V2
result = advanced_content_generator.generate_content_v2(
    topic=request.selected_topic,
    job_title=request.job_title.value,
    content_quality=request.content_quality.value,
    research_summary=research_summary,
    target_audience=target_audience,
    language=request.language
)
```

---

## 📊 对比示例

### 主题：AI在产品管理中的应用

**之前（普通级别）：**
```
1. AI辅助用户研究
   利用AI工具分析用户反馈，快速识别关键需求。

2. 智能需求优先级
   使用AI模型评估需求价值，优化产品路线图。

3. 自动化测试
   AI驱动的测试工具提高测试覆盖率和效率。
```

**现在（Professional级别）：**
```
1. **构建AI驱动的用户洞察引擎**（78字）
   整合NLP分析用户反馈、支持工单、应用内行为数据，每月生成用户需求报告。Microsoft使用此方法，产品迭代速度提升60%。关键：跨数据源关联分析，识别隐性需求模式。使用工具：GPT-4分析反馈、Mixpanel行为分析、Hotjar用户录音。投资：约$15K/月，ROI可见于3个月内。

2. **实施预测性需求优先级框架**（85字）
   采用RICE Score（Reach×Impact×Confidence÷Effort）+ AI预测模型，评估每个需求的潜在ROI。Intercom通过此方法，产品ROI提升45%。建立动态优先级仪表盘，每周更新。关键：结合战略目标和资源约束，避免过度优化短期指标。使用A/B测试验证优先级假设，季度调整框架。

3. **部署AI辅助原型和测试自动化**（72字）
   使用Figma AI和Galileo AI生成原型，缩短设计周期70%。结合Mabl/Testim进行AI驱动的E2E测试，覆盖率提升80%。关键：人工review AI生成内容，保持品牌一致性。实施阶段：先MVP测试（2周），再全功能部署（6周）。成本：$25K初期设置 + $8K/月。
```

---

## 🎯 质量检查清单

生成的内容必须满足：

✅ **信息密度**
- [ ] Professional级别：10-12个模块，每个60-80字
- [ ] 每个bullet都有具体数据/案例
- [ ] 没有废话或填充内容

✅ **专业性**
- [ ] 使用行业术语和框架
- [ ] 引用Fortune 500或市场领导者案例
- [ ] 包含具体数字和百分比
- [ ] 提供可执行的建议

✅ **可读性**
- [ ] 清晰的标题和结构
- [ ] 合理的段落长度
- [ ] 专业的排版
- [ ] 适合LinkedIn发布

✅ **视觉效果**
- [ ] 信息图模块11-13个（Professional）
- [ ] 图表数据丰富，无竖排文字
- [ ] 专业的颜色方案
- [ ] 清晰的层次结构

---

## 📝 新的API使用示例

### 请求格式：

```json
{
  "job_title": "ceo_founder",
  "selected_topic": "AI-Powered Business Transformation Strategies",
  "company_url": "https://www.microsoft.com",  // 可选
  "content_quality": "professional",
  "output_format": "with_image",
  "language": "en",
  "include_charts": true,
  "style_id": "executive_clean"
}
```

### 预期输出：

**内容：** 1,500-2,000字，10-12个详细bullet points
**图片：** 高密度信息图，11-13个模块，包含数据图表
**Research Summary：** 深度市场分析，3-5个战略洞察，5-7个关键数据点

---

## ⚙️ 配置文件更新

### 环境变量（无需更改）

现有配置仍然有效：
- `GROQ_API_KEY` - 用于文本生成
- `TAVILY_API_KEY` - 用于Deep Search
- `NOVITA_API_KEY` - 用于图片生成

---

## 🚀 部署步骤

1. **备份当前代码**
   ```bash
   cp api/services/advanced_content_generator.py api/services/advanced_content_generator.py.backup
   ```

2. **添加新文件**
   - `api/prompts/deep_search_prompts_v2.py`
   - `api/prompts/content_generation_prompts_v2.py`

3. **更新服务文件**
   - 修改`advanced_content_generator.py`导入V2提示词
   - 添加新方法：`synthesize_research_v2()`, `generate_infographic_spec_v2()`, `generate_content_v2()`

4. **测试新功能**
   ```bash
   # 启动后端
   ./start.sh

   # 运行测试
   ./diagnose.sh
   ```

5. **前端调整**
   - 移除LinkedIn URL输入框
   - 添加职位选择下拉菜单
   - 简化为公司网站（可选）

---

## 📚 相关文件

**新增文件：**
- `api/prompts/deep_search_prompts_v2.py` - 升级版Deep Search提示词
- `api/prompts/content_generation_prompts_v2.py` - 升级版内容生成提示词
- `REFACTOR_GUIDE.md` - 本文档

**需修改文件：**
- `api/services/advanced_content_generator.py` - 集成V2提示词
- `api/api/content.py` - 简化输入流程
- `frontend/src/app/(dashboard)/generate/page.tsx` - 简化前端输入

---

## ✅ 验证标准

### 内容质量检查：

1. **Bullet Points长度**
   - Professional: 每个bullet 60-80字 ✅
   - Advanced: 每个bullet 50-70字 ✅
   - Normal: 每个bullet 40-50字 ✅

2. **信息密度**
   - Professional: 10-12个bullets ✅
   - Advanced: 8-10个bullets ✅
   - Normal: 6-8个bullets ✅

3. **数据支持**
   - 每个bullet都有具体数字/案例 ✅
   - 包含行业基准/比较 ✅
   - 引用专家观点或研究 ✅

### 视觉质量检查：

1. **信息图模块**
   - Professional: 11-13个模块 ✅
   - Advanced: 9-10个模块 ✅
   - Normal: 7-8个模块 ✅

2. **图表质量**
   - 无竖排文字 ✅
   - 数据丰富（5-7个数据点）✅
   - 清晰的strategic narrative ✅

3. **排版**
   - 专业颜色方案 ✅
   - 清晰的层次结构 ✅
   - 合适的信息密度 ✅

---

**准备开始重构了吗？** 🚀

这是一个系统级升级，将把Avery从"基础内容生成"提升到"高管级别思想领导力内容"。

需要我协助实施这些改进吗，tiffany？
