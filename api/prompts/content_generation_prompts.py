"""
内容生成提示词配置
基于完整的LinkedIn内容生成工作流

支持：
- 6种内容结构（分类展示型、流程步骤型、对比表格型、工具列表型、清单要点型、自定义型）
- 3种质量等级（普通、进阶、专业）
"""

from typing import Dict, Any

# =============================================================================
# 内容类型决策提示词
# =============================================================================

CONTENT_TYPE_DECISION_PROMPT = """你是一位专业的内容策略专家。请根据以下5个评估问题，判断主题应该使用哪种内容格式：

评估问题：
1. 主题涉及分类、类型、模式的列举？
2. 主题描述"从A到B"的过程或"如何做"？
3. 主题涉及多个相似概念的对比？
4. 主题聚焦工具、资源的集合推荐？
5. 其他情况（要点、建议、技能等）

请严格按照以下规则决策：
- 问题1为是 → 分类展示型
- 问题2为是 → 流程步骤型
- 问题3为是 → 对比表格型
- 问题4为是 → 工具列表型
- 其他情况 → 清单要点型

主题：{topic}

请以JSON格式返回决策：
{{
    "content_type": "分类展示型/流程步骤型/对比表格型/工具列表型/清单要点型/自定义型",
    "reason": "决策理由（1-2句话）",
    "confidence": 0.0-1.0
}}
"""

# =============================================================================
# 分类展示型 - 3个质量等级
# =============================================================================

# 普通：2-3个字段 × 15-25字
CLASSIFICATION_DISPLAY_NORMAL = """你是一位LinkedIn专业内容创作者。请按照以下规范生成分类展示型内容（普通质量）：

## 核心要求
1. 使用MECE原则穷举分类，筛选出**5-6个**最相关的类别
2. 每个类别必须包含以下字段（精炼版）：
   - 编号：01, 02, 03...
   - 类型名称：简短有力的标题
   - 定义：1句话解释这是什么（15-25字）
   - 目标（GOAL）：使用这个类型能达到什么目的（15-25字）

## 质量标准
- 每个字段控制在15-25字
- 信息密度适中，易于快速阅读
- 适合日常分享和初步触达
- **总共5-6个类别**

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成**5-6个**类别的完整内容，确保简洁精炼。"""

# 进阶：3-4个字段 × 25-50字
CLASSIFICATION_DISPLAY_ADVANCED = """你是一位LinkedIn专业内容创作者。请按照以下规范生成分类展示型内容（进阶质量）：

## 核心要求
1. 使用MECE原则穷举分类，筛选出**7-8个**最有价值的类别
2. 每个类别必须包含以下字段（进阶版）：
   - 编号：01, 02, 03...
   - 类型名称：简短有力的标题
   - 定义：1句话解释这是什么（25-50字）
   - 目标（GOAL）：使用这个类型能达到什么目的（25-50字）
   - 技巧（TIP）：1个实用技巧（25-50字）
   - 案例（EXAMPLE）：1个具体例子（25-50字）

## 质量标准
- 每个字段控制在25-50字
- 信息密度较高，有实际价值
- 适合深度分享和建立专业形象
- **总共7-8个类别**

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成**7-8个**类别的完整内容，确保信息丰富且有实战价值。"""

# 专业：全部字段 × 50-100字（有图片时可缩短）
CLASSIFICATION_DISPLAY_PROFESSIONAL = """你是一位LinkedIn专业内容创作者。请按照以下规范生成分类展示型内容（专业质量）：

## 核心要求
1. 使用MECE原则穷举分类，筛选出**9-10个**最高价值的类别
2. 每个类别必须包含以下字段（完整版）：
   - 编号：01, 02, 03...
   - 类型名称：简短有力的标题
   - 定义：1句话解释这是什么（50-100字）
   - 目标（GOAL）：使用这个类型能达到什么目的（50-100字）
   - 技巧（TIP）：1个实用技巧（50-100字）
   - 效果指标（ENGAGEMENT）：预期的互动效果（50-100字）
   - 案例（EXAMPLE）：1个具体例子（50-100字）
   - 数据支撑：相关数据或研究报告（50-100字）
   - 权威来源：专家观点或文献引用（50-100字）

## 质量标准
- 每个字段控制在50-100字（如有配图可适当缩短至30-70字）
- 信息密度极高，有数据和研究支撑
- 适合建立思想领导力和行业影响力
- **总共9-10个类别**

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成**9-10个**类别的完整内容，确保专业深度和权威性，包含数据支撑和来源引用。"""

