"""Ollama service for LLM inference."""
import json
from typing import AsyncIterator, Optional

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
        self, prompt: str, system: Optional[str] = None, temperature: float = 0.7
    ) -> str:
        """Generate a response from the LLM."""
        logger.info("Generating LLM response", model=self.model, prompt_length=len(prompt))

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature},
            }
            if system:
                payload["system"] = system

            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info("LLM response generated", response_length=len(result.get("response", "")))
            return result.get("response", "")

    async def generate_stream(
        self, prompt: str, system: Optional[str] = None, temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Generate a streaming response from the LLM."""
        logger.info(
            "Starting streaming LLM response", model=self.model, prompt_length=len(prompt)
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
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
                            continue

    async def check_health(self) -> bool:
        """Check if Ollama service is available."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error("Ollama health check failed", error=str(e))
            return False
