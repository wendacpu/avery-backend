"""
主题推荐服务
基于三个维度生成 LinkedIn 内容主题推荐：
1. 热点 + 职位（AI分析）
2. 历史帖子分析（最近3个月，按互动排序）
3. 行业趋势（AI分析）
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from openai import OpenAI

from api.services.linkedin_scraper import linkedin_scraper
from api.services.audience_mapper import get_target_audience
from api.core.config import settings

logger = logging.getLogger(__name__)


class TopicRecommender:
    """主题推荐器 - 多维度主题推荐"""

    def __init__(self):
        self.client = None
        # 使用 Novita AI API（兼容 OpenAI SDK）
        if settings.novita_api_key and settings.novita_api_key != "your-novita-api-key-here":
            self.client = OpenAI(
                api_key=settings.novita_api_key,
                base_url="https://api.novita.ai/v1"
            )
            logger.info("Novita AI client initialized for topic recommendation")
        else:
            logger.warning("未配置 Novita API 密钥，将使用模拟推荐数据")

    def generate_recommendations(
        self,
        job_title: str,
        linkedin_profile: Dict[str, Any],
        company_info: Optional[Dict[str, Any]] = None,
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        生成多维度主题推荐

        Args:
            job_title: 职位（枚举值，如 "ceo_founder"）
            linkedin_profile: LinkedIn资料（包含最近3个月帖子）
            company_info: 公司信息（可选）
            count: 推荐数量，默认5个

        Returns:
            推荐主题列表，格式：
            [
                {
                    "topic": "CEO如何用AI提升决策效率",
                    "source": "hot_topic",  # hot_topic | historical | industry_trend
                    "reason": "AI是当前热点，结合CEO职位视角会产生独特价值",
                    "estimated_engagement": 85
                },
                ...
            ]
        """
        recommendations = []

        # 维度1: 热点 + 职位（AI分析）
        hot_topics = self._generate_hot_topic_recommendations(
            job_title, linkedin_profile, company_info, count=2
        )
        recommendations.extend(hot_topics)

        # 维度2: 历史帖子分析（从LinkedIn资料中提取）
        historical_topics = self._generate_historical_recommendations(
            job_title, linkedin_profile, count=2
        )
        recommendations.extend(historical_topics)

        # 维度3: 行业趋势（AI分析）
        trend_topics = self._generate_trend_recommendations(
            job_title, linkedin_profile, company_info, count=1
        )
        recommendations.extend(trend_topics)

        # 按预估互动度排序
        recommendations.sort(key=lambda x: x.get("estimated_engagement", 0), reverse=True)

        return recommendations[:count]

    def _generate_hot_topic_recommendations(
        self,
        job_title: str,
        linkedin_profile: Dict[str, Any],
        company_info: Optional[Dict[str, Any]],
        count: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        维度1: 热点 + 职位（AI分析）

        结合当前热点和职位特点，生成高互动度主题
        """
        if not self.client:
            return self._get_mock_hot_topics(job_title, count)

        try:
            # 准备上下文信息
            profile_str = self._format_profile_info(linkedin_profile)
            company_str = self._format_company_info(company_info) if company_info else "未提供"

            # 获取目标受众
            from api.models.content import JobTitle
            job_title_enum = JobTitle(job_title)
            target_audience = get_target_audience(job_title_enum)

            prompt = f"""你是一位LinkedIn内容策略专家。请基于当前热点和职位特点，生成 {count} 个高互动度主题推荐。

**用户信息**：
- 职位：{job_title}
- 目标受众：{target_audience}
- LinkedIn资料：{profile_str}
- 公司信息：{company_str}

**当前热点参考**（2025年）：
- AI/大模型应用（Agent、RAG、Copilot）
- 远程协作与异步沟通
- 个人品牌与私域运营
- 数据驱动决策
- 效率工具与自动化
- 可持续发展与社会责任
- 新兴市场机会

**要求**：
1. 每个主题都要结合热点 + 职位独特视角
2. 主题要具体、有观点、引发讨论
3. 估算互动度（0-100分，基于共鸣度、争议性、实用性）

请以JSON数组格式返回：
[
  {{
    "topic": "主题标题（10-25字）",
    "reason": "推荐理由（1-2句话）",
    "estimated_engagement": 85
  }}
]"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "你是LinkedIn内容策略专家，擅长结合热点和职位特点生成高互动度主题。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,  # 高温度以增加创意多样性
            )

            result = response.choices[0].message.content

            # 解析JSON响应
            try:
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0].strip()
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0].strip()

                topics = json.loads(result)

                # 添加source标记
                for item in topics:
                    item["source"] = "hot_topic"

                return topics

            except Exception as e:
                logger.warning(f"热点主题解析失败: {e}")
                return self._get_mock_hot_topics(job_title, count)

        except Exception as e:
            logger.error(f"热点主题生成失败: {e}")
            return self._get_mock_hot_topics(job_title, count)

    def _generate_historical_recommendations(
        self,
        job_title: str,
        linkedin_profile: Dict[str, Any],
        count: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        维度2: 历史帖子分析

        从用户最近3个月的高互动帖子中提取主题模式
        """
        try:
            # 从LinkedIn资料中获取历史帖子
            recent_posts = linkedin_profile.get("recent_posts", [])

            if not recent_posts or len(recent_posts) == 0:
                # 没有历史数据，返回通用建议
                return self._get_mock_historical_topics(job_title, count)

            # 按互动分数排序（如果有）
            sorted_posts = sorted(
                recent_posts,
                key=lambda x: x.get("engagement_score", 0),
                reverse=True
            )

            # 取前5个高互动帖子
            top_posts = sorted_posts[:5]

            if not self.client:
                # 无API，基于关键词简单提取
                return self._extract_topics_from_posts_simple(top_posts, count)

            # 使用AI分析高互动帖子，提取主题模式
            posts_summary = "\n".join([
                f"- {post.get('content', '')[:100]}... (互动: {post.get('engagement_score', 0)})"
                for post in top_posts
            ])

            prompt = f"""你是一位LinkedIn内容分析专家。请分析以下用户的高互动帖子，提取出 {count} 个可以再次创作的主题。

**用户职位**：{job_title}

**高互动帖子**（最近3个月，按互动排序）：
{posts_summary}

**分析要求**：
1. 识别这些高互动帖子的共同主题模式
2. 提取受众最感兴趣的话题方向
3. 生成可以延续创作的新主题（不要重复原帖，而是延伸相关话题）
4. 估算互动度（参考历史表现）

请以JSON数组格式返回：
[
  {{
    "topic": "延伸主题标题",
    "reason": "基于历史高互动帖子的XX方向延伸",
    "estimated_engagement": 75
  }}
]"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "你是LinkedIn内容分析专家，擅长从历史帖子中提取高价值主题。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )

            result = response.choices[0].message.content

            # 解析JSON响应
            try:
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0].strip()
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0].strip()

                topics = json.loads(result)

                # 添加source标记
                for item in topics:
                    item["source"] = "historical"

                return topics

            except Exception as e:
                logger.warning(f"历史主题解析失败: {e}")
                return self._extract_topics_from_posts_simple(top_posts, count)

        except Exception as e:
            logger.error(f"历史主题生成失败: {e}")
            return self._get_mock_historical_topics(job_title, count)

    def _generate_trend_recommendations(
        self,
        job_title: str,
        linkedin_profile: Dict[str, Any],
        company_info: Optional[Dict[str, Any]],
        count: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        维度3: 行业趋势（AI分析）

        基于职位所在行业的未来趋势，生成前瞻性主题
        """
        if not self.client:
            return self._get_mock_trend_topics(job_title, count)

        try:
            # 准备上下文信息
            profile_str = self._format_profile_info(linkedin_profile)
            company_str = self._format_company_info(company_info) if company_info else "未提供"

            prompt = f"""你是一位LinkedIn行业趋势分析师。请基于职位和行业特点，生成 {count} 个前瞻性趋势主题。

**用户信息**：
- 职位：{job_title}
- LinkedIn资料：{profile_str}
- 公司信息：{company_str}

**分析要求**：
1. 识别该职位所在行业的关键趋势（2025-2026年）
2. 结合职位特点，生成有前瞻性的主题
3. 主题要体现洞察力和专业度
4. 估算互动度（趋势类内容通常较高）

请以JSON数组格式返回：
[
  {{
    "topic": "趋势主题标题",
    "reason": "基于XX行业趋势，结合职位视角",
    "estimated_engagement": 80
  }}
]"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "你是LinkedIn行业趋势分析师，擅长识别和解读行业趋势。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.9,  # 高温度以增加创新性
            )

            result = response.choices[0].message.content

            # 解析JSON响应
            try:
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0].strip()
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0].strip()

                topics = json.loads(result)

                # 添加source标记
                for item in topics:
                    item["source"] = "industry_trend"

                return topics

            except Exception as e:
                logger.warning(f"趋势主题解析失败: {e}")
                return self._get_mock_trend_topics(job_title, count)

        except Exception as e:
            logger.error(f"趋势主题生成失败: {e}")
            return self._get_mock_trend_topics(job_title, count)

    # ===== 辅助方法 =====

    def _format_profile_info(self, profile: Dict[str, Any]) -> str:
        """格式化LinkedIn资料信息"""
        if not profile:
            return "未提供"
        return f"姓名: {profile.get('name', 'N/A')}, 职位: {profile.get('title', 'N/A')}"

    def _format_company_info(self, company: Dict[str, Any]) -> str:
        """格式化公司信息"""
        if not company:
            return "未提供"
        return f"公司: {company.get('name', 'N/A')}, 描述: {company.get('description', 'N/A')}"

    def _extract_topics_from_posts_simple(
        self,
        posts: List[Dict[str, Any]],
        count: int
    ) -> List[Dict[str, Any]]:
        """
        简单方法：从帖子中提取关键词作为主题（无API时使用）
        """
        # 提取帖子内容中的关键词
        topics = []
        for post in posts[:count]:
            content = post.get("content", "")
            # 取前50字作为主题
            topic = content[:50].replace("\n", " ")
            if len(topic) < 20:
                topic = "关于" + topic + "的深度思考"

            topics.append({
                "topic": topic,
                "source": "historical",
                "reason": "基于历史高互动内容延伸",
                "estimated_engagement": 70
            })

        return topics

    # ===== 模拟数据方法 =====

    def _get_mock_hot_topics(self, job_title: str, count: int) -> List[Dict[str, Any]]:
        """生成模拟热点主题"""
        mock_topics = {
            "ceo_founder": [
                {"topic": "How CEOs Use AI to Improve Decision-Making", "reason": "AI is trending, CEO decision-making is core pain point", "estimated_engagement": 90},
                {"topic": "How Founders Balance Short-term Revenue with Long-term Vision", "reason": "Eternal debate topic, resonates with audience", "estimated_engagement": 85},
            ],
            "product_manager": [
                {"topic": "How Product Managers Use AI to Reconstruct Requirements Analysis", "reason": "AI + Product Management is trending", "estimated_engagement": 88},
                {"topic": "PMF Validation Framework for B2B SaaS Products", "reason": "Practical methodology, high save rate", "estimated_engagement": 80},
            ],
            "sales_director": [
                {"topic": "How Sales Teams Use AI Tools to Double Efficiency", "reason": "Efficiency tools + sales, essential need", "estimated_engagement": 92},
                {"topic": "Building B2B Sales Funnel System from Scratch", "reason": "Practical insights, high share and save rate", "estimated_engagement": 85},
            ],
            "default": [
                {"topic": "How to Use AI Tools to Improve Work Efficiency", "reason": "AI trending + efficiency improvement, universal topic", "estimated_engagement": 80},
                {"topic": "Best Practices for Remote Team Collaboration", "reason": "Work style transformation, sparks discussion", "estimated_engagement": 75},
            ],
        }

        topics = mock_topics.get(job_title, mock_topics["default"])

        result = []
        for item in topics[:count]:
            item["source"] = "hot_topic"
            result.append(item)

        return result

    def _get_mock_historical_topics(self, job_title: str, count: int) -> List[Dict[str, Any]]:
        """生成模拟历史主题"""
        return [
            {
                "topic": f"Practical {job_title.replace('_', ' ').title()} Insights Based on Past Experience",
                "source": "historical",
                "reason": "Continue direction of high-engagement historical content",
                "estimated_engagement": 70,
            }
        ][:count]

    def _get_mock_trend_topics(self, job_title: str, count: int) -> List[Dict[str, Any]]:
        """生成模拟趋势主题"""
        return [
            {
                "topic": f"2025 Industry Trends Every {job_title.replace('_', ' ').title()} Should Watch",
                "source": "industry_trend",
                "reason": "Forward-looking trend analysis",
                "estimated_engagement": 75,
            }
        ][:count]


# 全局实例
topic_recommender = TopicRecommender()
