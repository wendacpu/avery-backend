#!/usr/bin/env python3
"""
测试 Groq API 生成功能
"""
import sys
sys.path.insert(0, '/Users/wanting/program/CC/Avery/backend')

from api.services.advanced_content_generator import AdvancedContentGenerator
import json

print("=" * 60)
print("🧪 测试 Groq API 内容生成")
print("=" * 60)
print()

# 初始化生成器
print("1️⃣ 初始化内容生成器...")
generator = AdvancedContentGenerator()

print(f"   模型: {generator.model}")
print(f"   客户端类型: {type(generator.client).__name__}")

# 检查是否是 Groq
if "llama" in generator.model.lower():
    print("   ✅ 使用 Groq (Llama 3.1 70B)")
else:
    print(f"   ⚠️  使用其他模型: {generator.model}")

print()

# 测试生成
print("2️⃣ 测试内容生成...")
print("   主题: AI Productivity Tools")
print()

try:
    result = generator.generate_content(
        topic="How Sales Teams Use AI Tools to Double Efficiency",
        linkedin_profile=None,
        company_info=None,
        job_title="sales_director",
        content_quality="advanced",
        output_format="with_image",
        language="en"
    )

    print("✅ 生成成功！")
    print()

    # 显示结果
    if result.get("success"):
        content = result.get("content", "")
        print("=" * 60)
        print("📝 生成的内容:")
        print("=" * 60)
        print(content[:500])
        if len(content) > 500:
            print("...")
        print("=" * 60)
        print()

        # 检查是否是 mock 数据
        if "Define Clear Goals" in content:
            print("⚠️  警告：仍在使用 mock 数据")
        else:
            print("✅ 确认：使用真实 AI 生成内容")

        print()
        print("📊 生成结果:")
        print(f"   - 成功: {result.get('success')}")
        print(f"   - 字数: {result.get('word_count')}")
        summary = result.get('summary')
        if summary:
            print(f"   - 摘要: {summary[:80]}...")
        else:
            print(f"   - 摘要: (无)")

    else:
        print("❌ 生成失败")
        print(json.dumps(result, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"❌ 生成出错: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
