"""
错误处理和降级策略 - 优化版
提供多级降级策略和智能重试机制
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)


class FallbackStrategy(Enum):
    """降级策略"""
    FULL_AI = "full_ai"  # 完整 AI 生成
    PARTIAL_AI = "partial_ai"  # 部分 AI (缓存 + 降级 prompt)
    SVG_PATTERN = "svg_pattern"  # SVG 图案背景
    SVG_GRADIENT = "svg_gradient"  # SVG 渐变背景
    SOLID_COLOR = "solid_color"  # 纯色背景


class RetryStrategy(Enum):
    """重试策略"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"  # 指数退避
    LINEAR_BACKOFF = "linear_backoff"  # 线性退避
    IMMEDIATE = "immediate"  # 立即重试
    NONE = "none"  # 不重试


@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    base_delay: float = 1.0  # 基础延迟(秒)
    max_delay: float = 60.0  # 最大延迟(秒)
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    backoff_multiplier: float = 2.0  # 退避乘数


@dataclass
class FallbackResult:
    """降级结果"""
    success: bool
    strategy_used: FallbackStrategy
    data: Any
    attempts: int
    error: Optional[str] = None


class SmartRetryHandler:
    """智能重试处理器"""

    def __init__(self, config: RetryConfig = None):
        """
        初始化重试处理器

        Args:
            config: 重试配置
        """
        self.config = config or RetryConfig()
        logger.info(f"✅ SmartRetryHandler initialized (strategy: {self.config.strategy.value})")

    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        执行函数并在失败时重试

        Args:
            func: 要执行的异步函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数执行结果

        Raises:
            Exception: 所有重试失败后抛出最后一次异常
        """
        last_exception = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                logger.info(f"🔄 Attempt {attempt}/{self.config.max_attempts}")

                # 执行函数
                result = await func(*args, **kwargs)

                if attempt > 1:
                    logger.info(f"✅ Success on attempt {attempt}")

                return result

            except Exception as e:
                last_exception = e
                error_msg = str(e)

                # 判断是否应该重试
                if attempt < self.config.max_attempts and self._should_retry(error_msg):
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"⚠️  Attempt {attempt} failed: {error_msg[:100]}... "
                        f"Retrying in {delay:.1f}s"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"❌ All attempts failed: {error_msg}")
                    break

        # 所有重试都失败
        raise last_exception

    def _should_retry(self, error_msg: str) -> bool:
        """
        判断是否应该重试

        Args:
            error_msg: 错误消息

        Returns:
            是否应该重试
        """
        # 不应重试的错误类型
        no_retry_errors = [
            "authentication failed",
            "invalid api key",
            "unauthorized",
            "forbidden",
            "not found"
        ]

        error_msg_lower = error_msg.lower()

        for no_retry in no_retry_errors:
            if no_retry in error_msg_lower:
                logger.warning(f"⚠️  Non-retryable error detected: {no_retry}")
                return False

        return True

    def _calculate_delay(self, attempt: int) -> float:
        """
        计算重试延迟

        Args:
            attempt: 当前尝试次数

        Returns:
            延迟时间(秒)
        """
        if self.config.strategy == RetryStrategy.IMMEDIATE:
            return 0.0

        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * attempt
            return min(delay, self.config.max_delay)

        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** (attempt - 1))
            return min(delay, self.config.max_delay)

        else:  # NONE
            return 0.0


class EnhancedFallbackManager:
    """增强的降级管理器"""

    def __init__(self):
        """初始化降级管理器"""
        self.retry_handler = SmartRetryHandler()
        self.svg_patterns = self._init_svg_patterns()
        logger.info("✅ EnhancedFallbackManager initialized")

    def _init_svg_patterns(self) -> Dict[str, str]:
        """初始化 SVG 图案"""
        return {
            "dots": self._create_dots_pattern(),
            "lines": self._create_lines_pattern(),
            "grid": self._create_grid_pattern(),
            "circles": self._create_circles_pattern(),
            "waves": self._create_waves_pattern()
        }

    def _create_dots_pattern(self) -> str:
        """创建点阵图案"""
        return '''
        <pattern id="dots" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
            <circle cx="10" cy="10" r="1.5" fill="currentColor" opacity="0.15"/>
        </pattern>'''

    def _create_lines_pattern(self) -> str:
        """创建线条图案"""
        return '''
        <pattern id="lines" x="0" y="0" width="10" height="10" patternUnits="userSpaceOnUse">
            <path d="M0,10 L10,10" stroke="currentColor" stroke-width="0.5" opacity="0.1"/>
        </pattern>'''

    def _create_grid_pattern(self) -> str:
        """创建网格图案"""
        return '''
        <pattern id="grid" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.1"/>
        </pattern>'''

    def _create_circles_pattern(self) -> str:
        """创建圆形图案"""
        return '''
        <pattern id="circles" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">
            <circle cx="15" cy="15" r="10" fill="none" stroke="currentColor" stroke-width="1" opacity="0.1"/>
        </pattern>'''

    def _create_waves_pattern(self) -> str:
        """创建波浪图案"""
        return '''
        <pattern id="waves" x="0" y="0" width="40" height="20" patternUnits="userSpaceOnUse">
            <path d="M0,10 Q10,5 20,10 T40,10" fill="none" stroke="currentColor" stroke-width="1" opacity="0.15"/>
        </pattern>'''

    async def generate_with_fallback(
        self,
        ai_generator_func: Callable,
        style_config: Dict[str, Any],
        fallback_order: list[FallbackStrategy] = None
    ) -> FallbackResult:
        """
        使用降级策略生成内容

        Args:
            ai_generator_func: AI 生成函数
            style_config: 风格配置
            fallback_order: 降级顺序(默认: FULL_AI → SVG_PATTERN → SOLID_COLOR)

        Returns:
            降级结果
        """
        if fallback_order is None:
            fallback_order = [
                FallbackStrategy.FULL_AI,
                FallbackStrategy.SVG_PATTERN,
                FallbackStrategy.SOLID_COLOR
            ]

        for strategy in fallback_order:
            try:
                logger.info(f"🎯 Trying strategy: {strategy.value}")

                if strategy == FallbackStrategy.FULL_AI:
                    # 尝试完整 AI 生成
                    result = await self.retry_handler.execute_with_retry(
                        ai_generator_func
                    )
                    return FallbackResult(
                        success=True,
                        strategy_used=strategy,
                        data=result,
                        attempts=1
                    )

                elif strategy == FallbackStrategy.SVG_PATTERN:
                    # 使用 SVG 图案背景
                    result = self._generate_svg_pattern_fallback(style_config)
                    return FallbackResult(
                        success=True,
                        strategy_used=strategy,
                        data=result,
                        attempts=1
                    )

                elif strategy == FallbackStrategy.SVG_GRADIENT:
                    # 使用 SVG 渐变背景
                    result = self._generate_svg_gradient_fallback(style_config)
                    return FallbackResult(
                        success=True,
                        strategy_used=strategy,
                        data=result,
                        attempts=1
                    )

                elif strategy == FallbackStrategy.SOLID_COLOR:
                    # 使用纯色背景
                    result = self._generate_solid_color_fallback(style_config)
                    return FallbackResult(
                        success=True,
                        strategy_used=strategy,
                        data=result,
                        attempts=1
                    )

            except Exception as e:
                logger.warning(f"⚠️  Strategy {strategy.value} failed: {str(e)}")
                continue

        # 所有策略都失败
        return FallbackResult(
            success=False,
            strategy_used=FallbackStrategy.SOLID_COLOR,
            data=None,
            attempts=len(fallback_order),
            error="All fallback strategies failed"
        )

    def _generate_svg_pattern_fallback(self, style_config: Dict[str, Any]) -> str:
        """生成 SVG 图案背景"""
        import random

        background_color = style_config.get("background_color", "#F7F4EF")
        pattern_name = random.choice(list(self.svg_patterns.keys()))
        pattern_svg = self.svg_patterns[pattern_name]

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600">
            <defs>{pattern_svg}</defs>
            <rect width="100%" height="100%" fill="{background_color}"/>
            <rect width="100%" height="100%" fill="url(#{pattern_name})"/>
        </svg>'''

        logger.info(f"✅ Generated SVG pattern fallback: {pattern_name}")
        return f"data:image/svg+xml;base64,{svg.encode().hex()}"

    def _generate_svg_gradient_fallback(self, style_config: Dict[str, Any]) -> str:
        """生成 SVG 渐变背景"""
        import random

        background_color = style_config.get("background_color", "#F7F4EF")
        primary_color = style_config.get("primary_color", "#2D5A3D")

        # 随机选择渐变方向
        gradient_directions = [
            "x1='0%' y1='0%' x2='100%' y2='100%'",
            "x1='0%' y1='0%' x2='0%' y2='100%'",
            "x1='0%' y1='0%' x2='100%' y2='0%'"
        ]
        direction = random.choice(gradient_directions)

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600">
            <defs>
                <linearGradient id="grad" {direction}>
                    <stop offset="0%" style="stop-color:{background_color};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:{primary_color};stop-opacity:0.3" />
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#grad)"/>
        </svg>'''

        logger.info("✅ Generated SVG gradient fallback")
        return f"data:image/svg+xml;base64,{svg.encode().hex()}"

    def _generate_solid_color_fallback(self, style_config: Dict[str, Any]) -> str:
        """生成纯色背景"""
        background_color = style_config.get("background_color", "#F7F4EF")

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600">
            <rect width="100%" height="100%" fill="{background_color}"/>
        </svg>'''

        logger.info("✅ Generated solid color fallback")
        return f"data:image/svg+xml;base64,{svg.encode().hex()}"

    def get_available_strategies(self) -> list[FallbackStrategy]:
        """获取可用的降级策略"""
        return [
            FallbackStrategy.FULL_AI,
            FallbackStrategy.SVG_PATTERN,
            FallbackStrategy.SVG_GRADIENT,
            FallbackStrategy.SOLID_COLOR
        ]


# 使用示例
if __name__ == "__main__":
    async def example_fallback():
        """降级策略示例"""

        fallback_manager = EnhancedFallbackManager()

        # 模拟 AI 生成函数
        async def mock_ai_generation():
            # 模拟失败
            raise Exception("AI service unavailable")

        # 使用降级策略
        result = await fallback_manager.generate_with_fallback(
            ai_generator_func=mock_ai_generation,
            style_config={
                "background_color": "#F7F4EF",
                "primary_color": "#2D5A3D"
            }
        )

        print(f"✅ Success: {result.success}")
        print(f"🎯 Strategy used: {result.strategy_used.value}")
        print(f"📊 Attempts: {result.attempts}")

    # 运行示例
    asyncio.run(example_fallback())
