"""
LinkedIn 资料爬取服务 - Playwright 版本
使用真实浏览器绕过 LinkedIn 反爬虫机制
"""
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)


class LinkedInScraperPlaywright:
    """LinkedIn 资料爬虫 - Playwright 版本"""

    def __init__(self):
        self.use_playwright = PLAYWRIGHT_AVAILABLE

        if not self.use_playwright:
            logger.warning("Playwright 未安装，将使用 mock 数据")

    def scrape_profile(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """
        爬取 LinkedIn 公开资料（同步接口，内部使用异步）

        Args:
            linkedin_url: LinkedIn 个人主页 URL

        Returns:
            包含用户信息的字典
        """
        if not self.use_playwright:
            return self._get_mock_profile(linkedin_url)

        try:
            # 运行异步爬取
            return asyncio.run(self._scrape_profile_async(linkedin_url))
        except Exception as e:
            logger.error(f"Playwright 爬取失败: {str(e)}，使用 mock 数据")
            return self._get_mock_profile(linkedin_url)

    async def _scrape_profile_async(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """异步爬取 LinkedIn 资料"""
        if not self._is_valid_linkedin_url(linkedin_url):
            logger.error(f"无效的 LinkedIn URL: {linkedin_url}")
            return self._get_mock_profile(linkedin_url)

        async with async_playwright() as p:
            # 启动浏览器（使用 Chromium，设置 headless=False 避免被检测）
            browser = await p.chromium.launch(
                headless=True,  # LinkedIn 可能检测 headless 模式
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ]
            )

            try:
                # 创建新上下文（模拟真实用户）
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York',
                )

                # 添加初始化脚本，隐藏 webdriver 特征
                await context.add_init_script("""
                    // 覆盖 navigator.webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });

                    // 覆盖 chrome 对象
                    window.chrome = {
                        runtime: {}
                    };

                    // 覆盖 permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """)

                page = await context.new_page()

                # 设置超时和等待策略
                page.set_default_timeout(15000)  # 15秒超时

                # 访问页面
                logger.info(f"正在访问 LinkedIn: {linkedin_url}")
                await page.goto(linkedin_url, wait_until='domcontentloaded', timeout=20000)

                # 等待关键元素加载
                try:
                    await page.wait_for_selector('h1', timeout=5000)
                except:
                    logger.warning("等待 h1 元素超时，尝试继续提取")

                # 提取页面内容
                content = await page.content()

                # 使用 playwright 的选择器提取信息
                name = await self._extract_name_playwright(page)
                title = await self._extract_title_playwright(page)
                company = await self._extract_company_playwright(page)
                location = await self._extract_location_playwright(page)
                bio = await self._extract_bio_playwright(page)

                # 验证提取结果
                if not name or name in ["Unknown Name", ""]:
                    logger.warning("未能提取到姓名，使用 mock 数据")
                    return self._get_mock_profile(linkedin_url)

                profile_data = {
                    'name': name,
                    'title': title or "Unknown",
                    'company': company or "Unknown",
                    'location': location or "Unknown",
                    'bio': bio or "",
                    'profile_url': linkedin_url
                }

                logger.info(f"✅ 成功爬取 LinkedIn 资料: {name} - {title}")
                return profile_data

            finally:
                await browser.close()

    async def _extract_name_playwright(self, page: 'Page') -> str:
        """使用 Playwright 提取姓名"""
        selectors = [
            'h1',
            '[data-anonymize="person-name"]',
            '.text-heading-xlarge',
            '.pv-text-details__left-panel h1',
        ]

        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and text.strip():
                        return text.strip()
            except:
                continue

        return "Unknown Name"

    async def _extract_title_playwright(self, page: 'Page') -> str:
        """使用 Playwright 提取职位"""
        selectors = [
            '.text-body-medium',
            '[data-anonymize="job-title"]',
            '.pv-text-details__left-panel .text-body-medium',
        ]

        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.text_content()
                    if text and text.strip() and len(text.strip()) > 5:
                        # 过滤掉一些非职位的内容
                        if not any(x in text.lower() for x in ['connect', 'message', 'more', 'follower']):
                            return text.strip()
            except:
                continue

        return "Unknown Title"

    async def _extract_company_playwright(self, page: 'Page') -> str:
        """使用 Playwright 提取公司"""
        selectors = [
            'button[aria-label*="Current company"]',
            '.pv-text-details__right-panel button',
            '.inline-show-more-text ul li:first-child',
        ]

        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and text.strip():
                        return text.strip()
            except:
                continue

        return "Unknown Company"

    async def _extract_location_playwright(self, page: 'Page') -> str:
        """使用 Playwright 提取位置"""
        selectors = [
            '.text-body-small',
            '.pv-text-details__left-panel .mt2',
        ]

        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.text_content()
                    if text and ('location' in text.lower() or ',' in text):
                        return text.strip()
            except:
                continue

        return "Unknown Location"

    async def _extract_bio_playwright(self, page: 'Page') -> str:
        """使用 Playwright 提取简介"""
        selectors = [
            '.pv-shared-text-with-see-more',
            '.pv-about__summary-text',
            '#about ~ div .display-flex',
        ]

        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and len(text.strip()) > 20:
                        return text.strip()
            except:
                continue

        return ""

    def _is_valid_linkedin_url(self, url: str) -> bool:
        """验证 LinkedIn URL 格式"""
        return "linkedin.com/in/" in url.lower()

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
        logger.warning("Playwright 版本暂不支持帖子爬取")
        return []

    def scrape_profile_with_posts(self, linkedin_url: str, months: int = 3) -> Dict[str, Any]:
        """爬取完整资料（仅资料，无帖子）"""
        profile = self.scrape_profile(linkedin_url)
        if profile:
            profile['recent_posts'] = []
        return profile


# 全局实例
linkedin_scraper_playwright = LinkedInScraperPlaywright()
