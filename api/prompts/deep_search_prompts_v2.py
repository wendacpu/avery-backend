"""
Deep search prompts for research synthesis and infographic spec - V2: Executive-Level
专为高管级别的内容设计，更深刻、更专业
"""

RESEARCH_SYNTHESIS_PROMPT_V2 = """You are a senior research analyst at a top-tier strategy consulting firm. Synthesize the provided sources into a comprehensive, executive-grade research summary.

**Requirements:**
- Focus on strategic insights, not just surface-level information
- Extract quantitative data with specific numbers, percentages, and metrics
- Identify industry trends, disruptions, and future outlooks
- Provide actionable frameworks and decision models
- Include expert perspectives and thought leadership opinions
- Depth over breadth - 1 profound insight > 10 obvious points

**Return STRICT JSON with this schema:**
{{
  "summary": "2-3 sentences of executive summary",
  "market_context": "60-80 words on market dynamics",
  "strategic_insights": [
    {{
      "insight": "40-60 word strategic insight",
      "implication": "what this means for executives"
    }}
  ],
  "key_numbers": [
    {{
      "metric": "specific metric name",
      "value": "number with unit",
      "context": "why this matters strategically"
    }}
  ],
  "strategic_implications": [
    {{
      "stakeholder": "who is affected",
      "implication": "50-70 word strategic implication"
    }}
  ],
  "chart_candidates": [
    {{
      "metric": "strategic metric",
      "chart_type": "line|bar|pie",
      "strategic_story": "what narrative this chart tells",
      "values": [{{"x": "label", "y": "value"}}]
    }}
  ]
}}

**Topic:** {topic}
**Target Audience:** {target_audience}
**Include Charts:** {include_charts}

**Sources:**
{sources_text}

Remember: This is for C-suite executives. Every insight must be actionable, backed by data, and strategically relevant.
"""


INFOGRAPHIC_SPEC_PROMPT_V2 = """You are a world-class information designer specializing in executive-level visual communications. Convert the research summary into a **high-density, data-rich infographic**.

**Design Principles:**
1. **Information Density**: MAXIMIZE - every pixel should convey value
2. **Modular Architecture**: 3-5 information modules (focused, high-impact)
3. **Executive-Grade Typography**: Hierarchy, readability, professional aesthetics
4. **Data Integration**: Seamlessly weave in charts, metrics, and comparisons

**Module Requirements:**
- **Header**: Title (bold, large), Subtitle (descriptive), Tagline (insightful)
- **Content Modules**: 3-5 modules (optimal: 3-4, maximum: 5), each with:
  - Module ID (A-01, A-02, etc.)
  - Compelling title (6-10 words, actionable)
  - Detailed content (30-50 words, substantive)
  - Supporting data point (specific metric/percentage)
  - Visual hierarchy (bold key terms, organized layout)
- **Chart Integration** (if enabled): Full-width, data-rich, clearly labeled

**Layout Specification:**
- **Canvas**: Vertical 3:4 aspect ratio
- **Grid System**: 2-column or 3-column modular layout
- **Spacing**: Tight but breathable (20% white space)
- **Typography**:
  - Title: 28-32pt, bold
  - Module headers: 16-18pt, bold
  - Body: 12-14pt, regular

**Color Palette (Executive Professional):**
- **Primary**: Deep navy (#1a365d) or forest green (#2d5a3d)
- **Accents**: Muted gold (#d4a017), teal (#0d9488)
- **Background**: Pure white (#ffffff)
- **Module Backgrounds**: Subtle tints

**Content Density Rules:**
- Each module: 30-50 words of substantive content
- No filler - every sentence must add value
- Use bullets for clarity (3-5 bullets per module)
- Include specific numbers, percentages, comparisons
- Bold key terms for scannability

**Return STRICT JSON:**
{{
  "title": "compelling, action-oriented title (8-12 words)",
  "subtitle": "descriptive subtitle (12-15 words)",
  "tagline": "insightful tagline (6-10 words)",
  "modules": [
    {{
      "id": "A-01",
      "title": "action-oriented module title (6-10 words)",
      "content": "30-50 word substantive content with specific insights and data points",
      "bullets": ["3-5 detailed bullet points", "each 8-12 words"],
      "data_point": "specific metric or percentage",
      "color_theme": "light_blue|light_green|cream|light_yellow"
    }}
  ],
  "chart": {{
    "enabled": true,
    "type": "line|bar|pie",
    "title": "strategic chart title (8-12 words)",
    "narrative": "what this chart shows (15-20 words)",
    "x_label": "x axis label",
    "y_label": "y axis label",
    "values": [
      {{
        "x": "label",
        "y": "value",
        "annotation": "strategic note (optional)",
        "highlight": true/false
      }}
    ],
    "key_insight": "single-sentence takeaway"
  }},
  "footer": {{
    "cta": "professional call-to-action (8-12 words)",
    "attribution": "data sources or methodology"
  }}
}}

**Topic:** {topic}
**Quality:** {content_quality} (normal=3-4 modules, advanced=4-5, professional=5 maximum)
**Include Charts:** {include_charts}
**Style:** {style_id}

**Research Summary:**
{research_summary}

**Critical Requirements:**
1. MAXIMIZE information density
2. Every module must have actionable, specific content
3. Use real data from research summary
4. Charts must be data-rich with clear narratives
5. Typography and layout must be executive-appropriate
6. All text labels in charts must be horizontal (no vertical text)
"""


