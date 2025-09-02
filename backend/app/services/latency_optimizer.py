"""
Latency optimization service for OpenAI API calls.
"""

import asyncio
import time
from typing import AsyncGenerator, Optional, Dict, Any
from dataclasses import dataclass

from ..core.logging_config import get_logger

logger = get_logger("latency_optimizer")


@dataclass
class LatencyConfig:
    """Configuration for latency optimization."""
    request_timeout: float = 30.0           # Individual request timeout
    stream_timeout: float = 5.0             # Timeout for stream chunks
    max_response_time: float = 45.0         # Max total response time
    chunk_buffer_size: int = 10             # Buffer size for streaming
    enable_compression: bool = True         # Enable response compression
    connection_pool_size: int = 100         # HTTP connection pool size


class LatencyOptimizer:
    """Optimizes latency for OpenAI API calls."""

    def __init__(self, config: LatencyConfig):
        self.config = config
        self.request_metrics: Dict[str, Any] = {}

    async def stream_with_timeout(
        self,
        stream_generator: AsyncGenerator[str, None],
        operation_id: str
    ) -> AsyncGenerator[str, None]:
        """Stream with timeout and metrics tracking."""
        start_time = time.time()
        chunk_count = 0
        total_chars = 0
        last_chunk_time = start_time

        try:
            async for chunk in stream_generator:
                current_time = time.time()

                # Check for stream timeout (time between chunks)
                time_since_last_chunk = current_time - last_chunk_time
                if time_since_last_chunk > self.config.stream_timeout:
                    logger.warning(
                        f"Stream timeout exceeded: {time_since_last_chunk:.2f}s "
                        f"between chunks (operation: {operation_id})"
                    )

                # Check total response time
                total_time = current_time - start_time
                if total_time > self.config.max_response_time:
                    logger.error(
                        f"Max response time exceeded: {total_time:.2f}s "
                        f"(operation: {operation_id})"
                    )
                    break

                chunk_count += 1
                total_chars += len(chunk)
                last_chunk_time = current_time

                yield chunk

        except asyncio.TimeoutError:
            logger.error(f"Stream timeout for operation: {operation_id}")
            raise
        except Exception as error:
            logger.error(f"Stream error for operation {operation_id}: {error}")
            raise
        finally:
            # Record metrics
            total_time = time.time() - start_time
            self._record_metrics(operation_id, total_time, chunk_count, total_chars)

    def _record_metrics(
        self,
        operation_id: str,
        total_time: float,
        chunk_count: int,
        total_chars: int
    ):
        """Record latency metrics."""
        metrics = {
            "operation_id": operation_id,
            "total_time": round(total_time, 3),
            "chunk_count": chunk_count,
            "total_chars": total_chars,
            "chars_per_second": round(total_chars / total_time, 2) if total_time > 0 else 0,
            "chunks_per_second": round(chunk_count / total_time, 2) if total_time > 0 else 0,
            "avg_chunk_size": round(total_chars / chunk_count, 2) if chunk_count > 0 else 0,
            "timestamp": time.time()
        }

        # Store recent metrics (keep last 100)
        if len(self.request_metrics) > 100:
            # Remove oldest entry
            oldest_key = min(self.request_metrics.keys(),
                           key=lambda k: self.request_metrics[k]["timestamp"])
            del self.request_metrics[oldest_key]

        self.request_metrics[operation_id] = metrics

        # Log performance
        if total_time > self.config.max_response_time * 0.8:  # Warn at 80% of max
            logger.warning(
                f"Slow response detected: {total_time:.2f}s "
                f"({metrics['chars_per_second']} chars/s, operation: {operation_id})"
            )
        else:
            logger.info(
                f"Response completed: {total_time:.2f}s "
                f"({metrics['chars_per_second']} chars/s, "
                f"{chunk_count} chunks, operation: {operation_id})"
            )

    async def with_timeout(self, coro, timeout: Optional[float] = None):
        """Execute coroutine with timeout."""
        timeout = timeout or self.config.request_timeout
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Request timeout after {timeout}s")
            raise

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.request_metrics:
            return {"status": "no_data"}

        metrics_list = list(self.request_metrics.values())
        total_requests = len(metrics_list)

        avg_time = sum(m["total_time"] for m in metrics_list) / total_requests
        avg_chars_per_sec = sum(m["chars_per_second"] for m in metrics_list) / total_requests

        slow_requests = [m for m in metrics_list if m["total_time"] > self.config.max_response_time * 0.8]
        slow_percentage = (len(slow_requests) / total_requests) * 100

        return {
            "total_requests": total_requests,
            "avg_response_time": round(avg_time, 3),
            "avg_chars_per_second": round(avg_chars_per_sec, 2),
            "slow_requests_percentage": round(slow_percentage, 2),
            "last_24h_requests": total_requests,  # Simplified for demo
            "performance_grade": self._calculate_performance_grade(avg_time, slow_percentage)
        }

    def _calculate_performance_grade(self, avg_time: float, slow_percentage: float) -> str:
        """Calculate performance grade."""
        if avg_time < 2.0 and slow_percentage < 5:
            return "A"
        elif avg_time < 5.0 and slow_percentage < 15:
            return "B"
        elif avg_time < 10.0 and slow_percentage < 30:
            return "C"
        else:
            return "D"


# Global latency optimizer instance
default_latency_optimizer = LatencyOptimizer(LatencyConfig())
