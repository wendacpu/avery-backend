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
    LINKEDIN_POST_REFINEMENT_PROMPT,
)
from api.prompts.deep_search_prompts import (
    RESEARCH_SYNTHESIS_PROMPT,
    INFOGRAPHIC_SPEC_PROMPT,
)
# V2升级版提示词（Executive级别）
from api.prompts.deep_search_prompts_v2 import (
    RESEARCH_SYNTHESIS_PROMPT_V2,
    INFOGRAPHIC_SPEC_PROMPT_V2,
    get_deep_search_queries,
)
from api.prompts.content_generation_prompts_v2 import CONTENT_QUALITY_PROMPTS_V2
from api.prompts.infographic_styles import STYLE_LIBRARY, DEFAULT_STYLE_ID
from api.services.audience_mapper import get_target_audience
from api.core.config import settings

logger = logging.getLogger(__name__)


class AdvancedContentGenerator:
    """高级内容生成器 - 完整内容生成工作流"""

    def __init__(self):
        self.client = None
        self.model = "google/gemini-2.5-flash"  # 默认模型

        # 优先级：Groq (免费) > OpenAI > Zhipu GLM > Mock
        # 1. 尝试使用 Groq (免费 Llama 3.3) - 优先级最高
        if settings.groq_api_key and settings.groq_api_key != "your-groq-api-key-here":
            self.client = OpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.3-70b-versatile"  # Llama 3.3 70B (最新)
            logger.info("Groq client initialized for content generation (free)")
        # 2. 尝试使用 OpenAI
        elif settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here":
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                base_url="https://api.openai.com/v1"
            )
            self.model = "gpt-4o"
            logger.info("OpenAI client initialized for content generation")
        # 3. 尝试使用 Zhipu GLM (智谱AI)
        elif settings.zhipu_api_key and settings.zhipu_api_key != "your-zhipu-api-key-here":
            self.client = OpenAI(
                api_key=settings.zhipu_api_key,
                base_url="https://open.bigmodel.cn/api/paas/v4"
            )
            self.model = "glm-4-flash"  # GLM-4-Flash 是高性价比模型
            logger.info("Zhipu GLM-4 client initialized for content generation")
        else:
            logger.warning("未配置文本生成 API 密钥 (GROQ_API_KEY、OPENAI_API_KEY 或 ZHIPU_API_KEY)，将使用模拟数据")

    def generate_content_v2(
        self,
        topic: str,
        job_title: Optional[str] = None,
        research_summary: Optional[Dict[str, Any]] = None,
        target_audience: str = "",
        content_quality: str = "advanced",
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        使用V2提示词生成内容（Executive级别，更高密度）

        特点：
        - Bullet points: 60-80字（Professional）
        - 数量: 10-12个（Professional）
        - 包含: 框架、数据、案例、实施建议
        """
        logger.info(f"使用V2升级版生成内容 - 主题: {topic}, 质量: {content_quality}")

        # 默认值处理
        if not content_quality:
            content_quality = "advanced"
        if not job_title:
            job_title = "other"

        # 推断内容类型（简化版，直接使用清单要点型）
        content_type_cn = "清单要点型"

        # 准备研究摘要文本
        research_text = ""
        if research_summary:
            research_text = json.dumps(research_summary, ensure_ascii=False, indent=2)

        # 使用V2提示词
        # 根据质量等级选择提示词
        if content_quality == "professional":
            quality_key = "professional"
        elif content_quality == "advanced":
            quality_key = "advanced"
        else:
            quality_key = "normal"

        # 从V2提示词中获取（注意：V2只有"清单要点型"的完整示例，其他类型需要扩展）
        prompt_template = CONTENT_QUALITY_PROMPTS_V2.get("清单要点型", {}).get(quality_key)

        if not prompt_template:
            logger.warning(f"V2提示词未找到质量等级 {quality_key}，回退到V1")
            # 回退到V1
            return self.generate_content(
                topic=topic,
                linkedin_profile=None,
                company_info=None,
                additional_context=None,
                job_title=job_title,
                content_quality=content_quality,
                output_format="text_only",
                language=language,
                research_summary=research_summary,
            )

        # 格式化提示词
        prompt = prompt_template.format(
            topic=topic,
            target_audience=target_audience,
            language=language,
            research_summary=research_text[:2000],  # 限制长度
        )

        if not self.client:
            logger.warning("未配置文本生成API，返回模拟内容")
            return self._get_mock_content(topic, content_type_cn)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a thought leader and strategic advisor writing for C-suite executives."
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=3000,  # 增加token限制以获取更详细内容
            )

            result = response.choices[0].message.content

            # 提取内容
            generated_content = result.strip()

            logger.info(f"V2内容生成成功，长度: {len(generated_content)} 字符")

            return {
                "content": generated_content,
                "content_type": content_type_cn,
                "target_audience": target_audience,
                "metadata": {
                    "version": "v2",
                    "content_quality": content_quality,
                    "research_included": bool(research_summary)
                }
            }

        except Exception as e:
            logger.error(f"V2内容生成失败: {str(e)}")
            # 回退到V1
            logger.warning("回退到V1版本的generate_content")
            return self.generate_content(
                topic=topic,
                linkedin_profile=None,
                company_info=None,
                additional_context=None,
                job_title=job_title,
                content_quality=content_quality,
                output_format="text_only",
                language=language,
                research_summary=research_summary,
            )

    def generate_content(
        self,
        topic: str,
        linkedin_profile: Optional[Dict] = None,
        company_info: Optional[Dict] = None,
        additional_context: Optional[str] = None,
        job_title: Optional[str] = None,
        content_quality: Optional[str] = None,
        output_format: Optional[str] = None,
        language: str = "en",
        research_summary: Optional[Dict[str, Any]] = None,
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
            language: 语言（"en" 或 "zh"）

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
            language,
            research_summary,
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
                model=self.model,
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
                model=self.model,
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
        language: str = "en",
        research_summary: Optional[Dict[str, Any]] = None,
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

        research_text = ""
        if research_summary:
            research_text = json.dumps(research_summary, ensure_ascii=False)

        # 如果有知识库检索结果或研究摘要，添加到提示词中
        if knowledge_text or research_text:
            prompt = f"""{prompt}

---

## 知识库参考资料

{knowledge_text}

## 深度研究摘要

{research_text}

请基于以上参考资料生成内容，确保内容有据可依、信息准确。

**语言要求：请使用{"中文" if language == "zh" else "英文"}生成内容。**"""
        else:
            prompt = f"""{prompt}

---

（注：未检索到外部参考资料，请使用自身知识库生成内容）

**语言要求：请使用{"中文" if language == "zh" else "英文"}生成内容。**"""

        if not self.client:
            return self._get_mock_content_main(topic, content_type_cn, language)

        try:
            # 根据语言选择不同的 system message
            content_type_en = CONTENT_TYPE_MAPPING.get(content_type_cn, "content")
            quality_str = QUALITY_MAPPING.get(content_quality, content_quality)

            if language == "zh":
                system_message = f"你是LinkedIn专业内容创作者，擅长创作{content_type_cn}内容（{quality_str}质量）。"
            else:
                system_message = f"You are a LinkedIn professional content creator specializing in {content_type_en} content ({quality_str} quality)."

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_message,
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
            return self._get_mock_content_main(topic, content_type_cn, language)

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
                model=self.model,
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
            # 获取原始详细内容
            detailed_content = content_main.get("content", "")

            # 精华提炼：生成适合 LinkedIn 的精简 POST 文本
            # 从世界前 0.1% 商业领袖的视角提炼核心洞察
            refined_post = self._refine_linkedin_post(
                topic=topic,
                original_content=detailed_content,
            )

            # 使用精华提炼后的内容作为最终内容
            final_content = refined_post

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
                    "refined": True,  # 标记已进行精华提炼
                    "detailed_content_length": len(detailed_content.split()),  # 原始内容字数
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

    def _refine_linkedin_post(
        self,
        topic: str,
        original_content: str,
    ) -> str:
        """
        精华提炼：将详细内容转化为精简的、有深度的 LinkedIn POST

        从世界前 0.1% 商业领袖的视角提炼核心洞察
        """
        if not self.client:
            # 无 API 时，返回原始内容（截取前500字）
            return original_content[:500] + "..." if len(original_content) > 500 else original_content

        try:
            # 使用精华提炼提示词
            prompt = LINKEDIN_POST_REFINEMENT_PROMPT.format(
                topic=topic,
                original_content=original_content[:2000],  # 限制输入长度
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a world-class business thinker in the top 0.1%. You transform complex ideas into profound, concise wisdom.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,  # 稍高的创造性
                max_tokens=500,  # 限制输出长度
            )

            refined_post = response.choices[0].message.content.strip()
            logger.info("LinkedIn POST 精华提炼完成")

            return refined_post

        except Exception as e:
            logger.error(f"精华提炼失败: {str(e)}")
            # 失败时返回原始内容（截取）
            return original_content[:500] + "..." if len(original_content) > 500 else original_content

    # ===== V2升级版方法：Executive级别内容生成 =====

    def synthesize_research_v2(
        self,
        topic: str,
        sources: List[Dict[str, Any]],
        target_audience: str,
        include_charts: bool,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        使用V2提示词进行深度研究综合（Executive级别）

        特点：
        - 更深刻的市场分析
        - 战略性洞察（非显而易见）
        - 带行业基准的数据点
        - 战略影响分析
        """
        if not sources:
            return {
                "summary": "",
                "market_context": "",
                "strategic_insights": [],
                "key_numbers": [],
                "strategic_implications": [],
                "chart_candidates": [],
                "expert_quotes": [],
                "citations": [],
            }

        # V2使用更多源（10个而不是8个）
        sources_text = "\n".join([
            f"- {s.get('title','')} | {s.get('url','')}\n{s.get('content','')[:1500]}"
            for s in sources[:10]
        ])

        if not self.client:
            return {
                "summary": "",
                "market_context": "",
                "strategic_insights": [],
                "key_numbers": [],
                "strategic_implications": [],
                "chart_candidates": [],
                "expert_quotes": [],
                "citations": [{"title": s.get("title", ""), "url": s.get("url", "")} for s in sources[:5]],
            }

        prompt = RESEARCH_SYNTHESIS_PROMPT_V2.format(
            topic=topic,
            target_audience=target_audience,
            include_charts=str(include_charts),
            sources_text=sources_text,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior research analyst at McKinsey/Bain/BCG level."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,  # 增加token限制以获取更详细内容
            )

            result = response.choices[0].message.content
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()

            data = json.loads(result)
            if not include_charts:
                data["chart_candidates"] = []
            return data
        except Exception as e:
            logger.error(f"V2 Research synthesis failed: {e}")
            # 回退到V1
            logger.warning("回退到V1版本的synthesize_research")
            return self.synthesize_research(topic, sources, target_audience, include_charts, language)

    def generate_infographic_spec_v2(
        self,
        topic: str,
        research_summary: Dict[str, Any],
        content_quality: str,
        include_charts: bool,
        style_id: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        使用V2提示词生成信息图规范（更高密度）

        特点：
        - 更多模块（Professional: 11-13个）
        - 更详细的每个模块（30-50字）
        - 优化的排版（20% white space）
        - 修复的图表竖排文字bug
        """
        if not self.client:
            return {
                "title": topic,
                "subtitle": "",
                "tagline": "",
                "modules": [],
                "chart": {"enabled": False},
                "footer": "",
            }

        style_id = style_id or DEFAULT_STYLE_ID
        prompt = INFOGRAPHIC_SPEC_PROMPT_V2.format(
            topic=topic,
            content_quality=content_quality,
            include_charts=str(include_charts),
            style_id=style_id,
            research_summary=json.dumps(research_summary, ensure_ascii=False),
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a world-class information designer specializing in executive communications."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2500,  # 增加token限制
            )

            result = response.choices[0].message.content
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()

            data = json.loads(result)

            # 确保图表没有竖排文字
            if include_charts and data.get("chart", {}).get("enabled"):
                chart = data["chart"]
                # 验证标签长度
                if "values" in chart:
                    for v in chart["values"]:
                        if "x" in v and len(v["x"]) > 10:
                            v["x"] = v["x"][:10] + "..."
                        if "annotation" in v and len(v["annotation"]) > 15:
                            v["annotation"] = v["annotation"][:15] + "..."

            if not include_charts and "chart" in data:
                data["chart"]["enabled"] = False
            return data
        except Exception as e:
            logger.error(f"V2 Infographic spec generation failed: {e}")
            # 回退到V1
            logger.warning("回退到V1版本的generate_infographic_spec")
            return self.generate_infographic_spec(topic, research_summary, content_quality, include_charts, style_id, language)

    # ===== 原有方法保持不变 =====

    def synthesize_research(
        self,
        topic: str,
        sources: List[Dict[str, Any]],
        target_audience: str,
        include_charts: bool,
        language: str = "en",
    ) -> Dict[str, Any]:
        if not sources:
            return {
                "summary": "",
                "key_insights": [],
                "key_numbers": [],
                "chart_candidates": [],
                "citations": [],
            }

        sources_text = "\n".join([
            f"- {s.get('title','')} | {s.get('url','')}\n{s.get('content','')[:1200]}"
            for s in sources[:8]
        ])

        if not self.client:
            return {
                "summary": "",
                "key_insights": [],
                "key_numbers": [],
                "chart_candidates": [],
                "citations": [{"title": s.get("title", ""), "url": s.get("url", "")} for s in sources[:5]],
            }

        prompt = RESEARCH_SYNTHESIS_PROMPT.format(
            topic=topic,
            target_audience=target_audience,
            include_charts=str(include_charts),
            sources_text=sources_text,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a rigorous research analyst."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1500,
            )

            result = response.choices[0].message.content
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()

            data = json.loads(result)
            if not include_charts:
                data["chart_candidates"] = []
            return data
        except Exception as e:
            logger.error(f"Research synthesis failed: {e}")
            return {
                "summary": "",
                "key_insights": [],
                "key_numbers": [],
                "chart_candidates": [],
                "citations": [{"title": s.get("title", ""), "url": s.get("url", "")} for s in sources[:5]],
            }

    def generate_infographic_spec(
        self,
        topic: str,
        research_summary: Dict[str, Any],
        content_quality: str,
        include_charts: bool,
        style_id: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        if not self.client:
            return {
                "title": topic,
                "subtitle": "",
                "modules": [],
                "chart": {"enabled": False},
                "footer": "",
            }

        style_id = style_id or DEFAULT_STYLE_ID
        prompt = INFOGRAPHIC_SPEC_PROMPT.format(
            topic=topic,
            content_quality=content_quality,
            include_charts=str(include_charts),
            style_id=style_id,
            research_summary=json.dumps(research_summary, ensure_ascii=False),
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise information designer."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1200,
            )

            result = response.choices[0].message.content
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()

            data = json.loads(result)
            if not include_charts and "chart" in data:
                data["chart"]["enabled"] = False
            return data
        except Exception as e:
            logger.error(f"Infographic spec generation failed: {e}")
            return {
                "title": topic,
                "subtitle": "",
                "modules": [],
                "chart": {"enabled": False},
                "footer": "",
            }

    def build_infographic_image_prompt(
        self,
        spec: Dict[str, Any],
        style_id: Optional[str] = None,
        include_charts: bool = True,
    ) -> str:
        style_id = style_id or DEFAULT_STYLE_ID
        style_block = STYLE_LIBRARY.get(style_id, STYLE_LIBRARY[DEFAULT_STYLE_ID])

        title = spec.get("title", "")
        subtitle = spec.get("subtitle", "")
        modules = spec.get("modules", [])
        chart = spec.get("chart", {})
        footer = spec.get("footer", "")

        modules_text = "\n".join([
            f"- {m.get('id','')}: {m.get('title','')} — {m.get('phrase','')}"
            for m in modules
        ])

        chart_text = ""
        if include_charts and chart and chart.get("enabled", True):
            values = chart.get("values", [])
            chart_text = (
                f"\nChart: {chart.get('type','')} | {chart.get('title','')}\n"
                f"X: {chart.get('x_label','')} | Y: {chart.get('y_label','')}\n"
                f"Values: {values}"
            )

        prompt = f"""Create a high-density, professional infographic for LinkedIn.
Title: {title}
Subtitle: {subtitle}

Modules:
{modules_text}
{chart_text}

Footer: {footer}

{style_block}

Aspect Ratio: 3:4 (Portrait)
All text must be legible. Use short phrases, high contrast, and precise alignment.
"""
        return prompt

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

    def _get_mock_content_main(self, topic: str, content_type: str, language: str = "en") -> Dict:
        """生成模拟内容主干"""
        if language == "en":
            mock_content = f"""# {topic}: Complete Guide

## Key Points

01. Define Clear Goals
Set clear and measurable objectives is the first step to success. Ensure your goals are specific, measurable, and achievable.

02. Create a Plan
Break down big goals into small steps. Each step should have clear action items and timelines.

03. Execute and Optimize
Execute continuously and optimize based on feedback. Use data to guide your decisions.

04. Measure Results
Establish key metrics. Review regularly and adjust strategies.

## Call to Action

Which step do you think is most important? Share your experience in the comments!

#{topic.replace(' ', '')} #ProfessionalAdvice #LinkedIn
"""
            summary = f"A complete guide to {topic}, covering 4 key points and call to action."
        else:
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
            summary = f"关于{topic}的完整指南，包含4个核心要点和行动号召。"

        return {
            "success": True,
            "content": mock_content,
            "summary": summary,
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