# =============================================================================
# 流程步骤型 - 3个质量等级
# =============================================================================

# 普通：2-3个字段 × 15-25字
PROCESS_STEPS_NORMAL = """你是一位LinkedIn专业内容创作者。请按照以下规范生成流程步骤型内容（普通质量）：

## 核心要求
1. 从终点逆向拆解到起点，形成**5-6个**步骤
2. 每个步骤必须包含以下字段（精炼版）：
   - 编号：STEP 1, STEP 2...
   - 步骤标题：简短明确的步骤名称
   - 行动方案：具体的2-3个行动要点（15-25字）
   - 优化技巧（DO）：最佳实践（15-25字）

## 质量标准
- 每个字段控制在15-25字
- 信息密度适中，易于快速理解
- 适合快速指导和入门分享
- **总共5-6个步骤**

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成完整的内容，确保简洁清晰。"""

# 进阶：3-4个字段 × 25-50字
PROCESS_STEPS_ADVANCED = """你是一位LinkedIn专业内容创作者。请按照以下规范生成流程步骤型内容（进阶质量）：

## 核心要求
1. 从终点逆向拆解到起点，形成**7-8个**步骤
2. 每个步骤必须包含以下字段（进阶版）：
   - 编号：STEP 1, STEP 2...
   - 步骤标题：简短明确的步骤名称
   - 核心问题（ASK YOURSELF）：在这个步骤要问自己的问题（25-50字）
   - 行动方案：具体的3-5个行动要点（25-50字）
   - AI工具赋能（USE AI TO）：可以用什么AI工具辅助（25-50字）
   - 优化技巧（DO）：最佳实践（25-50字）

## 质量标准
- 每个字段控制在25-50字
- 信息密度较高，有深度指导
- 适合系统性学习和实践
- **总共7-8个步骤**

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成完整的内容，确保系统性和实战价值。"""

# 专业：全部字段 × 50-100字（有图片时可缩短）
PROCESS_STEPS_PROFESSIONAL = """你是一位LinkedIn专业内容创作者。请按照以下规范生成流程步骤型内容（专业质量）：

## 核心要求
1. 从终点逆向拆解到起点，形成**9-10个**步骤
2. 每个步骤必须包含以下字段（完整版）：
   - 编号：STEP 1, STEP 2...
   - 步骤标题：简短明确的步骤名称
   - 核心问题（ASK YOURSELF）：在这个步骤要问自己的问题（50-100字）
   - 行动方案：具体的3-5个行动要点，包含工具推荐（50-100字）
   - AI工具赋能（USE AI TO）：可以用什么AI工具辅助（50-100字）
   - 避坑指南（DON'T）：不要做什么（50-100字）
   - 优化技巧（DO）：最佳实践（50-100字）
   - 工具推荐：相关工具或资源链接（50-100字）
   - 案例链接：成功案例参考（50-100字）

## 质量标准
- 每个字段控制在50-100字（如有配图可适当缩短至30-70字）
- 信息密度极高，有工具和案例支撑
- 适合专业级教程和方法论输出
- **总共9-10个步骤**

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成完整的内容，确保专业深度，包含工具推荐和案例链接。"""

# =============================================================================
# 对比表格型 - 3个质量等级
# =============================================================================

