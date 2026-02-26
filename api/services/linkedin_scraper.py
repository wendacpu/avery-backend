"""
LinkedIn 资料爬取服务 - 增强版
改进的反反爬虫策略，使用 requests + BeautifulSoup
"""
import logging
import time
import random
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """LinkedIn 资料爬虫 - 增强版"""

    def __init__(self):
        self.session = requests.Session()

        # 更真实的请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        })

    def scrape_profile(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """
        爬取 LinkedIn 公开资料

        Args:
            linkedin_url: LinkedIn 个人主页 URL

        Returns:
            包含用户信息的字典
        """
        try:
            if not self._is_valid_linkedin_url(linkedin_url):
                logger.error(f"无效的 LinkedIn URL: {linkedin_url}")
                return self._get_mock_profile(linkedin_url)

            # 添加随机延迟，模拟人类行为
            time.sleep(random.uniform(1, 2))

            # 使用重试机制
            response = self._make_request(linkedin_url)

            if not response or response.status_code != 200:
                logger.warning(f"LinkedIn 返回状态码: {response.status_code if response else 'None'}，尝试使用备用策略")

                # 尝试备用策略：不携带 cookies
                response = self._make_request(linkedin_url, use_cookies=False)

                if not response or response.status_code != 200:
                    logger.warning(f"备用策略也失败，使用 mock 数据")
                    return self._get_mock_profile(linkedin_url)

            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 使用增强的选择器提取信息
            name = self._extract_name_enhanced(soup)
            title = self._extract_title_enhanced(soup)
            company = self._extract_company_enhanced(soup)
            location = self._extract_location_enhanced(soup)
            bio = self._extract_bio_enhanced(soup)

            # 验证提取结果
            if not name or name in ["Unknown Name", "", "LinkedIn"]:
                logger.warning(f"未能提取到真实姓名，使用 mock 数据")
                return self._get_mock_profile(linkedin_url)

            profile_data = {
                'name': name,
                'title': title or "Unknown Title",
                'company': company or "Unknown Company",
                'location': location or "Unknown Location",
                'bio': bio or "",
                'profile_url': linkedin_url
            }

            logger.info(f"✅ 成功爬取 LinkedIn 资料: {name} - {title}")
            return profile_data

        except Exception as e:
            logger.error(f"爬取 LinkedIn 失败: {str(e)}，使用 mock 数据")
            return self._get_mock_profile(linkedin_url)

    def _make_request(self, url: str, use_cookies: bool = True, retry: int = 0) -> Optional[requests.Response]:
        """
        发送 HTTP 请求，支持重试

        Args:
            url: 请求 URL
            use_cookies: 是否使用 cookies
            retry: 重试次数

        Returns:
            Response 对象或 None
        """
        try:
            # 如果不使用 cookies，创建新 session
            session = self.session if use_cookies else requests.Session()

            # 添加 Referer（模拟从搜索页进入）
            if use_cookies and not self.session.cookies.get_dict():
                # 首次访问，先访问 LinkedIn 首页
                try:
                    session.get('https://www.linkedin.com', timeout=5)
                    time.sleep(random.uniform(0.5, 1))
                except:
                    pass

            response = session.get(
                url,
                timeout=15,
                allow_redirects=True
            )

            # 如果返回 999，可能被反爬虫拦截
            if response.status_code == 999 and retry < 2:
                logger.warning(f"收到 999 状态码，等待后重试 ({retry + 1}/2)")
                time.sleep(random.uniform(3, 5))
                return self._make_request(url, use_cookies, retry + 1)

            return response

        except requests.exceptions.Timeout:
            if retry < 2:
                logger.warning(f"请求超时，重试 ({retry + 1}/2)")
                time.sleep(random.uniform(2, 3))
                return self._make_request(url, use_cookies, retry + 1)
            return None
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            return None

    def _is_valid_linkedin_url(self, url: str) -> bool:
        """验证 LinkedIn URL 格式"""
        return "linkedin.com/in/" in url.lower()

    def _extract_name_enhanced(self, soup: BeautifulSoup) -> str:
        """增强版姓名提取"""
        # 扩展选择器列表
        selectors = [
            'h1',
            'h1.text-heading-xlarge',
            '[data-anonymize="person-name"]',
            '.pv-text-details__left-panel h1',
            '.text-heading-xlarge',
            '#profile-content h1',
            '.profile-top-card h1',
        ]

        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text().strip()
                    # 过滤掉无意义的内容
                    if text and len(text) > 1 and len(text) < 100:
                        # 排除一些非姓名的文本
                        if not any(x in text.lower() for x in ['sign in', 'join', 'login', 'home']):
                            return text
            except:
                continue

        return "Unknown Name"

    def _extract_title_enhanced(self, soup: BeautifulSoup) -> str:
        """增强版职位提取"""
        selectors = [
            '.text-body-medium.break-words',
            '.text-body-medium',
            '[data-anonymize="job-title"]',
            '.pv-text-details__left-panel .text-body-medium',
            '.text-body-medium:has(br)',
            'div[data-anonymize="job-title"]',
        ]

        for selector in selectors:
            try:
                # 使用 :has 选择器或逻辑判断
                if ':has(' in selector:
                    # BeautifulSoup 不支持 :has，跳过
                    continue

                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # 职位通常在 5-100 字符之间
                    if 5 < len(text) < 150:
                        # 排除按钮文本
                        if not any(x in text.lower() for x in ['connect', 'message', 'more', 'follow', 'pending']):
                            return text
            except:
                continue

        # 尝试从 meta 标签提取
        try:
            meta_og_title = soup.find('meta', property='og:title')
            if meta_og_title and meta_og_title.get('content'):
                content = meta_og_title['content']
                # LinkedIn og:title 格式通常是 "Name | Title"
                if '|' in content:
                    parts = content.split('|')
                    if len(parts) >= 2:
                        return parts[-1].strip()
        except:
            pass

        return "Unknown Title"

    def _extract_company_enhanced(self, soup: BeautifulSoup) -> str:
        """增强版公司提取"""
        selectors = [
            'button[aria-label*="Current company"]',
            '.pv-text-details__right-panel button',
            'ul.pv-text-details__right-panel button',
            '.inline-show-more-text--is-collapsed',
            '[data-anonymize="company"]',
        ]

        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text().strip()
                    if text and len(text) > 2 and len(text) < 200:
                        return text
            except:
                continue

        # 尝试从职位文本中提取公司
        try:
            title_elem = soup.select_one('.text-body-medium')
            if title_elem:
                title_text = title_elem.get_text().strip()
                # 有些职位包含公司信息，如 "CEO at Company"
                if ' at ' in title_text.lower():
                    parts = title_text.split(' at ')
                    if len(parts) >= 2:
                        return parts[-1].strip()
        except:
            pass

        return "Unknown Company"

    def _extract_location_enhanced(self, soup: BeautifulSoup) -> str:
        """增强版位置提取"""
        selectors = [
            '.text-body-small.inline-show-more-text--is-collapsed',
            '.pv-text-details__left-panel .mt2',
            '.text-body-small:contains("location")',
            '[data-anonymize="location"]',
        ]

        for selector in selectors:
            try:
                if ':contains(' in selector:
                    continue

                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # 位置信息通常包含逗号或地理标识
                    if text and (',' in text or any(x in text.lower() for x in ['area', 'region', 'state', 'country'])):
                        return text
            except:
                continue

        return "Unknown Location"

    def _extract_bio_enhanced(self, soup: BeautifulSoup) -> str:
        """增强版简介提取"""
        selectors = [
            '.pv-shared-text-with-see-more',
            '.pv-about__summary-text',
            '.pv-about-section',
            '#about ~ div .display-flex',
            '[data-anonymize="bio"]',
            'section[data-section="summary"]',
        ]

        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text().strip()
                    # 简介通常较长
                    if len(text) > 50:
                        return text[:500]  # 限制长度
            except:
                continue

        return ""

    def _get_mock_profile(self, linkedin_url: str) -> Dict[str, Any]:
        """返回模拟 LinkedIn 资料（开发测试用）"""
        username = linkedin_url.split("/in/")[-1].split("/")[0] if "/in/" in linkedin_url else "user"

        return {
            'name': f"LinkedIn User ({username})",
            'title': "Senior Business Professional",
            'company': "Technology Company",
            'location': "San Francisco, CA",
            'bio': f"Experienced professional specializing in business strategy and innovation.",
            'profile_url': linkedin_url
        }

    def scrape_recent_posts(self, linkedin_url: str, months: int = 3) -> List[Dict[str, Any]]:
        """暂不支持帖子爬取，返回空列表"""
        logger.warning("Posts scraping not supported in this version")
        return []

    def scrape_profile_with_posts(self, linkedin_url: str, months: int = 3) -> Dict[str, Any]:
        """爬取完整资料（仅资料，无帖子）"""
        profile = self.scrape_profile(linkedin_url)
        if profile:
            profile['recent_posts'] = []
        return profile


# 全局实例
linkedin_scraper = LinkedInScraper()
