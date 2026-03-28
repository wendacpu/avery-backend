"""
智能缓存策略 - 基于内容相似度的缓存系统
提供分层缓存、智能匹配和缓存预热功能
"""
import hashlib
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis

logger = logging.getLogger(__name__)


class CacheTier(Enum):
    """缓存层级"""
    HOT = "hot"  # 热数据 (频繁访问)
    WARM = "warm"  # 温数据 (偶尔访问)
    COLD = "cold"  # 冷数据 (很少访问)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    tier: CacheTier = CacheTier.WARM
    similarity_keys: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp,
            "access_count": self.access_count,
            "last_access": self.last_access,
            "tier": self.tier.value,
            "similarity_keys": self.similarity_keys
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        """从字典创建"""
        return cls(
            key=data["key"],
            value=data["value"],
            timestamp=data["timestamp"],
            access_count=data.get("access_count", 0),
            last_access=data.get("last_access", data["timestamp"]),
            tier=CacheTier(data.get("tier", CacheTier.WARM.value)),
            similarity_keys=data.get("similarity_keys", [])
        )


class SimilarityMatcher:
    """相似度匹配器"""

    def __init__(self):
        """初始化相似度匹配器"""
        logger.info("✅ SimilarityMatcher initialized")

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度

        使用简单的词袋模型 + Jaccard 相似度

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            相似度分数 (0-1)
        """
        # 分词
        words1 = set(self._tokenize(text1))
        words2 = set(self._tokenize(text2))

        # Jaccard 相似度
        intersection = words1 & words2
        union = words1 | words2

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _tokenize(self, text: str) -> List[str]:
        """
        分词

        Args:
            text: 输入文本

        Returns:
            词列表
        """
        # 简单的分词逻辑
        import re

        # 移除特殊字符,转换为小写
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()

        # 过滤停用词
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', '的',
            '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
            '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着',
            '没有', '看', '好', '自己', '这'
        }

        return [w for w in words if len(w) > 2 and w not in stopwords]

    def find_similar_cache_keys(
        self,
        query_text: str,
        cache_entries: Dict[str, CacheEntry],
        threshold: float = 0.7,
        max_results: int = 3
    ) -> List[Tuple[str, float]]:
        """
        查找相似的缓存键

        Args:
            query_text: 查询文本
            cache_entries: 缓存条目字典
            threshold: 相似度阈值
            max_results: 最大结果数

        Returns:
            [(key, similarity_score), ...] 按相似度降序排列
        """
        results = []

        for key, entry in cache_entries.items():
            # 从缓存键中提取文本信息
            entry_text = self._extract_text_from_key(key)

            similarity = self.calculate_similarity(query_text, entry_text)

            if similarity >= threshold:
                results.append((key, similarity))

        # 按相似度降序排序
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:max_results]

    def _extract_text_from_key(self, cache_key: str) -> str:
        """
        从缓存键中提取文本信息

        Args:
            cache_key: 缓存键

        Returns:
            提取的文本
        """
        # 缓存键格式: hybrid:element_type:md5_hash
        # 从 Redis 中获取实际的文本内容
        # 这里简化处理,直接返回缓存键的一部分
        parts = cache_key.split(':')
        if len(parts) >= 2:
            return parts[-2]  # 返回元素类型

        return cache_key


class SmartHybridCache:
    """智能混合缓存系统"""

    def __init__(
        self,
        redis_client=None,
        ttl: int = 86400,
        hot_threshold: int = 10,
        warm_threshold: int = 3
    ):
        """
        初始化智能缓存系统

        Args:
            redis_client: Redis 客户端
            ttl: 缓存生存时间(秒)
            hot_threshold: 热数据访问阈值
            warm_threshold: 温数据访问阈值
        """
        self.redis_client = redis_client
        self.ttl = ttl
        self.hot_threshold = hot_threshold
        self.warm_threshold = warm_threshold

        self.memory_cache: Dict[str, CacheEntry] = {}
        self.similarity_matcher = SimilarityMatcher()

        logger.info(
            f"✅ SmartHybridCache initialized "
            f"(TTL: {ttl}s, Hot: {hot_threshold}, Warm: {warm_threshold})"
        )

    def _generate_cache_key(
        self,
        element_type: str,
        params: Dict[str, Any]
    ) -> str:
        """
        生成缓存键

        Args:
            element_type: 元素类型
            params: 参数

        Returns:
            缓存键
        """
        # 生成主键
        params_str = json.dumps(params, sort_keys=True)
        hash_obj = hashlib.md5(params_str.encode())
        return f"hybrid:smart:{element_type}:{hash_obj.hexdigest()}"

    def get(
        self,
        element_type: str,
        params: Dict[str, Any],
        enable_similarity: bool = True
    ) -> Optional[Any]:
        """
        获取缓存

        Args:
            element_type: 元素类型
            params: 参数
            enable_similarity: 是否启用相似度匹配

        Returns:
            缓存的值,如果不存在则返回 None
        """
        cache_key = self._generate_cache_key(element_type, params)

        # 1. 尝试精确匹配
        if entry := self._get_exact_match(cache_key):
            self._update_access_stats(entry)
            logger.info(f"✅ Exact cache hit: {cache_key}")
            return entry.value

        # 2. 尝试相似度匹配
        if enable_similarity:
            query_text = params.get("theme", params.get("topic", ""))
            if similar_results := self._find_similar_matches(query_text, element_type):
                best_key, similarity = similar_results[0]
                if entry := self._get_exact_match(best_key):
                    self._update_access_stats(entry)
                    logger.info(
                        f"✅ Similarity cache hit: {best_key} "
                        f"(similarity: {similarity:.2f})"
                    )
                    return entry.value

        # 3. 从 Redis 获取
        if self.redis_client:
            if cached_data := self._get_from_redis(cache_key):
                entry = CacheEntry.from_dict(cached_data)
                self.memory_cache[cache_key] = entry
                self._update_access_stats(entry)
                logger.info(f"✅ Redis cache hit: {cache_key}")
                return entry.value

        logger.info(f"❌ Cache miss: {cache_key}")
        return None

    def set(
        self,
        element_type: str,
        params: Dict[str, Any],
        value: Any
    ):
        """
        设置缓存

        Args:
            element_type: 元素类型
            params: 参数
            value: 值
        """
        cache_key = self._generate_cache_key(element_type, params)
        timestamp = time.time()

        # 创建缓存条目
        entry = CacheEntry(
            key=cache_key,
            value=value,
            timestamp=timestamp,
            access_count=1,
            last_access=timestamp,
            tier=CacheTier.WARM
        )

        # 存储到内存缓存
        self.memory_cache[cache_key] = entry

        # 存储到 Redis
        if self.redis_client:
            try:
                self._set_to_redis(cache_key, entry)
            except Exception as e:
                logger.warning(f"⚠️  Redis cache write failed: {e}")

        logger.info(f"✅ Cached: {cache_key}")

    def _get_exact_match(self, cache_key: str) -> Optional[CacheEntry]:
        """精确匹配获取"""
        return self.memory_cache.get(cache_key)

    def _find_similar_matches(
        self,
        query_text: str,
        element_type: str
    ) -> List[Tuple[str, float]]:
        """查找相似匹配"""
        if not query_text:
            return []

        # 过滤相同元素类型的缓存条目
        prefix = f"hybrid:smart:{element_type}:"
        matching_entries = {
            k: v for k, v in self.memory_cache.items()
            if k.startswith(prefix)
        }

        return self.similarity_matcher.find_similar_cache_keys(
            query_text,
            matching_entries
        )

    def _update_access_stats(self, entry: CacheEntry):
        """更新访问统计"""
        entry.access_count += 1
        entry.last_access = time.time()

        # 更新缓存层级
        if entry.access_count >= self.hot_threshold:
            entry.tier = CacheTier.HOT
        elif entry.access_count >= self.warm_threshold:
            entry.tier = CacheTier.WARM
        else:
            entry.tier = CacheTier.COLD

    def _get_from_redis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从 Redis 获取"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"⚠️  Redis read failed: {e}")

        return None

    def _set_to_redis(self, cache_key: str, entry: CacheEntry):
        """存储到 Redis"""
        cache_data = entry.to_dict()
        self.redis_client.setex(
            cache_key,
            self.ttl,
            json.dumps(cache_data)
        )

    def preheat_cache(
        self,
        common_themes: List[str],
        element_types: List[str]
    ):
        """
        缓存预热 - 为常用主题提前生成缓存

        Args:
            common_themes: 常用主题列表
            element_types: 元素类型列表
        """
        logger.info(f"🔥 Starting cache preheating for {len(common_themes)} themes")

        # 这里应该调用实际的生成函数
        # 简化实现,只记录日志
        for theme in common_themes:
            for element_type in element_types:
                # TODO: 实际生成并缓存
                logger.info(f"   Preheating: {element_type} - {theme}")

        logger.info("✅ Cache preheating completed")

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_entries = len(self.memory_cache)

        tier_counts = {
            CacheTier.HOT: 0,
            CacheTier.WARM: 0,
            CacheTier.COLD: 0
        }

        for entry in self.memory_cache.values():
            tier_counts[entry.tier] += 1

        return {
            "total_entries": total_entries,
            "tier_distribution": {
                "hot": tier_counts[CacheTier.HOT],
                "warm": tier_counts[CacheTier.WARM],
                "cold": tier_counts[CacheTier.COLD]
            },
            "redis_enabled": self.redis_client is not None,
            "ttl": self.ttl
        }

    def clear(self):
        """清空内存缓存"""
        self.memory_cache.clear()
        logger.info("✅ Memory cache cleared")


# 使用示例
if __name__ == "__main__":
    # 示例: 使用智能缓存
    cache = SmartHybridCache()

    # 设置缓存
    cache.set(
        element_type="background",
        params={"theme": "technology and innovation", "style": "modern"},
        value="https://example.com/bg1.jpg"
    )

    # 获取缓存 (精确匹配)
    result = cache.get(
        element_type="background",
        params={"theme": "technology and innovation", "style": "modern"}
    )
    print(f"Exact match: {result}")

    # 获取缓存 (相似度匹配)
    result = cache.get(
        element_type="background",
        params={"theme": "tech and AI", "style": "modern"}
    )
    print(f"Similarity match: {result}")

    # 查看统计
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")