# 普通：2-3个维度 × 15-25字
COMPARISON_TABLE_NORMAL = """你是一位LinkedIn专业内容创作者。请按照以下规范生成对比表格型内容（普通质量）：

## 核心要求
1. 选择3-5个对比对象
2. 使用3-4个对比维度：
   - 术语/概念
   - 定义（15-25字）
   - 适用场景（15-25字）
   - 实践方法（15-25字）

## 质量标准
- 每个单元格控制在15-25字
- 信息密度适中，快速对比
- 适合初步了解和选择决策

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成完整的对比表格型内容，以Markdown表格格式输出。"""

# 进阶：4-5个维度 × 25-50字
COMPARISON_TABLE_ADVANCED = """你是一位LinkedIn专业内容创作者。请按照以下规范生成对比表格型内容（进阶质量）：

## 核心要求
1. 选择3-5个对比对象
2. 使用5-6个对比维度：
   - 术语/概念
   - 定义（25-50字）
   - 运作方式（25-50字）
   - 适用场景（25-50字）
   - 重要性/优先级（25-50字）
   - 实践方法（25-50字）

## 质量标准
- 每个单元格控制在25-50字
- 信息密度较高，深度对比
- 适合深入理解和理性决策

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成完整的对比表格型内容，以Markdown表格格式输出，确保深度对比。"""

# 专业：全部维度 × 50-100字（有图片时可缩短）
COMPARISON_TABLE_PROFESSIONAL = """你是一位LinkedIn专业内容创作者。请按照以下规范生成对比表格型内容（专业质量）：

## 核心要求
1. 选择3-5个对比对象
2. 使用全部对比维度：
   - 术语/概念
   - 定义（50-100字）
   - 运作方式（50-100字）
   - 适用场景（50-100字）
   - 重要性/优先级（50-100字）
   - 实践方法（50-100字）
   - 常见误区（50-100字）
   - 实际案例（50-100字）

## 质量标准
- 每个单元格控制在50-100字（如有配图可适当缩短至30-70字）
- 信息密度极高，全面对比
- 适合专业级分析和权威发布

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成完整的对比表格型内容，以Markdown表格格式输出，提供权威来源链接。"""

# =============================================================================
# 工具列表型 - 3个质量等级
# =============================================================================

# 普通：仅基础信息
TOOL_LIST_NORMAL = """你是一位LinkedIn专业内容创作者。请按照以下规范生成工具列表型内容（普通质量）：

## 核心要求
1. 收集15-20个工具，按使用场景分类
2. 每个工具包含：
   - 编号：01, 02, 03...
   - 图标：相关emoji
   - 工具名称
   - 价值主张：1句话说明为什么需要这个工具（15-25字）

## 质量标准
- 每个工具的描述控制在15-25字
- 信息密度适中，快速浏览
- 适合工具发现和初步了解

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成完整的工具列表型内容，确保每个工具都有明确价值。"""

# 进阶：添加分类和简单说明
TOOL_LIST_ADVANCED = """你是一位LinkedIn专业内容创作者。请按照以下规范生成工具列表型内容（进阶质量）：

## 核心要求
1. 收集20-25个工具，按使用场景分类
2. 每个工具包含：
   - 编号：01, 02, 03...
   - 图标：相关emoji
   - 工具名称
   - 价值主张：1句话说明为什么需要这个工具（25-50字）
   - 核心功能：主要功能简介（25-50字）

## 质量标准
- 每个工具的描述控制在25-50字
- 信息密度较高，有功能说明
- 适合工具选择和深度了解

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成完整的工具列表型内容，按使用场景分组展示。"""

