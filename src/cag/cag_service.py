"""
Cache-Augmented Generation (CAG) Service.

Provides 10x faster responses through intelligent caching with semantic similarity matching.
"""

import asyncio
import hashlib
import json
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class CAGQuery:
    """Query structure for CAG requests."""

    query: str
    context: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    use_cache: bool = True
    timeout: Optional[float] = None


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    response: str
    timestamp: datetime
    access_count: int = 0
    confidence: float = 0.0
    last_accessed: datetime = field(default_factory=datetime.now)
    ttl: float = 7200.0  # 2 hours default
    query_embedding: Optional[List[float]] = None
    context_hash: str = ""

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > self.ttl

    def touch(self) -> None:
        """Update access time and count."""
        self.access_count += 1
        self.last_accessed = datetime.now()


@dataclass
class CAGResult:
    """Result from CAG query."""

    response: str
    cached: bool
    confidence: float
    cache_hit_type: str  # 'exact', 'similar', 'none'
    processing_time: float
    similarity_score: Optional[float] = None


@dataclass
class CAGPerformanceMetrics:
    """Performance metrics for CAG system."""

    total_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    average_response_time: float = 0.0
    hit_rate: float = 0.0
    cache_size: int = 0
    evictions: int = 0

    def update_hit_rate(self) -> None:
        """Update hit rate calculation."""
        if self.total_queries > 0:
            self.hit_rate = self.cache_hits / self.total_queries