# Deep Search查询升级 - 更专业的搜索策略
DEEP_SEARCH_QUERIES_V2 = {
    "ceo_founder": [
        "{topic} strategic implications C-suite executives 2024-2025",
        "{topic} market size CAGR growth projections enterprise",
        "{topic} disruption case studies Fortune 500 companies",
        "{topic} investment trends venture capital M&A activity",
        "{topic} competitive landscape benchmark analysis leaders"
    ],
    "marketing_leader": [
        "{topic} marketing strategy ROI attribution metrics",
        "{topic} customer acquisition cost trends benchmarks B2B",
        "{topic} digital transformation marketing automation 2024",
        "{topic} brand positioning case studies successful campaigns",
        "{topic} marketing technology stack marquez evolution"
    ],
    "product_manager": [
        "{topic} product development frameworks agile methodology",
        "{topic} user research customer insights data-driven",
        "{topic} product-market fit metrics KPIs dashboards",
        "{topic} feature prioritization frameworks RICE score",
        "{topic} product launch go-to-market strategy case studies"
    ],
    "sales_director": [
        "{topic} sales methodology training enablement 2024",
        "{topic} sales performance metrics quotas compensation",
        "{topic} B2B sales cycles enterprise deal velocity",
        "{topic} sales tech stack CRM optimization automation",
        "{topic} prospecting strategies outbound inbound 2024 trends"
    ],
    "tech_lead": [
        "{topic} technology architecture patterns microservices 2024",
        "{topic} engineering productivity metrics DORA benchmark",
        "{topic} devops CI/CD pipeline best practices scalability",
        "{topic} tech stack selection criteria tradeoffs analysis",
        "{topic} engineering culture remote distributed teams"
    ],
    "consultant": [
        "{topic} consulting frameworks methodology best practices",
        "{topic} client delivery metrics satisfaction KPIs",
        "{topic} thought leadership content white papers research",
        "{topic} project management scoping change management",
        "{topic} industry analysis competitive intelligence frameworks"
    ],
    "default": [
        "{topic} strategic overview market analysis 2024-2025",
        "{topic} best practices industry standards benchmarks",
        "{topic} trends innovations recent developments expert",
        "{topic} case studies real-world examples implementation",
        "{topic} ROI metrics performance measurement success factors"
    ]
}


def get_deep_search_queries(job_title: str, topic: str, company_info: dict = None) -> list:
    """
    根据职位和主题生成专业的深度搜索查询

    Args:
        job_title: 职位类型 (如 "ceo_founder", "marketing_leader")
        topic: 主题
        company_info: 公司信息（可选）

    Returns:
        搜索查询列表
    """
    import re

    # 职位映射
    job_map = {
        "ceo_founder": "ceo_founder",
        "marketing_leader": "marketing_leader",
        "product_manager": "product_manager",
        "sales_director": "sales_director",
        "tech_lead": "tech_lead",
        "consultant": "consultant"
    }

    job_key = job_map.get(job_title, "default")
    base_queries = DEEP_SEARCH_QUERIES_V2.get(job_key, DEEP_SEARCH_QUERIES_V2["default"])

    # 格式化查询
    queries = [q.format(topic=topic) for q in base_queries]

    # 如果有公司信息，添加公司相关查询
    if company_info and company_info.get("name"):
        company_name = company_info["name"]
        company_queries = [
            f"{{company_name}} {topic} strategy competitive positioning",
            f"{{company_name}} annual report earnings {topic} insights",
            f"{{company_name}} press releases {topic} initiatives"
        ]
        queries.extend(company_queries)

    return queries