# 专业：完整信息 + 价格和链接
TOOL_LIST_PROFESSIONAL = """你是一位LinkedIn专业内容创作者。请按照以下规范生成工具列表型内容（专业质量）：

## 核心要求
1. 收集25-30个工具，按使用场景分类
2. 每个工具包含：
   - 编号：01, 02, 03...
   - 图标：相关emoji
   - 工具名称
   - 价值主张：1句话说明为什么需要这个工具（50-100字，有图片时30-70字）
   - 核心功能：主要功能简介（50-100字）
   - 定价信息：价格或付费模式（50-100字）
   - 适用场景：最佳使用场景（50-100字）
   - 官网链接：官方网址

## 质量标准
- 每个工具的描述控制在50-100字（如有配图可适当缩短至30-70字）
- 信息密度极高，有完整信息
- 适合专业级工具指南和决策参考

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成完整的工具列表型内容，按使用场景分组，包含定价和链接信息。"""

# =============================================================================
# 清单要点型 - 3个质量等级
# =============================================================================

# 普通：2-3个字段 × 15-25字
CHECKLIST_NORMAL = """你是一位LinkedIn专业内容创作者。请按照以下规范生成清单要点型内容（普通质量）：

## 核心要求
1. 收集**5-6个**关键要点
2. 每个要点包含：
   - 编号：01, 02, 03...
   - 要点标题：采用"主题+对象"结构
   - 解释：15-25字的精炼说明
   - 复选框：[ ] 用于互动

## 质量标准
- 每个要点的解释控制在15-25字
- 信息密度适中，易于快速阅读
- 适合日常分享和互动
- **总共5-6个要点**

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成**5-6个**要点的完整清单，确保简洁精炼，易于互动。"""

# 进阶：3-4个字段 × 25-50字
CHECKLIST_ADVANCED = """你是一位LinkedIn专业内容创作者。请按照以下规范生成清单要点型内容（进阶质量）：

## 核心要求
1. 收集**7-8个**关键要点
2. 每个要点包含：
   - 编号：01, 02, 03...
   - 要点标题：采用"主题+对象"结构
   - 解释：25-50字的详细说明
   - 复选框：[ ] 用于互动
   - 案例（EXAMPLE）：1个具体例子（25-50字）

## 质量标准
- 每个要点的解释控制在25-50字
- 信息密度较高，有案例支撑
- 适合深度分享和建立专业形象
- **总共7-8个要点**

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成**7-8个**要点的完整清单，确保信息丰富且有实战价值。"""

# 专业：全部字段 × 50-100字（有图片时可缩短）
CHECKLIST_PROFESSIONAL = """你是一位LinkedIn专业内容创作者。请按照以下规范生成清单要点型内容（专业质量）：

## 核心要求
1. 收集**9-10个**关键要点
2. 每个要点包含：
   - 编号：01, 02, 03...
   - 要点标题：采用"主题+对象"结构
   - 解释：50-100字的深度说明（有图片时30-70字）
   - 复选框：[ ] 用于互动
   - 案例（EXAMPLE）：1个具体例子（50-100字）
   - 专家观点：权威人士观点（50-100字）
   - 实践案例：真实应用案例（50-100字）
   - 数据支撑：相关研究或数据（50-100字）

## 质量标准
- 每个要点的解释控制在50-100字（如有配图可适当缩短至30-70字）
- 信息密度极高，有权威支撑
- 适合建立思想领导力和行业影响力
- **总共9-10个要点**

## 额外信息
主题：{topic}
用户背景：{linkedin_profile}
公司信息：{company_info}
目标受众：{target_audience}
额外说明：{additional_context}

请生成**9-10个**要点的完整清单，确保专业深度，包含专家观点和数据支撑。"""

# =============================================================================
# 自定义内容结构提示词（第六种结构）
# =============================================================================

