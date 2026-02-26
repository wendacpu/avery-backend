"""
AI 图片生成服务
使用 Novita AI API 生成配图
"""
import logging
import httpx
from typing import Optional, Dict, Any, List

from api.core.config import settings

logger = logging.getLogger(__name__)


class ImageGenerator:
    """AI 图片生成器 - 使用 Novita AI"""

    def __init__(self):
        self.model = settings.image_model or "gemini-2.5-flash-image"
        self.api_key = settings.novita_api_key
        self.api_base = "https://api.novita.ai/v3"

        if self.api_key and self.api_key != "your-novita-api-key-here":
            logger.info(f"Novita AI API initialized, using model: {self.model}")
        else:
            logger.warning("未配置 Novita API 密钥，将使用模拟图片")

    def generate_image(
        self,
        content: str,
        topic: str,
        content_type: str,
        detailed_prompt: Optional[str] = None,
        visual_design_specs: Optional[str] = None,
        content_quality: Optional[str] = "advanced"
    ) -> str:
        """
        根据内容生成配图

        Args:
            content: 生成的文字内容（用于提取关键信息）
            topic: 主题
            content_type: 内容类型
            detailed_prompt: 详细的图片生成提示词（优先使用）
            visual_design_specs: 视觉设计文案（来自工作流）
            content_quality: 内容质量等级 (normal/advanced/professional)

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
                visual_design_specs=visual_design_specs,
                content_quality=content_quality
            )
        # 其次使用详细的图片提示词
        elif detailed_prompt:
            prompt = detailed_prompt
        else:
            # 构建图片生成提示词
            prompt = self._build_image_prompt(topic, content_type, content)

        # 尝试使用 Novita API
        if self.api_key and self.api_key != "your-novita-api-key-here":
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
        visual_design_specs: str,
        content_quality: str = "advanced"
    ) -> str:
        """
        基于实际内容生成图片提示词

        从生成的文章中提取关键信息，结合视觉设计规范，生成图片提示词

        Args:
            content: 生成的文字内容
            topic: 主题
            content_type: 内容类型
            visual_design_specs: 视觉设计文案
            content_quality: 内容质量等级 (normal/advanced/professional)
        """
        # 从内容中提取关键信息
        content_info = self._extract_content_key_points(content, topic)

        # 直接使用传入的英文内容
        title = content_info.get("title", topic)

        # 根据质量等级决定模块数量（信息密度递增）
        quality_module_count = {
            "normal": (5, 6),      # 5-6 个模块
            "advanced": (7, 8),    # 7-8 个模块
            "professional": (9, 10)  # 9-10 个模块
        }
        min_modules, max_modules = quality_module_count.get(content_quality, (7, 8))
        key_points = content_info.get("key_points", [])[:max_modules]

        # 内容类型映射（中文 -> 英文）
        content_type_map = {
            "分类展示型": "Categorized Display",
            "流程步骤型": "Process Steps",
            "清单要点型": "Checklist",
            "对比表格型": "Comparison Table",
            "工具列表型": "Tool List"
        }
        content_type_en = content_type_map.get(content_type, "Professional Content")

        # 生成简短副标题（确保一行显示）
        # 移除常见的长前缀，简化表述
        subtitle_words = topic.split()
        if len(subtitle_words) > 6:
            short_subtitle = " ".join(subtitle_words[:5]) + "..."
        else:
            short_subtitle = topic

        # 构建基础提示词 - 移除所有排版术语
        prompt = f"""Create a professional LinkedIn infographic about '{topic}'.

**LAYOUT STRUCTURE:**
Tri-Section Hierarchy:
1. Header Zone: Main title + one-line subtitle + slogan
2. Content Zone: Modular grid section with {len(key_points)} information modules
3. Call-to-Action Zone: Footer with download/subscription info
Canvas size: vertical format suitable for LinkedIn (aspect ratio 3 to 4)

