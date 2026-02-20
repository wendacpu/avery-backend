"""
AI 图片生成服务
使用 Novita AI API 生成配图
"""
import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI

from api.core.config import settings

logger = logging.getLogger(__name__)


class ImageGenerator:
    """AI 图片生成器 - 使用 Novita AI"""

    def __init__(self):
        self.client = None
        self.model = settings.image_model or "gemini-2.5-flash-image"

        # 使用 Novita AI API
        if settings.novita_api_key and settings.novita_api_key != "your-novita-api-key-here":
            self.client = OpenAI(
                api_key=settings.novita_api_key,
                base_url="https://api.novita.ai/v1"
            )
            logger.info("Novita AI client initialized")

        if not self.client:
            logger.warning("未配置 Novita API 密钥，将使用模拟图片")

    def generate_image(
        self,
        content: str,
        topic: str,
        content_type: str,
        detailed_prompt: Optional[str] = None,
        visual_design_specs: Optional[str] = None
    ) -> str:
        """
        根据内容生成配图

        Args:
            content: 生成的文字内容（用于提取关键信息）
            topic: 主题
            content_type: 内容类型
            detailed_prompt: 详细的图片生成提示词（优先使用）
            visual_design_specs: 视觉设计文案（来自工作流）

        Returns:
            图片 URL 或 base64 编码
        """

        # 优先使用视觉设计文案 + 实际内容
        if visual_design_specs:
            # 从实际内容中提取关键信息，结合视觉设计文案生成图片提示词
            prompt = self._generate_content_based_image_prompt(
                content=content,
                topic=topic,
                content_type=content_type,
                visual_design_specs=visual_design_specs
            )
        # 其次使用详细的图片提示词
        elif detailed_prompt:
            prompt = detailed_prompt
        else:
            # 构建图片生成提示词
            prompt = self._build_image_prompt(topic, content_type, content)

        # 尝试使用 Novita API
        if self.client:
            try:
                return self._generate_with_novita(prompt)
            except Exception as e:
                logger.error(f"Novita API 调用失败: {str(e)}")
                # 返回模拟图片
                return self._get_mock_image_url(topic, content_type)
        else:
            return self._get_mock_image_url(topic, content_type)

    def _build_image_prompt(self, topic: str, content_type: str, content: str) -> str:
        """构建图片生成提示词"""

        # 从内容中提取关键词（简单实现）
        style_prompts = {
            "industry_trends": "professional business infographic style, clean modern design, data visualization",
            "position_insight": "professional business photo, modern office setting, leadership theme",
            "custom": "professional modern design, clean aesthetic, business context"
        }

        base_prompt = style_prompts.get(content_type, "professional business design")

        # 构建完整提示词
        full_prompt = (
            f"Professional LinkedIn image about '{topic}'. "
            f"{base_prompt}. "
            f"Minimalist design with good use of white space. "
            f"Professional color scheme suitable for business audience. "
            f"No text overlay. High quality, 1024x1024."
        )

        return full_prompt

    def _generate_content_based_image_prompt(
        self,
        content: str,
        topic: str,
        content_type: str,
        visual_design_specs: str
    ) -> str:
        """
        基于实际内容生成图片提示词

        从生成的文章中提取关键信息，结合视觉设计规范，生成图片提示词
        """
        # 从内容中提取关键信息
        content_info = self._extract_content_key_points(content, topic)

        # 构建图片提示词
        prompt_parts = []

        # 1. 主题和内容类型
        prompt_parts.append(f"Professional LinkedIn infographic about '{topic}'")
        prompt_parts.append(f"Content Type: {content_type.replace('_', ' ')}")

        # 2. 实际内容（要展示在图片上的信息）
        if content_info.get("title"):
            prompt_parts.append(f"Title: {content_info['title']}")

        if content_info.get("key_points"):
            # 将关键点转换为逗号分隔的列表
            points_str = "; ".join(content_info["key_points"][:5])  # 最多5个关键点
            prompt_parts.append(f"Key Content: {points_str}")

        # 3. 视觉设计规范（从 visual_design_specs 提取）
        design_specs = self._extract_design_specs(visual_design_specs)
        prompt_parts.extend(design_specs)

        # 4. 风格关键词
        prompt_parts.extend([
            "Professional business infographic style",
            "Clean, modern, minimalist design",
            "4:5 portrait ratio (1080x1350px)",
            "Vector illustration style",
            "High quality",
            "Swiss style layout"
        ])

        # 组合提示词
        prompt = ". ".join(filter(None, prompt_parts)) + "."

        logger.info(f"Content-based image prompt: {prompt[:300]}...")
        return prompt

    def _extract_content_key_points(self, content: str, topic: str) -> Dict[str, Any]:
        """
        从生成的内容中提取关键信息

        包括：标题、关键点、数据等
        """
        import re

        result = {
            "title": topic,
            "key_points": [],
            "statistics": [],
            "examples": []
        }

        # 提取标题（通常是第一行或 # 开头的行）
        lines = content.split('\n')
        for line in lines[:10]:  # 只看前10行
            line = line.strip()
            if line.startswith('#'):
                result["title"] = line.lstrip('#').strip()
                break
            elif line and len(line) < 100 and not line.startswith('-'):
                result["title"] = line
                break

        # 提取关键点（通常是列表项）
        # 匹配模式：01.、-、1.、• 等
        point_patterns = [
            r'^\d{1,2}\.\s+(.+)',           # 01. 或 1.
            r'^-\s+(.+)',                    # -
            r'^•\s+(.+)',                    # •
            r'^\*\s+(.+)',                   # *
        ]

        for line in lines:
            line = line.strip()
            for pattern in point_patterns:
                match = re.match(pattern, line)
                if match:
                    point_text = match.group(1).strip()
                    # 限制长度，避免过长
                    if len(point_text) < 200 and point_text:
                        result["key_points"].append(point_text)
                    break

            # 最多提取 10 个关键点
            if len(result["key_points"]) >= 10:
                break

        # 如果没有提取到关键点，使用句子的前几句
        if not result["key_points"]:
            sentences = re.split(r'[。！？.!?]', content)
            for sentence in sentences[:5]:
                sentence = sentence.strip()
                if 20 < len(sentence) < 200:
                    result["key_points"].append(sentence)

        # 提取数据/百分比（可选）
        stats_pattern = r'(\d+%\s+|\d+倍|\d+\+?\s*个?)'
        stats = re.findall(stats_pattern, content)
        if stats:
            result["statistics"] = stats[:5]  # 最多5个数据

        logger.info(f"Extracted {len(result['key_points'])} key points from content")
        return result

    def _extract_design_specs(self, visual_design_specs: str) -> List[str]:
        """
        从视觉设计文案中提取设计规范
        """
        specs = []

        # 颜色规范
        if "#2d5a3d" in visual_design_specs or "#006633" in visual_design_specs:
            specs.append("Deep forest green accent color (#2d5a3d)")

        if any(color in visual_design_specs for color in ["#e6f4ea", "#fff2cc", "#ffe6e6", "#e6f7fa"]):
            specs.append("Soft macaron color palette (light green, pale yellow, soft pink, sky blue)")

        # 背景色
        if "#FFFFFF" in visual_design_specs or "#F5F5F0" in visual_design_specs:
            specs.append("White or light beige background")

        # 字体
        if "Arial Black" in visual_design_specs:
            specs.append("Bold typography for titles")

        # 布局
        if "modular" in visual_design_specs.lower() or "grid" in visual_design_specs.lower():
            specs.append("Modular card grid layout")

        if "8px corner radius" in visual_design_specs or "rounded" in visual_design_specs.lower():
            specs.append("Rounded corners on modules")

        # 留白
        if "30%" in visual_design_specs:
            specs.append("Generous white space (30% of canvas)")

        return specs

    def _generate_with_novita(self, prompt: str) -> str:
        """使用 Novita AI 生成图片"""
        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size="1024x1024",
                n=1,
                response_format="url"
            )

            # 返回图片 URL
            image_url = response.data[0].url
            logger.info(f"Novita AI 图片生成成功: {image_url}")
            return image_url

        except Exception as e:
            logger.error(f"Novita AI 生成失败: {str(e)}")
            raise

    def _get_mock_image_url(self, topic: str, content_type: str) -> str:
        """获取模拟图片 URL（开发测试用）"""

        # 使用 picsum.photos 提供的随机图片（更稳定的服务）
        # 根据主题和类型选择不同的图片

        # 使用随机种子确保相同主题获得相同图片
        seed = abs(hash(topic + content_type)) % 1000

        # 使用 picsum.photos 作为替代
        # 注意：实际生产环境应该使用 DALL-E 或其他 AI 图片服务
        return f"https://picsum.photos/1024/1024?random={seed}"


# 全局实例
image_generator = ImageGenerator()
