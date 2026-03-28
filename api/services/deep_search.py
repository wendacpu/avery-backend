"""
Deep search service using Tavily.
"""
import logging
from typing import Any, Dict, List, Optional
import httpx

from api.core.config import settings

logger = logging.getLogger(__name__)


class DeepSearchService:
    def __init__(self):
        self.api_key = settings.tavily_api_key
        self.api_url = "https://api.tavily.com/search"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _build_queries(
        self,
        topic: str,
        company_info: Optional[Dict[str, Any]],
        linkedin_profile: Optional[Dict[str, Any]],
        job_title: Optional[str],
        additional_context: Optional[str],
    ) -> List[str]:
        queries = [
            f"{topic} market size CAGR statistics",
            f"{topic} benchmarks key metrics",
            f"{topic} case study enterprise adoption",
        ]

        if company_info and company_info.get("name"):
            company_name = company_info["name"]
            queries.append(f"{company_name} {topic} strategy insights")
            queries.append(f"{company_name} industry report")

        if linkedin_profile and linkedin_profile.get("title"):
            title = linkedin_profile.get("title")
            queries.append(f"{title} perspective on {topic}")

        if job_title:
            queries.append(f"{job_title} playbook {topic} insights")

        if additional_context:
            queries.append(f"{topic} {additional_context}")

        # De-dup while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            q_norm = q.strip().lower()
            if q_norm and q_norm not in seen:
                seen.add(q_norm)
                unique_queries.append(q)

        return unique_queries

    def search(
        self,
        topic: str,
        company_info: Optional[Dict[str, Any]] = None,
        linkedin_profile: Optional[Dict[str, Any]] = None,
        job_title: Optional[str] = None,
        additional_context: Optional[str] = None,
        max_results_per_query: int = 5,
        queries: Optional[List[str]] = None,  # 新增：直接传递查询列表
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("Tavily API key not configured; deep search skipped")
            return []

        # 如果直接提供了queries，使用它；否则构建queries
        if queries is None:
            queries = self._build_queries(
                topic=topic,
                company_info=company_info,
                linkedin_profile=linkedin_profile,
                job_title=job_title,
                additional_context=additional_context,
            )
        else:
            logger.info(f"使用提供的 {len(queries)} 个定制查询")

        results: List[Dict[str, Any]] = []
        seen_urls = set()

        for query in queries:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": max_results_per_query,
                "include_raw_content": True,
                "include_answer": False,
            }

            try:
                with httpx.Client(timeout=20.0) as client:
                    resp = client.post(self.api_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                items = data.get("results", []) or []

                for item in items:
                    url = item.get("url")
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    results.append({
                        "query": query,
                        "title": item.get("title", ""),
                        "url": url,
                        "content": item.get("content") or item.get("raw_content") or "",
                        "score": item.get("score", 0),
                    })
            except Exception as e:
                logger.warning(f"Tavily search failed for query '{query}': {e}")
                continue

        # Sort by score descending
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results


deep_search_service = DeepSearchService()