CUSTOM_CONTENT_STRUCTURE_PROMPT = """你是一位专业的内容创作者。根据用户提供的信息，自由选择最适合的内容结构生成LinkedIn内容。

## 可选内容结构
当以下结构都不适用时，你可以：
1. 自由使用上述5种结构中的任何一种
2. 创造新的结构形式
3. 混合多种结构的特点

## 可选结构参考
- 分类展示型：适合分类、类型、模式列举
- 流程步骤型：适合"从A到B"的过程或"如何做"
- 对比表格型：适合多个相似概念的对比
- 工具列表型：适合工具、资源的集合推荐
- 清单要点型：适合要点、建议、技能分享

## 用户信息
- 职位：{job_title}
- 主题：{topic}
- LinkedIn资料：{linkedin_profile}
- 公司信息：{company_info}
- 目标受众：{target_audience}
- 内容质量：{content_quality}
- 额外说明：{additional_context}

## 质量要求
根据内容质量等级，确保相应的信息密度：
- 普通：简洁精炼，易于快速阅读
- 进阶：信息丰富，有实际价值
- 专业：深度专业，有数据和研究支撑

请生成高质量的LinkedIn内容，选择或创造最适合的内容结构。
在开头说明你选择/创造的结构类型及理由。"""

# =============================================================================
# 辅助提示词（知识库、视觉设计、图片生成）
# =============================================================================

# 知识库检索提示词
KNOWLEDGE_RETRIEVAL_PROMPT = """你是一位专业的知识研究员。请根据主题检索相关的权威信息。

## 五大知识库体系
1. **领域专家库**：顶级创业者的观点、语录、方法论
2. **方法学文献库**：经典商业框架、模型、理论
3. **工具数据库**：AI工具、软件、平台信息
4. **案例研究库**：成功/失败案例、数据指标
5. **内容模板库**：格式模板、配色方案、视觉规范

## 检索要求
请为以下主题生成5-10个相关的知识条目：

主题：{topic}
内容类型：{content_type}

每个条目必须包含：
- 来源类型：[专家观点/方法学/工具/案例/模板]
- 条目标题：[具体名称]
- 详细内容：[关键信息]
- 来源出处：[作者/机构]
- 链接地址：[完整URL]

请以JSON格式返回检索结果。"""

# 视觉设计提示词
VISUAL_DESIGN_PROMPT = """你是一位专业的视觉设计师，专注于LinkedIn图文内容的视觉设计。

## 通用视觉参数
- 画布尺寸：1080×1350px（4:5竖版）
- 背景色：白色（#FFFFFF）或浅米色（#F5F5F0）
- 布局结构：标题区15-20%、内容区65-75%、行动区10%
- 主标题字体：Arial Black, 36-40pt, 深绿色（#2d5a3d）
- 正文字体：Arial Regular, 12-14pt, 深灰色（#333333）
- 配色方案：基底白色60%，强调色深绿色#2d5a3d（10%），模块背景采用马卡龙色系
- 留白：行间距1.5倍，边缘留白15-20px，模块圆角4-8px

## 生成要求
请根据以下信息生成详细的视觉设计文案：

主题：{topic}
内容类型：{content_type}
内容摘要：{content_summary}

请输出：
1. 整体布局描述
2. 配色序列（具体HEX值）
3. 各区域详细规格（位置、尺寸、字体、颜色）
4. 模块设计规范
"""

