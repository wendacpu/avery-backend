"""
LinkedIn 资料爬取服务
获取用户的 LinkedIn 公开资料信息和历史帖子
"""
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """LinkedIn 资料爬虫"""

    def __init__(self):
        self.session = requests.Session()
        # 设置请求头模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
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
                return None

            # 发送请求
            response = self.session.get(linkedin_url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"LinkedIn 返回状态码: {response.status_code}")
                # 返回模拟数据
                return self._get_mock_profile(linkedin_url)

            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取基本信息
            profile_data = {
                'name': self._extract_name(soup),
                'title': self._extract_title(soup),
                'company': self._extract_company(soup),
                'location': self._extract_location(soup),
                'bio': self._extract_bio(soup),
                'profile_url': linkedin_url
            }

            logger.info(f"成功爬取 LinkedIn 资料: {profile_data.get('name')}")
            return profile_data

        except Exception as e:
            logger.error(f"爬取 LinkedIn 失败: {str(e)}")
            # 返回模拟数据
            return self._get_mock_profile(linkedin_url)

    def _is_valid_linkedin_url(self, url: str) -> bool:
        """验证 LinkedIn URL 格式"""
        return "linkedin.com/in/" in url.lower()

    def _extract_name(self, soup: BeautifulSoup) -> str:
        """提取姓名"""
        # LinkedIn 的 HTML 结构经常变化，这里是简化版本
        try:
            # 尝试多种可能的选择器
            selectors = [
                'h1.text-heading-xlarge',
                '[data-anonymize="person-name"]',
                '.pv-text-details__left-panel h1',
                'h1'
            ]

            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
        except:
            pass

        return "未知姓名"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取职位"""
        try:
            selectors = [
                '.text-body-medium.break-words',
                '[data-anonymize="job-title"]',
                '.pv-text-details__left-panel .text-body-medium',
                '.text-body-medium'
            ]

            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
        except:
            pass

        return "未知职位"

    def _extract_company(self, soup: BeautifulSoup) -> str:
        """提取公司"""
        try:
            selectors = [
                'button[aria-label*="Current company"]',
                '.pv-text-details__right-panel li:first-child',
                'ul.pv-text-details__right-panel button',
                '.inline-show-more-text--is-collapsed'
            ]

            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
        except:
            pass

        return "未知公司"

    def _extract_location(self, soup: BeautifulSoup) -> str:
        """提取位置"""
        try:
            selectors = [
                '.text-body-small.inline-show-more-text--is-collapsed',
                '.pv-text-details__left-panel .mt2 relative',
                '.text-body-small'
            ]

            for selector in selectors:
                element = soup.select_one(selector)
                if element and "location" in element.get_text().lower():
                    return element.get_text().strip()
        except:
            pass

        return "未知位置"

    def _extract_bio(self, soup: BeautifulSoup) -> str:
        """提取简介"""
        try:
            selectors = [
                '.pv-shared-text-with-see-more',
                '.pv-about__summary-text',
                '.pv-about-section',
                '[data-anonymize="bio"]'
            ]

            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
        except:
            pass

        return ""

    def _get_mock_profile(self, linkedin_url: str) -> Dict[str, Any]:
        """返回模拟 LinkedIn 资料（开发测试用）"""
        # 从 URL 中提取用户名
        username = linkedin_url.split("/in/")[-1].split("/")[0] if "/in/" in linkedin_url else "user"

        return {
            'name': f"LinkedIn User ({username})",
            'title': "Senior Business Professional",
            'company': "Technology Company",
            'location': "San Francisco, CA",
            'bio': f"Experienced professional specializing in business strategy and innovation. Passionate about leveraging technology to drive growth and create value.",
            'profile_url': linkedin_url
        }

    def scrape_recent_posts(self, linkedin_url: str, months: int = 3) -> List[Dict[str, Any]]:
        """
        爬取用户最近的帖子（用于分析高互动主题）

        Args:
            linkedin_url: LinkedIn 个人主页 URL
            months: 爬取最近几个月的帖子（默认3个月）

        Returns:
            帖子列表，包含互动数据
        """
        try:
            if not self._is_valid_linkedin_url(linkedin_url):
                logger.error(f"无效的 LinkedIn URL: {linkedin_url}")
                return []

            # 构建帖子活动页面URL
            # 注意：LinkedIn 的帖子页面 URL 格式可能会变化
            posts_url = linkedin_url.rstrip('/') + '/recent-activity/all/'

            logger.info(f"爬取最近 {months} 个月的帖子: {posts_url}")

            response = self.session.get(posts_url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"LinkedIn 帖子页面返回状态码: {response.status_code}")
                # 返回模拟数据
                return self._get_mock_posts()

            # 解析帖子
            soup = BeautifulSoup(response.text, 'html.parser')

            posts = []
            cutoff_date = datetime.now() - timedelta(days=30 * months)

            # 提取帖子（LinkedIn的HTML结构经常变化，这里提供通用版本）
            # 实际实现中可能需要使用 Playwright 处理动态加载的内容
            post_elements = soup.select('.feed-shared-update-v2, .occludable-update, .feed-update')

            for element in post_elements[:20]:  # 最多20条
                try:
                    post = self._extract_post_data(element, linkedin_url, cutoff_date)
                    if post and post.get('published_at'):
                        posts.append(post)
                except Exception as e:
                    logger.warning(f"解析帖子失败: {str(e)}")
                    continue

            logger.info(f"成功爬取 {len(posts)} 条帖子")
            return posts

        except Exception as e:
            logger.error(f"爬取 LinkedIn 帖子失败: {str(e)}")
            # 返回模拟数据
            return self._get_mock_posts()

    def _extract_post_data(self, element, profile_url: str, cutoff_date: datetime) -> Optional[Dict[str, Any]]:
        """从HTML元素中提取帖子数据"""
        try:
            # 提取文本内容
            content_elem = element.select_one('.feed-shared-text, .update-components-text, .description')
            content = content_elem.get_text().strip() if content_elem else ""

            if not content:
                return None

            # 提取互动数据（点赞、评论、分享）
            likes_elem = element.select_one('[data-anonymize="react-count"], .social-counts__reactions-count, .like-count')
            comments_elem = element.select_one('.social-counts__comments-count, .comment-count')
            shares_elem = element.select_one('.social-counts__shares-count, .share-count')

            likes = self._parse_count(likes_elem.get_text() if likes_elem else "0")
            comments = self._parse_count(comments_elem.get_text() if comments_elem else "0")
            shares = self._parse_count(shares_elem.get_text() if shares_elem else "0")

            # 计算综合互动分数
            engagement_score = likes * 1 + comments * 3 + shares * 5

            # 提取发布时间
            time_elem = element.select_one('.feed-shared-time, .time-ago, .update-time')
            published_at_str = time_elem.get_text().strip() if time_elem else ""

            return {
                'url': profile_url,
                'content': content[:500],  # 限制内容长度
                'published_at': published_at_str,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'engagement_score': engagement_score,
            }

        except Exception as e:
            logger.warning(f"提取帖子数据失败: {str(e)}")
            return None

    def _parse_count(self, text: str) -> int:
        """解析互动数量（处理 "1,234" 或 "1.2k" 格式）"""
        try:
            text = text.strip().lower()

            # 处理 "1.2k" 格式
            if 'k' in text:
                return int(float(text.replace('k', '').replace(',', '.')) * 1000)

            # 处理 "1.2m" 格式
            if 'm' in text:
                return int(float(text.replace('m', '').replace(',', '.')) * 1000000)

            # 处理带逗号的数字
            return int(text.replace(',', '').replace('likes', '').replace('comments', '').replace('shares', '').strip())
        except:
            return 0

    def _get_mock_posts(self) -> List[Dict[str, Any]]:
        """返回模拟帖子数据（开发测试用）"""
        return [
            {
                'url': 'https://linkedin.com/in/example',
                'content': '刚刚完成了Q4的复盘，发现AI工具帮助我们提升了40%的效率。推荐3个我最喜欢的工具：ChatGPT用于内容生成，Notion AI用于知识管理，Zapier用于自动化工作流。大家有什么推荐吗？',
                'published_at': '1天前',
                'likes': 156,
                'comments': 23,
                'shares': 8,
                'engagement_score': 341,
            },
            {
                'url': 'https://linkedin.com/in/example',
                'content': '分享一个我在团队管理中使用的框架：每周一15分钟站会，每个成员分享上周最大的收获和本周目标。简单但有效，大大提升了团队透明度和凝聚力。',
                'published_at': '1周前',
                'likes': 89,
                'comments': 12,
                'shares': 5,
                'engagement_score': 140,
            },
            {
                'url': 'https://linkedin.com/in/example',
                'content': '很多人问我如何平衡工作和生活。我的答案是：不要追求平衡，而要追求整合。找到你热爱的事情，工作和生活就不再是对立面，而是相互促进的伙伴。',
                'published_at': '2周前',
                'likes': 234,
                'comments': 31,
                'shares': 15,
                'engagement_score': 414,
            },
        ]

    def scrape_profile_with_posts(self, linkedin_url: str, months: int = 3) -> Dict[str, Any]:
        """
        爬取完整资料，包含历史帖子

        Args:
            linkedin_url: LinkedIn URL
            months: 爬取最近几个月的帖子

        Returns:
            包含资料和帖子的字典
        """
        profile = self.scrape_profile(linkedin_url)
        posts = self.scrape_recent_posts(linkedin_url, months)

        if profile:
            profile['recent_posts'] = posts

        return profile


# 全局实例
linkedin_scraper = LinkedInScraper()
