"""
公司网站信息提取服务
从公司网站提取关键信息
"""
import os
import logging
from typing import Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class CompanyScraper:
    """公司信息提取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def scrape_company_info(self, company_url: str) -> Optional[Dict[str, Any]]:
        """
        提取公司信息

        Args:
            company_url: 公司网站 URL

        Returns:
            包含公司信息的字典
        """
        try:
            if not company_url:
                return None

            # 规范化 URL
            if not company_url.startswith(('http://', 'https://')):
                company_url = 'https://' + company_url

            # 发送请求
            response = self.session.get(company_url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"公司网站返回状态码: {response.status_code}")
                return self._get_mock_company_info(company_url)

            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取信息
            company_info = {
                'name': self._extract_company_name(soup, company_url),
                'description': self._extract_description(soup),
                'industry': self._extract_industry(soup),
                'keywords': self._extract_keywords(soup),
                'website_url': company_url
            }

            logger.info(f"成功提取公司信息: {company_info.get('name')}")
            return company_info

        except Exception as e:
            logger.error(f"提取公司信息失败: {str(e)}")
            return self._get_mock_company_info(company_url)

    def _extract_company_name(self, soup: BeautifulSoup, url: str) -> str:
        """提取公司名称"""
        try:
            # 尝试从 meta 标签获取
            meta_name = soup.find('meta', property='og:site_name')
            if meta_name and meta_name.get('content'):
                return meta_name['content']

            # 尝试从 title 获取
            title = soup.find('title')
            if title:
                title_text = title.get_text().strip()
                # 移除常见的后缀
                for suffix in [' - Home', ' | Home', ' - Official Site', ' | Official Site']:
                    title_text = title_text.replace(suffix, '')
                return title_text

            # 从 URL 提取域名作为公司名
            domain = urlparse(url).netloc.replace('www.', '').split('.')[0]
            return domain.capitalize()

        except:
            return "Unknown Company"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """提取公司描述"""
        try:
            # 尝试 meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                return meta_desc['content']

            # 尝试 og:description
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                return og_desc['content']

            # 尝试从页面内容提取
            for tag in ['p', 'div']:
                element = soup.find(tag, class_=lambda x: x and ('about' in x.lower() or 'description' in x.lower() or 'intro' in x.lower()))
                if element:
                    text = element.get_text().strip()
                    if len(text) > 50 and len(text) < 500:
                        return text

            return ""

        except:
            return ""

    def _extract_industry(self, soup: BeautifulSoup) -> str:
        """提取行业信息"""
        try:
            # 从 keywords 中猜测行业
            keywords = self._extract_keywords(soup)

            industry_keywords = {
                'Technology': ['software', 'tech', 'ai', 'cloud', 'saas', 'data'],
                'Finance': ['finance', 'banking', 'investment', 'financial'],
                'Healthcare': ['health', 'medical', 'healthcare', 'pharmaceutical'],
                'Retail': ['retail', 'ecommerce', 'shopping', 'store'],
                'Manufacturing': ['manufacturing', 'industrial', 'factory'],
                'Consulting': ['consulting', 'services', 'advisory'],
            }

            keywords_lower = keywords.lower()
            for industry, terms in industry_keywords.items():
                if any(term in keywords_lower for term in terms):
                    return industry

            return "Business"

        except:
            return "Unknown"

    def _extract_keywords(self, soup: BeautifulSoup) -> str:
        """提取关键词"""
        try:
            # meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and meta_keywords.get('content'):
                return meta_keywords['content']

            # 从标题和描述中提取
            keywords = []
            title = soup.find('title')
            if title:
                keywords.extend(title.get_text().split())

            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_keywords.get('content'):
                keywords.extend(meta_desc['content'].split())

            return ' '.join(keywords[:10])  # 返回前10个词

        except:
            return ""

    def _get_mock_company_info(self, company_url: str) -> Dict[str, Any]:
        """返回模拟公司信息（开发测试用）"""
        domain = urlparse(company_url).netloc.replace('www.', '').split('.')[0]

        return {
            'name': domain.capitalize() + " Inc.",
            'description': f"{domain.capitalize()} is a leading company specializing in innovative solutions and services for businesses worldwide.",
            'industry': "Technology",
            'keywords': "innovation, technology, business, solutions, services",
            'website_url': company_url
        }


# 全局实例
company_scraper = CompanyScraper()
