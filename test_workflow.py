"""
测试完整的内容生成工作流
"""
import sys
sys.path.insert(0, '.')

from api.services.advanced_content_generator import advanced_content_generator

# 测试完整工作流
print("=" * 50)
print("测试完整n8n工作流")
print("=" * 50)

topic = "AI在创业中的应用"

result = advanced_content_generator.generate_content(
    topic=topic,
    content_type="custom",  # 可以是 industry_trends, position_insight, custom
    linkedin_profile=None,
    company_info=None,
    additional_context=None
)

print("\n生成结果:")
print(f"内容类型: {result.get('content_type')}")
print(f"字数: {result.get('word_count')}")
print(f"\n生成内容预览:")
print(result.get('content', '')[:500] + "..." if len(result.get('content', '')) > 500 else result.get('content', ''))

print("\n元数据:")
print(result.get('metadata', {}))

print("\n" + "=" * 50)
print("测试完成!")
print("=" * 50)
