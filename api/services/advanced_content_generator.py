"""
高级内容生成服务
实现完整的内容生成工作流，支持：
- 6种内容结构
- 3种质量等级（普通、进阶、专业）
- 2种输出格式（纯文字、一图）
- 自动目标受众推断
"""
import os
import json
import logging
import httpx
from typing import Dict, Any, Optional, List
from openai import OpenAI

from api.prompts.content_generation_prompts import (
    CONTENT_TYPE_DECISION_PROMPT,
    CONTENT_QUALITY_PROMPTS,
    CONTENT_TYPE_PROMPTS,
    KNOWLEDGE_RETRIEVAL_PROMPT,
    VISUAL_DESIGN_PROMPT,
    IMAGE_GENERATION_PROMPT,
    CONTENT_TYPE_MAPPING,
    CONTENT_TYPE_MAPPING_REVERSE,
    QUALITY_MAPPING,
)
from api.services.audience_mapper import get_target_audience
from api.core.config import settings

logger = logging.getLogger(__name__)


class AdvancedContentGenerator:
    """高级内容生成器 - 完整内容生成工作流"""

    def __init__(self):
        self.client = None
        # 使用 Novita AI API（兼容 OpenAI SDK）
        if settings.novita_api_key and settings.novita_api_key != "your-novita-api-key-here":
            self.client = OpenAI(
                api_key=settings.novita_api_key,
                base_url="https://api.novita.ai/v1"
            )
            logger.info("Novita AI client initialized for content generation")
        else:
            logger.warning("未配置 Novita API 密钥，将使用模拟数据")

    def generate_content(
        self,
        topic: str,
        linkedin_profile: Optional[Dict] = None,
        company_info: Optional[Dict] = None,
        additional_context: Optional[str] = None,
        job_title: Optional[str] = None,
        content_quality: Optional[str] = None,
        output_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        完整的内容生成流程

        Args:
            topic: 主题
            linkedin_profile: LinkedIn资料
            company_info: 公司信息
            additional_context: 额外上下文
            job_title: 职位（枚举值，如 "ceo_founder"）
            content_quality: 内容质量（"normal", "advanced", "professional"）
            output_format: 输出格式（"text_only", "with_image"）

        Returns:
            生成的内容和元数据
        """
        logger.info(f"开始内容生成流程 - 主题: {topic}, 质量: {content_quality}, 格式: {output_format}")

        # 默认值处理
        if not content_quality:
            content_quality = "advanced"
        if not output_format:
            output_format = "text_only"
        if not job_title:
            job_title = "other"

        # 第一步：推断目标受众
        target_audience = get_target_audience(job_title)
        logger.info(f"目标受众: {target_audience}")

        # 第二步：内容类型决策
        content_type_decision = self._decide_content_type(topic)
        content_type_cn = content_type_decision["content_type_cn"]
        logger.info(f"内容类型决策: {content_type_cn}")

        # 第三步：知识库检索
        knowledge_retrieval = self._retrieve_knowledge(topic, content_type_cn)
        logger.info(f"知识库检索完成，找到 {len(knowledge_retrieval.get('items', []))} 条")

        # 第四步：生成内容主干（使用质量等级提示词）
        content_main = self._generate_content_main(
            topic,
            content_type_cn,
            linkedin_profile,
            company_info,
            additional_context,
            knowledge_retrieval,
            target_audience,
            content_quality,
        )
        logger.info("内容主干生成完成")

        # 第五步：生成视觉设计文案（仅当 output_format == "with_image"）
        visual_design = None
        if output_format == "with_image":
            visual_design = self._generate_visual_design(
                topic,
                content_type_cn,
                content_main.get("summary", ""),
            )
            logger.info("视觉设计文案生成完成")
        else:
            logger.info("纯文字模式，跳过视觉设计生成")

        # 第六步：整合最终输出
        final_content = self._integrate_final_content(
            topic,
            content_type_decision,
            knowledge_retrieval,
            content_main,
            visual_design,
            linkedin_profile,
            company_info,
            additional_context,
            target_audience,
            content_quality,
        )
        logger.info("最终内容整合完成")

        return final_content

    def _decide_content_type(self, topic: str) -> Dict[str, Any]:
        """
        内容类型决策

        通过5个评估问题自动匹配最优内容格式
        """
        if not self.client:
            # 无API时返回默认类型
            return {
                "content_type_cn": "清单要点型",
                "content_type_en": "checklist",
                "reason": "使用默认类型（无AI API）",
                "confidence": 0.5,
            }

        try:
            prompt = CONTENT_TYPE_DECISION_PROMPT.format(topic=topic)
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "你是专业的内容策略专家，擅长分析主题并选择最优的内容格式。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )

            result = response.choices[0].message.content
            # 解析JSON响应
            decision = json.loads(result)
            content_type_cn = decision.get("content_type", "清单要点型")

            return {
                "content_type_cn": content_type_cn,
                "content_type_en": CONTENT_TYPE_MAPPING.get(content_type_cn, "checklist"),
                "reason": decision.get("reason", ""),
                "confidence": decision.get("confidence", 0.8),
            }

        except Exception as e:
            logger.error(f"内容类型决策失败: {str(e)}")
            return {
                "content_type_cn": "清单要点型",
                "content_type_en": "checklist",
                "reason": "决策失败，使用默认类型",
                "confidence": 0.5,
            }

    def _retrieve_knowledge(self, topic: str, content_type_cn: str) -> Dict[str, Any]:
        """
        知识库检索（完整版）

        1. 使用 AI 生成检索 URL 列表
        2. 使用 HTTP 请求抓取网页内容
        3. 过滤、排序、格式化知识库
        """
        if not self.client:
            # 返回模拟知识库数据
            return self._get_mock_knowledge(topic, content_type_cn)

        try:
            # 步骤 1: 使用 AI 生成 URL 列表
            url_list_prompt = f"""根据主题「{topic}」，生成 5-10 个最相关的高质量信息源 URL。

请选择以下类型的来源：
1. 专家观点博客（如 Paul Graham, Naval Ravikant 等）
2. 方法论文献（如 AIDA, AARRR, 精益创业等）
3. 工具数据库（如 Product Hunt, G2, 官网）
4. 案例研究（如 Indie Hackers, Case Study Club）
5. 知名公司/产品文档

请以 JSON 数组格式返回，每个 URL 包含：
- url: 完整的 URL
- type: 来源类型（expert_viewpoint/framework/tool/case_study）
- title: 简短标题

返回格式：
[
  {{"url": "https://...", "type": "expert_viewpoint", "title": "..."}},
  ...
]"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "你是专业的知识研究员，擅长为指定主题找到最权威的信息源。",
                    },
                    {"role": "user", "content": url_list_prompt},
                ],
                temperature=0.3,
            )

            result = response.choices[0].message.content

            # 解析 URL 列表
            try:
                # 提取 JSON（可能被代码块包裹）
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0].strip()
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0].strip()

                url_list = json.loads(result)

                if not isinstance(url_list, list):
                    url_list = []

                logger.info(f"AI 生成了 {len(url_list)} 个 URL")

            except Exception as e:
                logger.warning(f"URL 列表解析失败: {e}，使用空列表")
                url_list = []

            # 步骤 2: 使用 HTTP 请求抓取网页内容
            retrieved_content = []
            if url_list:
                retrieved_content = self._fetch_urls_content(url_list)

            # 步骤 3: 格式化知识库为文本（供 LLM 使用）
            formatted_knowledge = self._format_knowledge_for_llm(retrieved_content, topic)

            return {
                "success": True,
                "items": retrieved_content,
                "formatted_text": formatted_knowledge,
                "retrieval_stats": {
                    "total_urls": len(url_list),
                    "successful": len(retrieved_content),
                    "failed": len(url_list) - len(retrieved_content)
                },
                "source": "web_retrieval",
            }

        except Exception as e:
            logger.error(f"知识库检索失败: {str(e)}")
            return self._get_mock_knowledge(topic, content_type_cn)

    def _fetch_urls_content(self, url_list: List[Dict]) -> List[Dict]:
        """
        使用 HTTP 请求批量抓取 URL 内容

        Args:
            url_list: URL 列表，每个元素包含 url, type, title

        Returns:
            抓取成功的内容列表
        """
        retrieved_content = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        for url_info in url_list:
            url = url_info.get("url", "")
            content_type = url_info.get("type", "unknown")
            title = url_info.get("title", "")

            if not url:
                continue

            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.get(url, headers=headers, follow_redirects=True)

                    if response.status_code == 200:
                        # 简单提取文本内容（去除 HTML 标签）
                        text = self._extract_text_from_html(response.text)

                        # 计算质量分数
                        quality_score = 0
                        if len(text) > 500:
                            quality_score += 0.3
                        if len(text) > 1500:
                            quality_score += 0.2
                        if "404" not in text and "error" not in text.lower():
                            quality_score += 0.3
                        if len(text) > 200:
                            quality_score += 0.2

                        # 只保留高质量内容
                        if quality_score >= 0.5:
                            retrieved_content.append({
                                "url": url,
                                "type": content_type,
                                "title": title,
                                "text": text[:5000],  # 限制长度
                                "length": len(text),
                                "quality_score": quality_score,
                            })
                            logger.info(f"成功抓取: {url} (质量分数: {quality_score:.2f})")
                        else:
                            logger.warning(f"内容质量过低，跳过: {url}")
                    else:
                        logger.warning(f"HTTP {response.status_code}: {url}")

            except Exception as e:
                logger.warning(f"抓取失败 {url}: {str(e)}")
                continue

        # 按质量分数降序排序
        retrieved_content.sort(key=lambda x: x["quality_score"], reverse=True)

        return retrieved_content

    def _extract_text_from_html(self, html: str) -> str:
        """
        简单的 HTML 文本提取（不使用外部库）
        """
        import re

        # 移除 script 和 style 标签
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # 移除所有 HTML 标签
        text = re.sub(r'<[^>]+>', ' ', html)

        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def _format_knowledge_for_llm(self, retrieved_content: List[Dict], topic: str) -> str:
        """
        将检索到的内容格式化为 LLM 可读的文本

        Args:
            retrieved_content: 检索到的内容列表
            topic: 主题

        Returns:
            格式化后的文本
        """
        if not retrieved_content:
            return f"未找到关于「{topic}」的相关资料。请使用自身知识库生成内容。"

        formatted_parts = [f"## 知识库检索结果：{topic}\n"]
        formatted_parts.append(f"共检索到 {len(retrieved_content)} 条高质量资料：\n")

        # 按类型分组
        grouped = {}
        for item in retrieved_content:
            content_type = item.get("type", "unknown")
            if content_type not in grouped:
                grouped[content_type] = []
            grouped[content_type].append(item)

        # 类型映射到中文
        type_names = {
            "expert_viewpoint": "📚 专家观点",
            "framework": "📋 方法框架",
            "tool": "🔧 工具资源",
            "case_study": "📖 案例研究",
            "unknown": "📄 相关资料"
        }

        # 格式化每种类型
        for content_type, items in grouped.items():
            type_name = type_names.get(content_type, f"📄 {content_type}")
            formatted_parts.append(f"\n### {type_name}\n")

            for i, item in enumerate(items[:5], 1):  # 每种类型最多显示 5 个
                title = item.get("title", "Untitled")
                url = item.get("url", "")
                text = item.get("text", "")[:500]  # 限制长度

                formatted_parts.append(f"{i}. **{title}**")
                formatted_parts.append(f"   来源: {url}")
                formatted_parts.append(f"   内容: {text}...\n")

        return "\n".join(formatted_parts)

    def _generate_content_main(
        self,
        topic: str,
        content_type_cn: str,
        linkedin_profile: Optional[Dict],
        company_info: Optional[Dict],
        additional_context: Optional[str],
        knowledge_retrieval: Dict,
        target_audience: str,
        content_quality: str,
    ) -> Dict[str, Any]:
        """
        生成内容主干

        根据选定类型和质量等级生成完整的内容结构
        """
        # 准备上下文信息
        profile_str = self._format_profile_info(linkedin_profile) if linkedin_profile else "未提供"
        company_str = self._format_company_info(company_info) if company_info else "未提供"
        context_str = additional_context or "无"

        # 获取格式化的知识库文本（如果存在）
        knowledge_text = knowledge_retrieval.get("formatted_text", "")
        if not knowledge_text and knowledge_retrieval.get("items"):
            # 如果没有格式化文本但有 items，创建简单的格式化文本
            knowledge_text = f"参考资料：\n" + "\n".join([
                f"- {item.get('title', 'Untitled')}: {item.get('text', '')[:200]}..."
                for item in knowledge_retrieval["items"][:5]
            ])

        # 根据质量等级选择对应的提示词
        quality_prompts = CONTENT_QUALITY_PROMPTS.get(content_type_cn, {})
        prompt_template = quality_prompts.get(content_quality, CONTENT_TYPE_PROMPTS.get(content_type_cn))

        # 格式化提示词
        prompt = prompt_template.format(
            topic=topic,
            linkedin_profile=profile_str,
            company_info=company_str,
            target_audience=target_audience,
            additional_context=context_str,
            job_title=content_quality,  # 自定义类型需要job_title
            content_quality=QUALITY_MAPPING.get(content_quality, content_quality),
        )

        # 如果有知识库检索结果，添加到提示词中
        if knowledge_text:
            prompt = f"""{prompt}

---

## 知识库参考资料

{knowledge_text}

请基于以上参考资料生成内容，确保内容有据可依、信息准确。"""
        else:
            prompt = f"""{prompt}

---

（注：未检索到外部参考资料，请使用自身知识库生成内容）"""

        if not self.client:
            return self._get_mock_content_main(topic, content_type_cn)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"你是LinkedIn专业内容创作者，擅长创作{content_type_cn}内容（{QUALITY_MAPPING.get(content_quality, content_quality)}质量）。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=3000,
            )

            content = response.choices[0].message.content

            return {
                "success": True,
                "content": content,
                "summary": content[:200] + "..." if len(content) > 200 else content,
                "word_count": len(content.split()),
                "knowledge_used": len(knowledge_retrieval.get("items", [])),  # 记录使用的知识库数量
            }

        except Exception as e:
            logger.error(f"内容主干生成失败: {str(e)}")
            return self._get_mock_content_main(topic, content_type_cn)

    def _generate_visual_design(
        self,
        topic: str,
        content_type_cn: str,
        content_summary: str,
    ) -> Dict[str, Any]:
        """
        生成视觉设计文案

        为内容生成详细的视觉设计规范
        """
        if not self.client:
            return self._get_mock_visual_design(topic, content_type_cn)

        try:
            prompt = VISUAL_DESIGN_PROMPT.format(
                topic=topic,
                content_type=content_type_cn,
                content_summary=content_summary,
            )

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "你是专业的视觉设计师，专注于LinkedIn图文内容的视觉设计。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=1500,
            )

            design_specs = response.choices[0].message.content

            return {
                "success": True,
                "design_specs": design_specs,
                "canvas_size": "1080x1350px (4:5 portrait)",
                "primary_color": "#2d5a3d (深绿色)",
                "background": "#FFFFFF or #F5F5F0",
            }

        except Exception as e:
            logger.error(f"视觉设计生成失败: {str(e)}")
            return self._get_mock_visual_design(topic, content_type_cn)

    def _integrate_final_content(
        self,
        topic: str,
        content_type_decision: Dict,
        knowledge_retrieval: Dict,
        content_main: Dict,
        visual_design: Optional[Dict],
        linkedin_profile: Optional[Dict],
        company_info: Optional[Dict],
        additional_context: Optional[str],
        target_audience: str,
        content_quality: str,
    ) -> Dict[str, Any]:
        """
        整合最终输出

        整合所有信息，生成最终的高质量内容
        """
        profile_str = self._format_profile_info(linkedin_profile) if linkedin_profile else "未提供"
        company_str = self._format_company_info(company_info) if company_info else "未提供"
        context_str = additional_context or "无"

        if not self.client:
            # 无API时返回简化版内容
            return self._get_mock_final_content(
                topic,
                content_type_decision,
                content_main,
                visual_design,
                target_audience,
            )

        try:
            # 直接使用内容主干作为最终内容
            final_content = content_main.get("content", "")

            return {
                "success": True,
                "content": final_content,
                "content_type": content_type_decision["content_type_cn"],
                "content_type_en": content_type_decision["content_type_en"],
                "word_count": len(final_content.split()),
                "target_audience": target_audience,
                "content_quality": content_quality,
                "metadata": {
                    "decision": content_type_decision,
                    "knowledge_count": len(knowledge_retrieval.get("items", [])),
                    "has_visual_design": visual_design is not None,
                    "visual_design_specs": visual_design.get("design_specs") if visual_design else None,
                },
            }

        except Exception as e:
            logger.error(f"最终内容整合失败: {str(e)}")
            return self._get_mock_final_content(
                topic,
                content_type_decision,
                content_main,
                visual_design,
                target_audience,
            )

    def generate_image_prompt(
        self,
        topic: str,
        content_type_cn: str,
        content_summary: str,
    ) -> str:
        """
        生成图片生成的提示词
        """
        return IMAGE_GENERATION_PROMPT.format(
            topic=topic,
            content_type=content_type_cn,
            content_summary=content_summary,
        )

    # ===== 辅助方法 =====

    def _format_profile_info(self, profile: Dict) -> str:
        """格式化LinkedIn资料信息"""
        if not profile:
            return "未提供"
        return f"姓名: {profile.get('name', 'N/A')}, 职位: {profile.get('title', 'N/A')}"

    def _format_company_info(self, company: Dict) -> str:
        """格式化公司信息"""
        if not company:
            return "未提供"
        return f"公司: {company.get('name', 'N/A')}, 描述: {company.get('description', 'N/A')}"

    # ===== 模拟数据方法（无API时使用）=====

    def _get_mock_knowledge(self, topic: str, content_type: str) -> Dict:
        """生成模拟知识库数据"""
        return {
            "success": True,
            "items": [
                {
                    "来源类型": "专家观点",
                    "条目标题": f"{topic}核心洞察",
                    "详细内容": f"关于{topic}的最新研究和实践表明，系统化的方法和持续迭代是成功的关键。",
                    "来源出处": "行业专家",
                    "链接地址": "",
                    "可信度评级": "中",
                    "相关度评分": 8,
                },
                {
                    "来源类型": "方法学",
                    "条目标题": "框架模型",
                    "详细内容": "采用结构化思维模式，结合数据驱动的决策方法，可以显著提升效果。",
                    "来源出处": "商业框架",
                    "链接地址": "",
                    "可信度评级": "中",
                    "相关度评分": 7,
                },
            ],
            "source": "mock",
        }

    def _get_mock_content_main(self, topic: str, content_type: str) -> Dict:
        """生成模拟内容主干"""
        mock_content = f"""# {topic}：完整指南

## 核心要点

01. 明确目标
设定清晰的目标是成功的第一步。确保你的目标具体、可衡量、可实现。

02. 制定计划
将大目标分解为小步骤。每个步骤都应该有明确的行动项和时间节点。

03. 执行与优化
持续执行并根据反馈优化。使用数据来指导你的决策。

04. 测量结果
建立关键指标体系。定期review并调整策略。

## 行动号召

你认为哪一步最重要？在评论区分享你的经验！

#{topic.replace(' ', '')} #专业建议 #LinkedIn
"""

        return {
            "success": True,
            "content": mock_content,
            "summary": f"关于{topic}的完整指南，包含4个核心要点和行动号召。",
            "word_count": 100,
        }

    def _get_mock_visual_design(self, topic: str, content_type: str) -> Dict:
        """生成模拟视觉设计规范"""
        return {
            "success": True,
            "design_specs": f"""
## 视觉设计规范 - {topic}

### 布局
- 画布尺寸：1080x1350px (4:5竖版)
- 背景色：#FFFFFF
- 标题区：顶部15%
- 内容区：中间70%
- 行动区：底部15%

### 配色
- 主色：#2d5a3d (深绿色)
- 背景：#FFFFFF (白色)
- 文字：#333333 (深灰色)
- 强调：#FF6B6B, #4ECDC4 (马卡龙色)

### 字体
- 标题：Arial Black, 36pt
- 正文：Arial Regular, 14pt
- 行间距：1.5倍

### 模块设计
- 圆角：6px
- 内边距：15px
- 外边距：20px
""",
            "canvas_size": "1080x1350px",
            "primary_color": "#2d5a3d",
            "background": "#FFFFFF",
        }

    def _get_mock_final_content(
        self,
        topic: str,
        decision: Dict,
        content_main: Dict,
        visual_design: Optional[Dict],
        target_audience: str,
    ) -> Dict:
        """生成模拟最终内容"""
        content = content_main.get("content", "")

        return {
            "success": True,
            "content": content,
            "content_type": decision.get("content_type_cn", "清单要点型"),
            "content_type_en": decision.get("content_type_en", "checklist"),
            "word_count": content_main.get("word_count", 0),
            "target_audience": target_audience,
            "content_quality": "advanced",
            "metadata": {
                "decision": decision,
                "knowledge_count": 2,
                "has_visual_design": visual_design is not None,
                "source": "mock",
                "visual_design_specs": visual_design.get("design_specs", "") if visual_design else None,
            },
        }


# 全局实例
advanced_content_generator = AdvancedContentGenerator()
