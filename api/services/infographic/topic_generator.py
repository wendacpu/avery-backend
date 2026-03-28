"""
Topic Generator Module
Generates infographic topics using CTO/CEO dual-perspective approach with "how-to" framework.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI

from api.core.config import settings

logger = logging.getLogger(__name__)


class Perspective(Enum):
    """Content perspective types"""
    CTO = "cto"              # Technical/implementation focus
    CEO = "ceo"              # Business/strategy focus
    HYBRID = "hybrid"        # Balanced approach
    CMO = "cmo"              # Marketing & growth focus
    CFO = "cfo"              # Financial & ROI focus
    FOUNDER = "founder"      # Vision & disruption focus
    VP_PRODUCT = "vp_product"         # Product & UX thinking
    VP_ENGINEERING = "vp_engineering" # Eng org & systems
    INVESTOR = "investor"    # ROI & market lens


def resolve_perspective(value: str) -> "Perspective":
    """Safely resolve a string to a Perspective, defaulting to HYBRID on unknown values."""
    try:
        return Perspective(value.lower())
    except ValueError:
        logger.warning(f"Unknown perspective '{value}', falling back to HYBRID")
        return Perspective.HYBRID


@dataclass
class GeneratedTopic:
    """Generated topic with metadata"""
    topic: str
    perspective: Perspective
    framework: str  # e.g., "how-to", "listicle", "comparison"
    key_points: List[str]
    target_audience: str
    estimated_engagement: int
    content_structure: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "topic": self.topic,
            "perspective": self.perspective.value,
            "framework": self.framework,
            "key_points": self.key_points,
            "target_audience": self.target_audience,
            "estimated_engagement": self.estimated_engagement,
            "content_structure": self.content_structure
        }


class TopicGenerator:
    """
    Topic Generation Engine

    Uses CTO/CEO dual-perspective approach with "how-to" framework
    to generate engaging infographic topics.

    Workflow Requirements:
    - All English content
    - High information density
    - Actionable insights
    """

    def __init__(self):
        """Initialize topic generator"""
        self.client: Optional[OpenAI] = None
        self._init_client()
        logger.info("TopicGenerator initialized")

    def _init_client(self):
        """Initialize OpenAI client if API key available"""
        api_key = None
        base_url = None

        # Try Zhipu first (reliable domestic alternative to avoid 403 Forbidden)
        if settings.zhipu_api_key and settings.zhipu_api_key != "your-zhipu-api-key-here":
            api_key = settings.zhipu_api_key
            base_url = "https://open.bigmodel.cn/api/paas/v4/"
        # Try Groq next
        elif settings.groq_api_key and settings.groq_api_key != "your-groq-api-key-here":
            api_key = settings.groq_api_key
            base_url = "https://api.groq.com/openai/v1"
        # Fallback to OpenAI
        elif settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here":
            api_key = settings.openai_api_key

        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            logger.info(f"LLM client initialized: {base_url or 'OpenAI'}")

    def generate(
        self,
        industry_context: str,
        job_title: str,
        perspective: Perspective = Perspective.HYBRID,
        framework: str = "how-to",
        count: int = 1
    ) -> List[GeneratedTopic]:
        """
        Generate infographic topics

        Args:
            industry_context: Industry background/context from client materials
            job_title: Target job title (e.g., "ceo", "cto", "product_manager")
            perspective: Content perspective (CTO/CEO/HYBRID)
            framework: Content framework (how-to, listicle, comparison)
            count: Number of topics to generate

        Returns:
            List of GeneratedTopic objects
        """
        logger.info(f"Generating {count} topics: {perspective.value} perspective, {framework} framework")

        if self.client:
            return self._generate_with_llm(
                industry_context, job_title, perspective, framework, count
            )
        else:
            logger.warning("No LLM client available, using template-based generation")
            return self._generate_template_based(
                industry_context, job_title, perspective, framework, count
            )

    def _generate_with_llm(
        self,
        industry_context: str,
        job_title: str,
        perspective: Perspective,
        framework: str,
        count: int
    ) -> List[GeneratedTopic]:
        """Generate topics using LLM"""
        # Build prompt
        prompt = self._build_generation_prompt(
            industry_context, job_title, perspective, framework, count
        )

        try:
            model_name = "gpt-4"
            if "groq" in str(self.client.base_url):
                model_name = "llama-3.3-70b-versatile"
            elif "bigmodel.cn" in str(self.client.base_url):
                model_name = "glm-4-flash"

            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(job_title)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )

            import json
            import re
            content = response.choices[0].message.content
            
            # Robust JSON extraction: look for the first { and the last }
            # LLMs sometimes wrap JSON in markdown blocks or add preamble
            try:
                # Find the actual JSON object in the string
                json_match = re.search(r"(\{.*\})", content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    result = json.loads(json_str)
                else:
                    # Fallback to direct load
                    result = json.loads(content)
            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing error: {je}. Raw content: {content[:200]}...")
                raise

            return self._parse_llm_response(result, perspective, framework)

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._generate_template_based(
                industry_context, job_title, perspective, framework, count
            )

    def _get_system_prompt(self, job_title: str) -> str:
        """Get system prompt for LLM"""
        return f"""You are an expert content strategist specializing in LinkedIn infographic creation.

