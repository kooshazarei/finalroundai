"""
OpenAI error handling service with retry logic and exponential backoff.
"""

import asyncio
import time
from typing import Any, Callable, TypeVar, Optional
from functools import wraps
import openai
from openai import RateLimitError, APITimeoutError, APIConnectionError, InternalServerError

from ..core.logging_config import get_logger

T = TypeVar('T')

logger = get_logger("openai_error_handler")


class OpenAIErrorHandler:
    """Handles OpenAI API errors with retry logic and exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter."""
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        if self.jitter:
            # Add random jitter (±25% of delay)
            import random
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(delay, 0.1)  # Minimum 100ms delay

    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if error should be retried."""
        if attempt >= self.max_retries:
            return False

        # Retry on specific error types
        retryable_errors = (
            RateLimitError,
            APITimeoutError,
            APIConnectionError,
            InternalServerError,
        )

        return isinstance(error, retryable_errors)

    def _log_retry(self, error: Exception, attempt: int, delay: float):
        """Log retry attempt."""
        logger.warning(
            f"OpenAI API error (attempt {attempt + 1}/{self.max_retries}): "
            f"{type(error).__name__}: {str(error)}. "
            f"Retrying in {delay:.2f}s..."
        )

    async def retry_async(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Async retry wrapper for OpenAI API calls."""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as error:
                last_error = error

                if not self._should_retry(error, attempt):
                    # Don't retry non-retryable errors or max retries reached
                    break

                delay = self._calculate_delay(attempt)
                self._log_retry(error, attempt, delay)
                await asyncio.sleep(delay)

        # Log final failure
        logger.error(
            f"OpenAI API call failed after {self.max_retries + 1} attempts: "
            f"{type(last_error).__name__}: {str(last_error)}"
        )
        raise last_error

    def retry_sync(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Sync retry wrapper for OpenAI API calls."""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                last_error = error

                if not self._should_retry(error, attempt):
                    break

                delay = self._calculate_delay(attempt)
                self._log_retry(error, attempt, delay)
                time.sleep(delay)

        logger.error(
            f"OpenAI API call failed after {self.max_retries + 1} attempts: "
            f"{type(last_error).__name__}: {str(last_error)}"
        )
        raise last_error


def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0
):
    """Decorator for automatic retry on OpenAI API calls."""
    def decorator(func):
        error_handler = OpenAIErrorHandler(
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay
        )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await error_handler.retry_async(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return error_handler.retry_sync(func, *args, **kwargs)

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Global error handler instance
default_error_handler = OpenAIErrorHandler()
