"""Minimal configuration for caliper_v2."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Minimal settings for caliper_v2."""

    # Core paths
    db_path: Path = Path("data_v2/caliper.db")
    output_dir: Path = Path("outputs")
    data_dir: Path = Path("data_v2")

    # Provider settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    google_api_key: Optional[str] = None  # For Google AI Studio
    google_application_credentials: Optional[str] = None
    xai_api_key: Optional[str] = None
    xai_api_base: str = "https://api.x.ai/v1"
    cohere_api_key: Optional[str] = None
    llama_cloud_api_key: Optional[str] = None

    # Default model selection (optional)
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    embed_provider: Optional[str] = None
    embed_model: Optional[str] = None

    # Feature flags
    use_reranking: bool = True
    use_hybrid_search: bool = True
    hybrid_alpha: float = 0.5

    # Retrieval settings
    retrieval_top_k: int = 100
    chunk_size: int = 2000
    chunk_overlap: int = 400

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields from .env


# Global settings instance
settings = Settings()