# 图片生成提示词模板
IMAGE_GENERATION_PROMPT = """Role: You are a world-class Aesthetic Master and Content Creation Specialist, elite in visual design languages, Swiss-style typography, and modular information architecture. You will transform the following structural copy into a high-end, clean, and logical infographic.

I. Structural Framework (Grid Skeleton)

Modular Card Layout: Utilize a precise "Modular Card Grid" (2-column x N-row or Asymmetric Grid).

Independent Units: Every concept must be enclosed in an independent rounded rectangular container (8px corner radius) with a subtle 1-2px border.

Tri-Section Hierarchy: 1. Header Zone: Main Title + Subtitle + Slogan. 2. Content Zone: The modular grid section. 3. Call-to-Action (CTA) Zone: Footer with download/subscription info.

Design Intent: Maximize information density while ensuring "Scannable Readability."

II. Color Palette (Soft Macaron + Forest Green Anchor)

Base Layer (60%): White (#FFFFFF) or Light Beige (#F5F5F0).

Module Backgrounds (25%): Cycle through low-saturation Macaron tones: Light Green (#e6f4ea), Pale Yellow (#fff2cc), Soft Pink (#ffe6e6), Sky Blue (#e6f7fa), Light Purple (#dda0dd).

Accent/Anchor (10%): Deep Forest Green (#2d5a3d or #006633) used strictly for the Header and Key Titles to provide visual weight.

Highlight Tone (5%): Orange (#ffb347) or Pink (#ffb6c1) for secondary tags or "EXAMPLE" labels.

Text: Deep Charcoal (#333333) for maximum legibility.

III. Typography Hierarchy (Sans-Serif System)

Level 1 (Main Title): Arial Black | 36pt | Deep Green | Bold | Center or Left-aligned.

Level 2 (Subtitle): Arial Bold | 20pt | Deep Green or Grey | Optional Italics.

Level 3 (Module Title): Arial Bold | 16pt | Module-specific Accent Color | Bold.

Body Text: Arial Regular | 12-14pt | #333333 | 1.5x Line Spacing.

Annotations: Arial Bold | 10pt | Bold (e.g., "GOAL:", "TIP:").

Alignment: 90% Left-aligned for logical flow.

IV. Visual Elements (Iconography & Decoration)

Icon System: 2px stroke weight, Outline Style. Consistent sizing (24-32px).

Conceptual: Gears (Ops), Money Bags (Finance).

Indicators: Battery icons (Levels/Energy), Funnel shapes (Process), Checkboxes (Checklists).

Functional Decor: 1px Dashed Lines (#CCCCCC) for soft grouping.

Subtle Light Green Gradient in the Header for depth.

Numbered Circles (White text on black/dark background) to indicate sequence.

V. White Space Philosophy (Breathing Room > Density)

The 30% Rule: Ensure 30% of the canvas remains empty.

Spacing Specs: Between Modules: 15px.

Internal Padding: 10px (Text to Border).

Header to Content: 25px.

Outer Margins: 20px.

📝 Visual Design Copy Implementation
Based on the content about: {topic}

Content Type: {content_type}

Content Summary: {content_summary}

Please generate a professional infographic following these specifications.

Styling Keywords: Minimalist UI Design, Professional Infographic, Vector Illustration, High-Resolution Clean Graphic, Swiss Style Layout, Flat Design, Soft Pastel Tones."""

# =============================================================================
# 提示词映射系统
# =============================================================================

# 质量等级到提示词的映射
# 结构：{内容类型: {质量等级: 提示词}}
CONTENT_QUALITY_PROMPTS = {
    "分类展示型": {
        "normal": CLASSIFICATION_DISPLAY_NORMAL,
        "advanced": CLASSIFICATION_DISPLAY_ADVANCED,
        "professional": CLASSIFICATION_DISPLAY_PROFESSIONAL,
    },
    "流程步骤型": {
        "normal": PROCESS_STEPS_NORMAL,
        "advanced": PROCESS_STEPS_ADVANCED,
        "professional": PROCESS_STEPS_PROFESSIONAL,
    },
    "对比表格型": {
        "normal": COMPARISON_TABLE_NORMAL,
        "advanced": COMPARISON_TABLE_ADVANCED,
        "professional": COMPARISON_TABLE_PROFESSIONAL,
    },
    "工具列表型": {
        "normal": TOOL_LIST_NORMAL,
        "advanced": TOOL_LIST_ADVANCED,
        "professional": TOOL_LIST_PROFESSIONAL,
    },
    "清单要点型": {
        "normal": CHECKLIST_NORMAL,
        "advanced": CHECKLIST_ADVANCED,
        "professional": CHECKLIST_PROFESSIONAL,
    },
    "自定义型": {
        "normal": CUSTOM_CONTENT_STRUCTURE_PROMPT,
        "advanced": CUSTOM_CONTENT_STRUCTURE_PROMPT,
        "professional": CUSTOM_CONTENT_STRUCTURE_PROMPT,
    },
}