class CAGService:
    """
    Cache-Augmented Generation service providing intelligent response caching.

    Features:
    - Exact match caching
    - Semantic similarity matching
    - LRU eviction policy
    - TTL-based expiration
    - Performance metrics
    """

    def __init__(
        self,
        llm_client: Any,
        max_cache_size: int = 2000,
        similarity_threshold: float = 0.92,
        default_ttl: float = 7200.0,
        embedding_service: Optional[Any] = None,
    ):
        """
        Initialize CAG service.

        Args:
            llm_client: LLM client for generating responses
            max_cache_size: Maximum number of cache entries
            similarity_threshold: Minimum similarity score for cache hit
            default_ttl: Default time-to-live in seconds
            embedding_service: Optional embedding service for semantic matching
        """
        self.llm_client = llm_client
        self.max_cache_size = max_cache_size
        self.similarity_threshold = similarity_threshold
        self.default_ttl = default_ttl
        self.embedding_service = embedding_service

        # Cache storage (OrderedDict for LRU)
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()

        # Performance metrics
        self.metrics = CAGPerformanceMetrics()

        # Response time tracking
        self.response_times: List[float] = []
        self.max_response_time_history = 1000

        logger.info(
            "cag_service.initialized",
            max_cache_size=max_cache_size,
            similarity_threshold=similarity_threshold,
            default_ttl=default_ttl,
        )

        # Start background maintenance
        self._maintenance_task = None

    async def query(self, query: CAGQuery) -> CAGResult:
        """
        Execute CAG query with intelligent caching.

        Args:
            query: CAG query object

        Returns:
            CAGResult with response and cache information
        """
        start_time = time.time()
        self.metrics.total_queries += 1

        try:
            # Check for exact cache hit first
            if query.use_cache:
                exact_hit = await self._check_exact_cache(query)
                if exact_hit:
                    processing_time = time.time() - start_time
                    self._update_metrics(processing_time, cached=True)

                    logger.debug(
                        "cag_service.cache_hit",
                        hit_type="exact",
                        processing_time=processing_time,
                    )

                    return exact_hit

                # Check for similar cache hit
                similar_hit = await self._check_similar_cache(query)
                if similar_hit:
                    processing_time = time.time() - start_time
                    self._update_metrics(processing_time, cached=True)

                    logger.debug(
                        "cag_service.cache_hit",
                        hit_type="similar",
                        processing_time=processing_time,
                    )

                    return similar_hit

            # Cache miss - generate new response
            logger.debug("cag_service.cache_miss", query_length=len(query.query))
            result = await self._generate_and_cache(query)

            processing_time = time.time() - start_time
            self._update_metrics(processing_time, cached=False)

            return result

        except Exception as e:
            logger.error("cag_service.query_failed", error=str(e))
            raise

    async def _check_exact_cache(self, query: CAGQuery) -> Optional[CAGResult]:
        """Check for exact cache match."""
        cache_key = self._generate_cache_key(query)

        if cache_key in self.cache:
            entry = self.cache[cache_key]

            # Check if expired
            if entry.is_expired():
                del self.cache[cache_key]
                logger.debug("cag_service.cache_expired", key=cache_key[:16])
                return None

            # Update access info
            entry.touch()

            # Move to end (most recently used)
            self.cache.move_to_end(cache_key)

            self.metrics.cache_hits += 1

            return CAGResult(
                response=entry.response,
                cached=True,
                confidence=entry.confidence,
                cache_hit_type="exact",
                processing_time=0.0,
            )

        return None

    async def _check_similar_cache(self, query: CAGQuery) -> Optional[CAGResult]:
        """Check for semantically similar cache match."""
        if not self.embedding_service:
            return None

        # Get query embedding
        try:
            query_embedding = await self._get_embedding(query.query)
        except Exception as e:
            logger.error("cag_service.embedding_failed", error=str(e))
            return None

        # Find most similar cached entry
        best_similarity = 0.0
        best_entry = None
        best_key = None

        for key, entry in self.cache.items():
            if entry.is_expired():
                continue

            if entry.query_embedding is None:
                continue

            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, entry.query_embedding)

            if similarity > best_similarity:
                best_similarity = similarity
                best_entry = entry
                best_key = key

        # Check if similarity meets threshold
        if best_similarity >= self.similarity_threshold and best_entry:
            best_entry.touch()
            if best_key:
                self.cache.move_to_end(best_key)

            self.metrics.cache_hits += 1

            logger.debug(
                "cag_service.similar_cache_hit",
                similarity=best_similarity,
            )

            return CAGResult(
                response=best_entry.response,
                cached=True,
                confidence=best_entry.confidence,
                cache_hit_type="similar",
                processing_time=0.0,
                similarity_score=best_similarity,
            )

        return None

    async def _generate_and_cache(self, query: CAGQuery) -> CAGResult:
        """Generate new response and cache it."""
        self.metrics.cache_misses += 1

        # Generate response
        response = await self._generate_response(query)

        # Get embedding for semantic matching
        query_embedding = None
        if self.embedding_service:
            try:
                query_embedding = await self._get_embedding(query.query)
            except Exception as e:
                logger.error("cag_service.embedding_generation_failed", error=str(e))

        # Create cache entry
        cache_key = self._generate_cache_key(query)
        context_hash = self._hash_context(query.context)

        entry = CacheEntry(
            response=response,
            timestamp=datetime.now(),
            confidence=0.85,  # Default confidence
            ttl=self.default_ttl,
            query_embedding=query_embedding,
            context_hash=context_hash,
        )

        # Add to cache with eviction if needed
        self._add_to_cache(cache_key, entry)

        return CAGResult(
            response=response,
            cached=False,
            confidence=entry.confidence,
            cache_hit_type="none",
            processing_time=0.0,
        )

    async def _generate_response(self, query: CAGQuery) -> str:
        """Generate response using LLM."""
        prompt = query.query

        if query.context:
            context_str = json.dumps(query.context)
            prompt = f"Context: {context_str}\n\nQuery: {query.query}"

        response = await self.llm_client.generate(prompt, temperature=0.2, max_tokens=500)
        return response

    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text."""
        if self.embedding_service:
            return await self.embedding_service.get_embedding(text)
        # Fallback: simple character-based pseudo-embedding
        return [float(ord(c) % 256) / 255.0 for c in text[:128]]

    def _add_to_cache(self, key: str, entry: CacheEntry) -> None:
        """Add entry to cache with LRU eviction."""
        # Evict if at capacity
        if len(self.cache) >= self.max_cache_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.metrics.evictions += 1
            logger.debug("cag_service.cache_evicted", evicted_key=oldest_key[:16])

        self.cache[key] = entry
        self.metrics.cache_size = len(self.cache)

    def _generate_cache_key(self, query: CAGQuery) -> str:
        """Generate cache key from query."""
        key_data = {
            "query": query.query,
            "context": query.context,
            "category": query.category,
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _hash_context(self, context: Optional[Dict[str, Any]]) -> str:
        """Hash context for comparison."""
        if not context:
            return ""
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _update_metrics(self, processing_time: float, cached: bool) -> None:
        """Update performance metrics."""
        self.response_times.append(processing_time)
        if len(self.response_times) > self.max_response_time_history:
            self.response_times.pop(0)

        self.metrics.average_response_time = sum(self.response_times) / len(
            self.response_times
        )
        self.metrics.update_hit_rate()

    async def clear_cache(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.metrics.cache_size = 0
        logger.info("cag_service.cache_cleared")

    async def prewarm_cache(self, queries: List[CAGQuery]) -> int:
        """
        Pre-warm cache with common queries.

        Args:
            queries: List of queries to pre-generate and cache

        Returns:
            Number of queries cached
        """
        cached_count = 0
        for query in queries:
            try:
                await self.query(query)
                cached_count += 1
            except Exception as e:
                logger.error("cag_service.prewarm_failed", query=query.query[:50], error=str(e))

        logger.info("cag_service.prewarmed", count=cached_count)
        return cached_count

    def get_metrics(self) -> CAGPerformanceMetrics:
        """Get current performance metrics."""
        self.metrics.cache_size = len(self.cache)
        return self.metrics

    async def export_cache(self, filepath: Path) -> None:
        """Export cache to file."""
        cache_data = {
            "entries": [
                {
                    "key": key,
                    "response": entry.response,
                    "timestamp": entry.timestamp.isoformat(),
                    "access_count": entry.access_count,
                    "confidence": entry.confidence,
                }
                for key, entry in self.cache.items()
            ],
            "metrics": {
                "total_queries": self.metrics.total_queries,
                "cache_hits": self.metrics.cache_hits,
                "cache_misses": self.metrics.cache_misses,
                "hit_rate": self.metrics.hit_rate,
            },
        }

        with open(filepath, "w") as f:
            json.dump(cache_data, f, indent=2)

        logger.info("cag_service.cache_exported", filepath=str(filepath))

    async def import_cache(self, filepath: Path) -> None:
        """Import cache from file."""
        try:
            with open(filepath, "r") as f:
                cache_data = json.load(f)

            for entry_data in cache_data.get("entries", []):
                key = entry_data["key"]
                entry = CacheEntry(
                    response=entry_data["response"],
                    timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                    access_count=entry_data.get("access_count", 0),
                    confidence=entry_data.get("confidence", 0.85),
                )
                self.cache[key] = entry

            self.metrics.cache_size = len(self.cache)
            logger.info("cag_service.cache_imported", count=len(self.cache))

        except Exception as e:
            logger.error("cag_service.import_failed", error=str(e))

    async def start_maintenance(self) -> None:
        """Start background cache maintenance task."""
        if self._maintenance_task is None or self._maintenance_task.done():
            self._maintenance_task = asyncio.create_task(self._maintenance_loop())
            logger.info("cag_service.maintenance_started")

    async def _maintenance_loop(self) -> None:
        """Background task for cache maintenance."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._cleanup_expired()
            except Exception as e:
                logger.error("cag_service.maintenance_error", error=str(e))

    async def _cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        expired_keys = [
            key for key, entry in self.cache.items() if entry.is_expired()
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.info("cag_service.expired_removed", count=len(expired_keys))

        self.metrics.cache_size = len(self.cache)
