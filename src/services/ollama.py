"""Ollama service for LLM inference."""

import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class OllamaService:
    """Service for interacting with Ollama LLM."""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The input prompt
            system: Optional system message
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response text

        Raises:
            httpx.HTTPError: If the request fails
        """
        logger.info("Generating LLM response", model=self.model, prompt_length=len(prompt))

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload: dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature},
            }
            if system:
                payload["system"] = system
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            try:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()

                result: dict[str, Any] = response.json()
                generated_text: str = result.get("response", "")
                logger.info("LLM response generated", response_length=len(generated_text))
                return generated_text
            except httpx.HTTPError as e:
                logger.error(
                    "LLM generation failed",
                    error=str(e),
                    status_code=getattr(e.response, "status_code", None),
                )
                raise

    async def generate_stream(
        self, prompt: str, system: str | None = None, temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response from the LLM.

        Args:
            prompt: The input prompt
            system: Optional system message
            temperature: Sampling temperature (0.0-1.0)

        Yields:
            Generated text chunks

        Raises:
            httpx.HTTPError: If the request fails
        """
        logger.info("Starting streaming LLM response", model=self.model, prompt_length=len(prompt))

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload: dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {"temperature": temperature},
            }
            if system:
                payload["system"] = system

            async with client.stream(
                "POST", f"{self.base_url}/api/generate", json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            logger.warning("Failed to decode streaming response line", line=line)
                            continue

    async def check_health(self) -> bool:
        """
        Check if Ollama service is available.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                is_healthy = response.status_code == 200
                if is_healthy:
                    logger.debug("Ollama health check passed")
                else:
                    logger.warning("Ollama health check failed", status_code=response.status_code)
                return is_healthy
        except Exception as e:
            logger.error("Ollama health check failed", error=str(e))
            return False