# 向后兼容的提示词映射（默认使用进阶质量）
CONTENT_TYPE_PROMPTS = {
    "分类展示型": CLASSIFICATION_DISPLAY_ADVANCED,
    "流程步骤型": PROCESS_STEPS_ADVANCED,
    "对比表格型": COMPARISON_TABLE_ADVANCED,
    "工具列表型": TOOL_LIST_ADVANCED,
    "清单要点型": CHECKLIST_ADVANCED,
    "自定义型": CUSTOM_CONTENT_STRUCTURE_PROMPT,
}

# 内容类型映射到英文（用于内部处理）
CONTENT_TYPE_MAPPING = {
    "分类展示型": "classification_display",
    "流程步骤型": "process_steps",
    "对比表格型": "comparison_table",
    "工具列表型": "tool_list",
    "清单要点型": "checklist",
    "自定义型": "custom",
}

# 反向映射
CONTENT_TYPE_MAPPING_REVERSE = {
    "classification_display": "分类展示型",
    "process_steps": "流程步骤型",
    "comparison_table": "对比表格型",
    "tool_list": "工具列表型",
    "checklist": "清单要点型",
    "custom": "自定义型",
}

# 质量等级映射到中文
QUALITY_MAPPING = {
    "normal": "普通",
    "advanced": "进阶",
    "professional": "专业",
}

# =============================================================================
# LinkedIn POST 精华提炼提示词
# =============================================================================

LINKEDIN_POST_REFINEMENT_PROMPT = """You are a world-class business thinker and LinkedIn influencer in the top 0.1%. You think like Paul Graham, Naval Ravikant, Sam Altman, and other elite business leaders.

## Your Task
Transform the detailed content into a concise, impactful LinkedIn post that captures the **essence and wisdom** rather than repeating details.

## Content to Refine
**Topic**: {topic}
**Original Content**:
{original_content}

## Your Philosophy
1. **First Principles Thinking**: Get to the fundamental truth, not surface-level tactics
2. **Contrarian Insights**: Challenge conventional wisdom with unique perspectives
3. **Mental Models**: Frame ideas using powerful mental models (e.g., Pareto Principle, Compound Effect, Second-Order Thinking)
4. **Actionable Wisdom**: Provide 1-2 powerful insights that can change how people think/act
5. **Emotional Intelligence**: Connect with human desires, fears, and aspirations

## Output Requirements

### Length: 150-300 words (strict)
### Structure:
```
[One powerful opening hook - 10-15 words]
[One sentence framing the insight using a mental model]
[2-3 bullet points with deep wisdom - not tactics]
[One thought-provoking question]
[2-3 relevant hashtags]
```

### Writing Style:
- ✅ Conversational but profound
- ✅ Use simple words for complex ideas
- ✅ Share a counterintuitive insight
- ✅ Focus on ONE big idea
- ✅ End with curiosity
- ❌ NO numbered lists (01, 02, 03...)
- ❌ NO technical jargon
- ❌ NO repetition of image content
- ❌ NO generic advice

### Examples of Good vs Bad:

**❌ Bad (Mechanical Repetition)**:
"Here are 5 ways AI tools help sales teams:
1. Lead scoring helps prioritize
2. Automated outreach saves time
3. Predictive analytics forecasts outcomes
4. Conversation intelligence improves coaching
5. Dynamic pricing optimizes revenue"

**✅ Good (Essence & Wisdom)**:
"Most sales teams use AI wrong. They focus on automation when they should focus on augmentation.

The 80/20 rule applies: 20% of your AI understanding drives 80% of results.

The winners aren't using AI to replace salespeople. They're using it to remove friction from human judgment.

• Automate the process, not the decision
• Scale insights, not just activity
• Let AI be the analyst, you be the strategist

The question isn't 'What can AI do?' It's 'What should humans do differently now that AI exists?'

#AI #Sales #BusinessStrategy"

---

Now, transform the content about "{topic}" into an exceptional LinkedIn post following these guidelines.

Remember: You are writing for sophisticated professionals who value insight over information.
"""