"""
Cache-Augmented Generation (CAG) system for 10x faster responses.

This module provides intelligent caching with:
- Semantic similarity matching for cache hits
- Multi-level caching (exact, similar, embedding-based)
- LRU eviction and TTL expiration
- Performance metrics and monitoring
"""

from src.cag.cag_service import CAGPerformanceMetrics, CAGQuery, CAGResult, CAGService

__all__ = [
    "CAGService",
    "CAGQuery",
    "CAGResult",
    "CAGPerformanceMetrics",
]
