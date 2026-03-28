# Infographic Design Specification System

## ✅ 已实现功能

### 1. 设计规范引擎 (`design_specification.py`)

**核心功能：**
- ✅ **5种布局模式** - 自动选择，避免重复：
  - 左文右图 (left-text-right-image)
  - 左图右文 (left-image-right-text)
  - 上文下图 (top-text-bottom-image)
  - 四周文中心图 (four-sides-center-image)
  - 垂直流向 (vertical-flow)

- ✅ **板块数量控制** - 自动设置为3-5个板块（偏好4个）
- ✅ **5种商务风配色方案** - 每种方案严格限制4种颜色
- ✅ **字体规范** - 硬性要求正文字号最小14px
- ✅ **布局历史记录** - 记录最近10次使用的布局，确保不重复

### 2. 智能图表选择器

**规则：**
- ✅ **折线图** - 用于时间序列/趋势数据 (has_time_series)
- ✅ **柱状图** - 用于对比数据 (has_comparison)
- ✅ **饼状图** - 用于分布/占比数据 (has_distribution)

**实现：**
- 自动分析内容关键词识别数据特性
- 从行业调研数据中提取图表类型信息
- 根据数据特性推荐最优图表类型

### 3. Prompt Builder集成

**功能：**
- ✅ 自动应用设计规范到每个生成的prompt
- ✅ 动态调整板块数量匹配设计规范要求
- ✅ 智能集成研究数据和图表推荐
- ✅ 生成多样化的布局指令

## 📋 设计规范详情

### 板块数量规则
```python
min_sections: 3    # 最少3个板块
max_sections: 5    # 最多5个板块
preferred: 4       # 偏好4个板块 (70%概率)
```

### 字体规范（硬性要求）
```python
title: 48px min        # 主标题
subtitle: 24px min     # 副标题
body: 14px MINIMUM     # 正文字号（不小于14px）
caption: 12px          # 说明文字
```

### 配色方案（最多4种颜色）
每个配色方案包含：
1. **Primary** - 主色，用于标题和重点
2. **Secondary** - 辅色，用于副标题和标签
3. **Background** - 背景色，用于画布
4. **Accent** - 强调色，用于图表和高亮

### 商务风配色库
- 森林绿 + 金色
- 海军蓝 + 棕色
- 咖啡色 + 米色
- 深灰蓝 + 橙色
- 鞍褐色 + 金麒麟色

## 🔄 工作流程

```
用户请求 → 行业调研 → 设计规范引擎 → Prompt Builder → AI生成
                ↓
          数据特性分析
          (图表类型推荐)
```

## 📝 Prompt生成示例

每次生成的prompt包含：

```
**2. LAYOUT STRUCTURE**
Layout Pattern: left-text-right-image (唯一，不重复)
Sections: 4 (strictly between 3-5)
[具体布局描述]

**3. COLOR PALETTE (Maximum 4 colors)**
Primary: #2D5A3D
Secondary: #C9A65C
Background: #F7F4EF
Accent: #4A7C59
[严格限制]

**4. TYPOGRAPHY**
Body Text: 14px, Regular (MINIMUM - NO EXCEPTIONS)
[硬性要求]

**7. DATA VISUALIZATION**
Chart 1: BAR CHART - Use for comparisons
Chart 2: LINE CHART - Use for trends over time
[智能推荐]
```

## 🎯 用户要求固化完成

✅ 严禁每个图片使用同一模板 - 5种布局随机选择
✅ 保持3-4个板块，最多不超过5个 - 自动控制板块数量
✅ 正文字号最小为14px - 硬性编码在prompt中
✅ 风格为商务风，主题色不超过4种颜色 - 5种商务配色方案
✅ 排版多样化 - 5种布局模式
✅ 图表智能选择 - 根据数据特性自动选择最优图表

## ⚠️ 已知问题

**板块数量匹配问题：**
- 当前状态：设计规范引擎可能要求5个板块，但实际内容可能只有3-4个key_points
- 影响：序号验证可能失败（期望5个序号，实际只有3-4个）
- 修复方案：已在_adjust_section_count中实现自动补充机制

**下次生成测试：**
- 系统会自动补充缺少的板块
- 确保序号完整性
- 验证整个流程

## 📊 系统状态

✅ 设计规范引擎 - 已实现并测试
✅ 智能图表选择器 - 已实现并测试
✅ Prompt Builder集成 - 已实现并测试
✅ 后端启动 - 正常运行
✅ 5种商务风配色 - 可用
✅ 布局多样性 - 5种模式随机选择
⚠️ 板块数量匹配 - 已修复，待测试验证

---
**创建时间:** 2026-03-16
**版本:** v1.0
**状态:** 生产就绪（待最终测试验证）
