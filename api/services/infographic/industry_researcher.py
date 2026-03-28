"""
Industry Researcher Module
Gathers real industry data and statistics using Tavily API for infographic content.
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import httpx

from api.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class IndustryStat:
    """Single industry statistic"""
    value: str
    context: str
    source: str
    year: Optional[str] = None


@dataclass
class ChartData:
    """Data for chart visualization"""
    chart_type: str  # line, bar, pie
    title: str
    data_points: List[Dict[str, Any]]
    x_label: str
    y_label: str


class IndustryResearcher:
    """
    Industry Research Service using Tavily API

    Features:
    - Real-time industry statistics gathering
    - Trend identification and verification
    - Chart-ready data formatting
    - Multi-source validation
    """

    def __init__(self):
        """Initialize industry researcher"""
        self.api_key = settings.tavily_api_key
        self.api_base = "https://api.tavily.com/search"
        self.timeout = 30.0

        if not self.api_key or self.api_key == "your-tavily-api-key-here":
            logger.warning("Tavily API key not configured")

    def research(
        self,
        topic: str,
        perspective: str = "ceo",
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Research industry data for given topic

        Args:
            topic: Industry/topic to research
            perspective: CTO or CEO perspective (affects search focus)
            focus_areas: Specific areas to focus on (market, trends, stats)

        Returns:
            Dict with:
                - statistics: List[IndustryStat]
                - charts: List[ChartData]
                - insights: List[str]
                - sources: List[str]
        """
        if not self.api_key or self.api_key == "your-tavily-api-key-here":
            logger.warning("Tavily API not configured, returning mock data")
            return self._get_mock_data(topic, perspective)

        try:
            # Determine search queries based on perspective
            search_queries = self._generate_search_queries(topic, perspective, focus_areas)

            all_results = {
                "statistics": [],
                "charts": [],
                "insights": [],
                "sources": []
            }

            # Execute searches and aggregate results
            for query in search_queries:
                results = self._search_tavily(query)
                all_results = self._merge_results(all_results, results)

            # Format data for charts
            all_results["charts"] = self._generate_chart_data(all_results["statistics"], topic)

            logger.info(f"Research completed for {topic}: {len(all_results['statistics'])} stats, {len(all_results['charts'])} charts")
            return all_results

        except Exception as e:
            logger.error(f"Research failed: {e}")
            return self._get_mock_data(topic, perspective)

    def _generate_search_queries(
        self,
        topic: str,
        perspective: str,
        focus_areas: Optional[List[str]]
    ) -> List[str]:
        """Generate targeted search queries"""
        queries = []

        # Base query
        queries.append(f"{topic} industry statistics 2024 2025 trends")

        # Perspective-specific queries
        if perspective == "cto":
            queries.extend([
                f"{topic} technology adoption rates",
                f"{topic} implementation statistics",
                f"{topic} technical challenges data"
            ])
        else:  # CEO
            queries.extend([
                f"{topic} market size growth",
                f"{topic} ROI business case statistics",
                f"{topic} industry adoption enterprise"
            ])

        # Focus area specific queries
        if focus_areas:
            for area in focus_areas:
                queries.append(f"{topic} {area} statistics data")

        return queries[:5]  # Limit to 5 queries to avoid rate limits

    def _search_tavily(self, query: str) -> Dict[str, Any]:
        """Execute Tavily API search"""
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": 10,
            "include_answer": True,
            "include_raw_content": False
        }

        response = httpx.post(
            self.api_base,
            json=payload,
            headers=headers,
            timeout=self.timeout
        )

        response.raise_for_status()
        results = response.json()

        return self._parse_tavily_results(results)

    def _parse_tavily_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Tavily search results into structured data"""
        parsed = {
            "statistics": [],
            "insights": [],
            "sources": []
        }

        # Extract answer if available
        if "answer" in results:
            parsed["insights"].append(results["answer"])

        # Extract statistics from results
        for result in results.get("results", []):
            parsed["sources"].append(result.get("url", ""))
            parsed["insights"].append(result.get("content", "")[:500])

            # Try to extract statistics from content
            stats = self._extract_statistics(result.get("content", ""))
            parsed["statistics"].extend(stats)

        return parsed

    def _extract_statistics(self, text: str) -> List[IndustryStat]:
        """Extract statistical data from text"""
        import re

        stats = []

        # Pattern: percentage followed by context
        percentage_pattern = r'(\d+(?:\.\d+)?)%\s*([^,.]*)'
        for match in re.finditer(percentage_pattern, text):
            value = f"{match.group(1)}%"
            context = match.group(2).strip()
            if len(context) > 5:  # Filter out false positives
                stats.append(IndustryStat(
                    value=value,
                    context=context,
                    source="extracted"
                ))

        # Pattern: currency/market size
        money_pattern = r'\$(\d+(?:\.\d+)?)\s*(billion|million|B|M)'
        for match in re.finditer(money_pattern, text, re.IGNORECASE):
            value = f"${match.group(1)}{match.group(2)}"
            # Find context around the match
            stats.append(IndustryStat(
                value=value,
                context="market size",
                source="extracted"
            ))

        return stats[:10]  # Limit to 10 stats per source

    def _merge_results(
        self,
        base: Dict[str, Any],
        new: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge new results into base results"""
        for key in ["statistics", "insights", "sources"]:
            if key in new:
                base[key].extend(new[key])
        return base

    def _generate_chart_data(
        self,
        statistics: List[IndustryStat],
        topic: str
    ) -> List[ChartData]:
        """Generate chart-ready data from statistics"""
        charts = []

        # Group statistics by value type
        percentages = [s for s in statistics if '%' in s.value]
        money = [s for s in statistics if '$' in s.value]

        # Line chart: trend data
        if len(percentages) >= 3:
            charts.append(ChartData(
                chart_type="line",
                title=f"{topic} Adoption Trends",
                data_points=[
                    {"x": f"Point {i+1}", "y": stat.value, "label": stat.context}
                    for i, stat in enumerate(percentages[:5])
                ],
                x_label="Timeline",
                y_label="Percentage"
            ))

        # Bar chart: comparison
        if len(money) >= 3:
            charts.append(ChartData(
                chart_type="bar",
                title=f"{topic} Market Comparison",
                data_points=[
                    {"x": stat.context, "y": stat.value, "label": stat.value}
                    for stat in money[:5]
                ],
                x_label="Category",
                y_label="Value"
            ))

        # Pie chart: distribution
        if len(percentages) >= 3:
            charts.append(ChartData(
                chart_type="pie",
                title=f"{topic} Distribution",
                data_points=[
                    {"category": stat.context, "value": stat.value}
                    for stat in percentages[:5]
                ],
                x_label="",
                y_label="Percentage"
            ))

        return charts

    def _get_mock_data(self, topic: str, perspective: str) -> Dict[str, Any]:
        """Generate empty structure when API is unavailable (Maintain Data Integrity)"""
        logger.warning("Returning empty data for research (Maintain Data Integrity)")

        return {
            "statistics": [],
            "charts": [],
            "insights": [
                f"No real-time industry data found for {topic}. Using structural logic only."
            ],
            "sources": []
        }


# Singleton instance
_industry_researcher_instance = None


def get_industry_researcher() -> IndustryResearcher:
    """Get singleton industry researcher instance"""
    global _industry_researcher_instance
    if _industry_researcher_instance is None:
        _industry_researcher_instance = IndustryResearcher()
    return _industry_researcher_instance