**GRID SYSTEM:**
- Modular Card Layout: multi-column grid with information modules
- Independent Units: Each concept in rounded rectangular containers with subtle borders
- Optimize information density with scannable readability

**COLOR PALETTE:**
- Base Layer: White or light beige background
- Module Backgrounds: Soft pastel tones - light green, pale yellow, soft pink, sky blue (cycle through these)
- Accent Color: Deep forest green for header and key titles
- Highlight Tone: Orange for secondary tags or example labels
- Text Color: Dark charcoal for maximum legibility

**TYPOGRAPHY:**
- Main Title: Extra bold, large size, forest green color
- Subtitle: Bold, medium size, one line only
- Module Titles: Bold with accent colors
- Body Text: Regular size with comfortable line spacing
- Annotation Labels: Bold small size for labels like GOAL, TIP, EXAMPLE
- Most text left-aligned for natural reading flow

**VISUAL ELEMENTS:**
- Simple icons: outline style with consistent sizing throughout
- Decorative elements: dashed lines for soft grouping, numbered circles for sequence
- Illustrations: include relevant small illustrations for each module (e.g., gear icons for processes, charts for data, light bulbs for ideas)
- Visual separators: thin lines or subtle dividers between sections

**WHITE SPACE & BALANCE:**
- Ensure adequate white space (about one-third of canvas empty)
- Consistent spacing between modules
- Comfortable padding inside each module
- Balanced margins around edges

**CONTENT TO DISPLAY:**

- Main Title: {title}
- Subtitle: {short_subtitle}
- Slogan: Practical actionable insights

**CONTENT MODULES ({content_type_en}):**
"""

        # 添加关键内容 - 使用高密度信息结构
        for i, point in enumerate(key_points, 1):
            color_name = ["light green", "pale yellow", "soft pink", "sky blue"][i % 4]
            # 移除颜色代码中的 # 符号
            prompt += f"Module {i} [Background: {color_name}]: {point}\n"

        # 添加页脚
        prompt += """
**FOOTER (CTA):**
- Download or subscribe for complete guide
- Professional branding

**STYLE KEYWORDS:**
Clean professional infographic, vector illustration, high-resolution graphic, modern layout, flat design, soft pastel colors, modular card grid, business style.

Create this as a clean, modern, business infographic suitable for LinkedIn. All text should be legible, well-organized, and free of any technical specifications or measurements. Use English text only.
"""

        logger.info(f"Content-based image prompt: {prompt[:500]}...")
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
        """使用 Novita AI 生成图片 - Gemini 2.5 Flash"""
        if not self.api_key:
            raise Exception("Novita API Key 未配置")

        try:
            # 使用正确的 endpoint 和格式
            # Endpoint: POST https://api.novita.ai/v3/gemini-2.5-flash-image-text-to-image
            url = f"{self.api_base}/{self.model}-text-to-image"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            # Gemini 2.5 Flash 的请求格式
            payload = {
                "prompt": prompt,
                "aspect_ratio": "3:4"  # 竖版，适合 LinkedIn
            }

            logger.info(f"调用 Gemini API: {url}")
            logger.info(f"提示词长度: {len(prompt)}")

            # 发送请求
            response = httpx.post(
                url,
                json=payload,
                headers=headers,
                timeout=60.0
            )

            # 检查响应
            response.raise_for_status()

            # 解析响应 - Gemini 格式: {"image_urls": ["url1", "url2"]}
            result = response.json()

            if "image_urls" in result and len(result["image_urls"]) > 0:
                image_url = result["image_urls"][0]
                logger.info(f"Gemini 图片生成成功: {image_url}")
                return image_url
            else:
                raise Exception(f"响应格式错误: {result}")

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 错误 {e.response.status_code}: {e.response.text}")
            raise Exception(f"Novita API HTTP {e.response.status_code}: {e.response.text[:200]}")
        except Exception as e:
            logger.error(f"Gemini API 调用失败: {str(e)}")
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
