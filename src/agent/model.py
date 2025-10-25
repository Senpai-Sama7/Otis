"""Ollama model wrapper with streaming support and retry/backoff."""

import asyncio
from typing import Any, AsyncIterator, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class OllamaModel:
    """Ollama LLM client wrapper with streaming support and retry/backoff."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 300,
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def infer(
        self,
        prompt: str,
        temperature: float = 0.1,
        top_p: float = 0.9,
        num_ctx: int = 1536,
    ) -> str:
        """
        Generate a response from the Ollama model with deterministic parameters.

        Args:
            prompt: The input prompt
            temperature: Temperature for generation (default: 0.1 for deterministic)
            top_p: Top-p sampling parameter (default: 0.9)
            num_ctx: Context window size (default: 1536)

        Returns:
            Generated text response
        """
        logger.info("Sending inference request", model=self.model, prompt_len=len(prompt))

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_ctx": num_ctx,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()

            generated_text = result.get("response", "")
            logger.info(
                "Inference completed",
                response_len=len(generated_text),
                done=result.get("done"),
            )

            return generated_text

        except httpx.HTTPError as e:
            logger.error("Ollama inference failed", error=str(e))
            raise

    async def infer_stream(
        self,
        prompt: str,
        temperature: float = 0.1,
        top_p: float = 0.9,
        num_ctx: int = 1536,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response from the Ollama model.

        Args:
            prompt: The input prompt
            temperature: Temperature for generation
            top_p: Top-p sampling parameter
            num_ctx: Context window size

        Yields:
            Generated text chunks
        """
        logger.info("Sending streaming inference request", model=self.model)

        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_ctx": num_ctx,
                    },
                },
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line:
                        import json

                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                        if chunk.get("done"):
                            break

        except httpx.HTTPError as e:
            logger.error("Ollama streaming inference failed", error=str(e))
            raise


async def infer(
    prompt: str, temperature: float = 0.1, top_p: float = 0.9, num_ctx: int = 1536
) -> str:
    """
    Convenience function for inference using default model.

    Args:
        prompt: The input prompt
        temperature: Temperature for generation (default: 0.1)
        top_p: Top-p sampling parameter (default: 0.9)
        num_ctx: Context window size (default: 1536)

    Returns:
        Generated text response
    """
    model = OllamaModel()
    try:
        return await model.infer(prompt, temperature, top_p, num_ctx)
    finally:
        await model.close()
