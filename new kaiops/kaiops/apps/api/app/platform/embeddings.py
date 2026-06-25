from __future__ import annotations

import math
from dataclasses import dataclass

from openai import AsyncAzureOpenAI, AsyncOpenAI

from app.core.config import settings

VECTOR_DIMENSION = 1536


@dataclass(frozen=True)
class EmbeddedChunk:
    chunk_index: int
    content: str
    embedding: list[float]


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 120) -> list[str]:
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0

    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class EmbeddingClient:
    async def embed(self, text: str) -> list[float]:
        provider = settings.embedding_provider.lower()
        if provider == "openai":
            return await self._embed_openai(text)
        if provider == "azure_openai":
            return await self._embed_azure_openai(text)
        raise ValueError("embedding_provider must be openai or azure_openai")

    async def _embed_openai(self, text: str) -> list[float]:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when embedding_provider=openai")

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.embeddings.create(model=settings.openai_embedding_model, input=text)
        return response.data[0].embedding

    async def _embed_azure_openai(self, text: str) -> list[float]:
        if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
            raise ValueError(
                "AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY are required when embedding_provider=azure_openai"
            )

        deployment = settings.azure_openai_embedding_deployment
        if not deployment:
            raise ValueError("AZURE_OPENAI_EMBEDDING_DEPLOYMENT is required when embedding_provider=azure_openai")

        client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version="2024-02-15-preview",
        )
        response = await client.embeddings.create(model=deployment, input=text)
        return response.data[0].embedding


embedding_client = EmbeddingClient()
