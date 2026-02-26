#!/usr/bin/env python3
"""
测试 LinkedIn POST 精华提炼功能
"""
import sys
sys.path.insert(0, '/Users/wanting/program/CC/Avery/backend')

from api.services.advanced_content_generator import AdvancedContentGenerator

print("=" * 80)
print("🧪 测试 LinkedIn POST 精华提炼功能")
print("=" * 80)
print()

# 初始化生成器
print("1️⃣ 初始化内容生成器...")
generator = AdvancedContentGenerator()
print(f"   模型: {generator.model}")
print()

# 模拟详细内容（类似于图片上会显示的内容）
detailed_content = """
## How Sales Teams Use AI Tools to Double Efficiency

### 01. AI-Powered Lead Scoring
AI prioritizes leads based on likelihood to convert, improving ROI.
**Goal**: Focus efforts on high-value prospects first.
**Tip**: Use historical data to train your scoring model.
**Example**: HubSpot's AI scores leads automatically.

### 02. Automated Outreach & Follow-up
AI automates routine emails and ensures timely communication.
**Goal**: Maintain consistent contact without manual effort.
**Tip**: Personalize templates at scale.
**Example**: Outreach.io automates sequences.

### 03. Predictive Analytics
AI predicts customer behavior and buying patterns.
**Goal**: Anticipate needs and close deals faster.
**Tip**: Combine with CRM data for accuracy.
**Example**: Clari forecasts deal outcomes.

### 04. Conversation Intelligence
AI analyzes sales calls to extract insights and coach reps.
**Goal**: Improve performance through data-driven feedback.
**Tip**: Track keyword usage and talk ratios.
**Example**: Gong.io provides call analytics.

### 05. Dynamic Pricing Optimization
AI adjusts pricing based on market and customer data.
**Goal**: Maximize revenue while staying competitive.
**Tip**: Set guardrails for price ranges.
**Example**: Pricer optimizes dynamically.
"""

print("2️⃣ 原始详细内容（模拟图片内容）:")
print("-" * 80)
print(f"字数: {len(detailed_content.split())} 字")
print(detailed_content[:300] + "...")
print("-" * 80)
print()

# 测试精华提炼
print("3️⃣ 精华提炼中...")
print("   从世界前 0.1% 商业领袖的视角提炼核心洞察")
print()

try:
    refined_post = generator._refine_linkedin_post(
        topic="How Sales Teams Use AI Tools to Double Efficiency",
        original_content=detailed_content,
    )

    print("=" * 80)
    print("✅ 精华提炼完成！")
    print("=" * 80)
    print()
    print("📝 提炼后的 LinkedIn POST:")
    print("-" * 80)
    print(refined_post)
    print("-" * 80)
    print()

    # 分析结果
    word_count = len(refined_post.split())
    print(f"📊 分析:")
    print(f"   原始字数: {len(detailed_content.split())} 字")
    print(f"   提炼字数: {word_count} 字")
    print(f"   压缩比: {word_count / len(detailed_content.split()) * 100:.1f}%")

    # 检查是否有数字序号（应该避免）
    has_numbered_list = any(line.strip().startswith(('01.', '02.', '03.', '04.', '05.', '1.', '2.', '3.', '4.', '5.'))
                            for line in refined_post.split('\n'))
    print(f"   有数字序号: {'❌ 是（需改进）' if has_numbered_list else '✅ 否（符合要求）'}")

    # 检查是否包含深度洞察的关键词
    insight_keywords = ['wisdom', 'insight', 'principle', 'question', 'strategy', 'paradox', 'mistake']
    has_insight = any(keyword in refined_post.lower() for keyword in insight_keywords)
    print(f"   包含深度洞察: {'✅ 是' if has_insight else '⚠️  否'}")

    print()
    print("=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)
    print()
    print("💡 提示:")
    print("   - 如果提炼后的内容仍然太长或太详细，可以调整提示词")
    print("   - 如果缺乏深度洞察，可以增加示例")
    print("   - 当前字数目标: 150-300 字")

except Exception as e:
    print(f"❌ 精华提炼失败: {e}")
    import traceback
    traceback.print_exc()
