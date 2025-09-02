"""
Circuit breaker pattern for OpenAI API calls to prevent cascading failures.
"""

import asyncio
import time
from enum import Enum
from typing import Callable, Optional, Any
from dataclasses import dataclass

from ..core.logging_config import get_logger

logger = get_logger("circuit_breaker")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Circuit is open, calls fail immediately
    HALF_OPEN = "half_open"  # Testing if service is back up


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5          # Number of failures to open circuit
    recovery_timeout: float = 60.0      # Time before attempting recovery
    success_threshold: int = 3          # Successes needed to close circuit in half-open
    timeout: float = 30.0               # Request timeout


class CircuitBreaker:
    """Circuit breaker for OpenAI API calls."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN. "
                        f"Will retry after {self.config.recovery_timeout}s"
                    )

        # Execute the function
        try:
            # Add timeout to the call
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )
            await self._on_success()
            return result

        except Exception as error:
            await self._on_failure(error)
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout

    async def _on_success(self):
        """Handle successful call."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    logger.info("Circuit breaker CLOSED - service recovered")
            else:
                # Reset failure count on success in CLOSED state
                self.failure_count = 0

    async def _on_failure(self, error: Exception):
        """Handle failed call."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.error(
                        f"Circuit breaker OPENED after {self.failure_count} failures. "
                        f"Error: {type(error).__name__}: {str(error)}"
                    )
            elif self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker back to OPEN - service still failing")

    def get_state(self) -> dict:
        """Get current circuit breaker state."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


# Global circuit breaker instance for OpenAI calls
openai_circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
