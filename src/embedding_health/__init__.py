"""Embedding quality checks for RAG and vector-search pipelines."""

from embedding_health.checks import check_embeddings
from embedding_health.models import EmbeddingRecord, Finding

__all__ = ["EmbeddingRecord", "Finding", "check_embeddings"]
__version__ = "0.1.0"