Your task is to generate engaging, high-value infographic topics that:

1. Are written in English only
2. Follow a "how-to" framework with actionable steps
3. Have high information density (no fluff)
4. Provide practical, implementable insights
5. CRITICAL: ROLE CONSISTENCY. Every topic MUST be written specifically for the target audience: {job_title}.
6. CRITICAL: THEMATIC DIVERSITY. While the role is the same, generate 3 unique thematic angles:
   - Angle A: Strategic Vision & Maturity (Planning for the {job_title})
   - Angle B: Operational Execution (Action plan for the {job_title}'s team)
   - Angle C: Performance & Data Benchmarks (KPIs that matter to the {job_title})
7. CRITICAL: Anchoring. All topics MUST be strictly derived from the user's provided context and research data.

Example of GOOD key point:
"Establish automated data pipelines: Set up ETL processes using Apache Airflow or similar tools. Schedule daily incremental loads from source systems. Implement data quality checks at each stage. Monitor pipeline performance and set up alerts for failures."

Example of BAD key point:
"Build good data infrastructure" (too vague, no actionable guidance)

Focus on topics that professionals would save and share."""

    def _build_generation_prompt(
        self,
        industry_context: str,
        job_title: str,
        perspective: Perspective,
        framework: str,
        count: int
    ) -> str:
        """Build generation prompt"""
        perspective_desc = {
            Perspective.CTO: "Focus on technical implementation, tools, and engineering best practices. Readers are engineers and technical leaders",
            Perspective.CEO: "Focus on business strategy, ROI, competitive advantage, and board-level decisions",
            Perspective.HYBRID: "Balance technical depth with business value — useful for both engineers and executives",
            Perspective.CMO: "Focus on marketing strategy, demand generation, brand positioning, and growth metrics",
            Perspective.CFO: "Focus on financial ROI, cost optimisation, budget allocation, and risk management",
            Perspective.FOUNDER: "Focus on vision, product-market fit, fundraising narrative, and disruption angles",
            Perspective.VP_PRODUCT: "Focus on product strategy, user experience, roadmap prioritisation, and product-led growth",
            Perspective.VP_ENGINEERING: "Focus on engineering org design, developer productivity, platform architecture, and team scaling",
            Perspective.INVESTOR: "Focus on market opportunity, unit economics, competitive moats, and investment thesis",
        }

        return f"""Generate {count} infographic topic(s) for LinkedIn content.

**Industry Context:** {industry_context[:4000]}

**Target Audience:** {job_title}
**Perspective:** {perspective_desc[perspective]}
**Framework:** {framework.upper()} - Step-by-step actionable guidance

REQUIREMENTS:
- Action-oriented title (10-15 words)
- 4-5 detailed key points (NOT 7-9 - keep it focused)
- Each key point MUST be 3-5 detailed sentences of actionable guidance
- Focus on "HOW-TO" specific steps, not "why" explanations
- High information density with practical, implementable insights
- All content must be in English
- Professional but conversational tone

Return JSON in this format:
{{
  "topics": [
    {{
      "topic": "Clear, action-oriented title (10-15 words)",
      "key_points": [
        "Detailed point 1: 3-5 sentences of specific, actionable guidance",
        "Detailed point 2: 3-5 sentences explaining exact steps to take",
        "Detailed point 3: 3-5 sentences with implementable recommendations",
        "Detailed point 4: 3-5 sentences of practical guidance"
      ],
      "target_audience": "Specific audience description",
      "estimated_engagement": 85,
      "content_structure": {{
        "type": "{framework}",
        "sections": ["Introduction", "Core Content (4-5 detailed points)", "Key Takeaway"]
      }}
    }}
  ]
}}"""

    def _parse_llm_response(
        self,
        response: Dict[str, Any],
        perspective: Perspective,
        framework: str
    ) -> List[GeneratedTopic]:
        """Parse LLM response into GeneratedTopic objects"""
        topics = []

        for item in response.get("topics", []):
            topics.append(GeneratedTopic(
                topic=item.get("topic", ""),
                perspective=perspective,
                framework=framework,
                key_points=item.get("key_points", []),
                target_audience=item.get("target_audience", ""),
                estimated_engagement=item.get("estimated_engagement", 70),
                content_structure=item.get("content_structure", {})
            ))

        return topics

    def _generate_template_based(
        self,
        industry_context: str,
        job_title: str,
        perspective: Perspective,
        framework: str,
        count: int
    ) -> List[GeneratedTopic]:
        """Generate topics using template-based approach (fallback)"""
        topics = []

        # Template structures
        templates = {
            Perspective.CTO: [
                "How to Build Scalable {industry} Architecture",
                "Technical Implementation Guide for {industry}",
                "Engineering Best Practices for {industry} Systems",
                "Data Security and Compliance in {industry}"
            ],
            Perspective.CEO: [
                "Business Strategy Framework for {industry}",
                "ROI-Driven Decision Making in {industry}",
                "Leadership Playbook for {industry} Growth",
                "Market Disruptions in {industry} by 2025"
            ],
            Perspective.HYBRID: [
                "Complete Guide to {industry} Success",
                "Balancing Technical and Business in {industry}",
                "Strategic Implementation for {industry}",
                "The Future of {industry} Architecture"
            ]
        }

        # Key point templates
        point_templates = {
            "how-to": [
                "Assess current state and define metrics",
                "Build cross-functional alignment",
                "Implement core capabilities",
                "Measure and iterate continuously"
            ]
        }

        selected_templates = templates.get(perspective, templates[Perspective.HYBRID])

        for i in range(count):
            template = selected_templates[i % len(selected_templates)]
            topic = template.format(industry=industry_context.split()[0] if industry_context else "Your Industry")

            topics.append(GeneratedTopic(
                topic=topic,
                perspective=perspective,
                framework=framework,
                key_points=point_templates.get(framework, point_templates["how-to"]),
                target_audience=f"{job_title} professionals",
                estimated_engagement=75,
                content_structure={"type": framework, "sections": ["Intro", "Content", "Conclusion"]}
            ))

        return topics

    def generate_dual_perspective(
        self,
        industry_context: str,
        job_title: str,
        framework: str = "how-to"
    ) -> Tuple[GeneratedTopic, GeneratedTopic]:
        """
        Generate both CTO and CEO perspectives for the same topic

        Returns:
            Tuple of (CTO topic, CEO topic)
        """
        cto_topics = self.generate(
            industry_context, job_title, Perspective.CTO, framework, 1
        )
        ceo_topics = self.generate(
            industry_context, job_title, Perspective.CEO, framework, 1
        )

        return (cto_topics[0] if cto_topics else None,
                ceo_topics[0] if ceo_topics else None)


# Global instance
_topic_generator_instance: Optional[TopicGenerator] = None


def get_topic_generator() -> TopicGenerator:
    """Get singleton topic generator instance"""
    global _topic_generator_instance
    if _topic_generator_instance is None:
        _topic_generator_instance = TopicGenerator()
    return _topic_generator_instance
