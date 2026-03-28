"""
Deep search prompts for research synthesis and infographic spec.
"""

RESEARCH_SYNTHESIS_PROMPT = """You are a senior research analyst. Synthesize the provided sources into a concise, high-signal research summary for executives.

Requirements:
- Prioritize concrete, defensible facts and numbers.
- Avoid fluff. Prefer crisp sentences and short phrases.
- Use the provided sources only; do not invent citations.
- If data conflicts, note uncertainty briefly.

Return STRICT JSON with this schema:
{{
  "summary": "2-4 sentences",
  "key_insights": ["short phrase", "short phrase"],
  "key_numbers": [
    {{"label": "metric name", "value": "number + unit", "context": "short phrase"}}
  ],
  "chart_candidates": [
    {{
      "metric": "what the chart shows",
      "chart_type": "line|bar|pie|area",
      "x_label": "x axis label",
      "y_label": "y axis label",
      "values": [{{"x": "label", "y": "value"}}],
      "rationale": "why this chart is useful"
    }}
  ],
  "citations": [{{"title": "source title", "url": "source url"}}]
}}

Topic: {topic}
Target audience: {target_audience}
Include charts: {include_charts}

Sources:
{sources_text}
"""


INFOGRAPHIC_SPEC_PROMPT = """You are a world-class information designer. Convert the research summary into a high-density infographic specification.

Constraints:
- 3-4 modules for normal, 4-5 for advanced, 5 maximum for professional.
- Each module must be a short, high-impact phrase (max 12 words).
- If include_charts=false, do not include any chart block.
- Choose chart type based on data characteristics; keep it simple.

Return STRICT JSON with this schema:
{{
  "title": "short title",
  "subtitle": "short subtitle",
  "modules": [
    {{"id": "A-01", "title": "4-8 words", "phrase": "short phrase", "data_hint": "optional data hook"}}
  ],
  "chart": {{
    "enabled": true,
    "type": "line|bar|pie|area",
    "title": "chart title",
    "x_label": "x axis label",
    "y_label": "y axis label",
    "values": [{{"x": "label", "y": "value"}}]
  }},
  "footer": "short footer phrase"
}}

Topic: {topic}
Quality: {content_quality}
Include charts: {include_charts}
Style: {style_id}

Research summary:
{research_summary}
"""
