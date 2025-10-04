"""Provider-specific optimization profiles for RAG generation.

This module defines optimal parameter configurations for each frontier LLM model
when used for RAG (Retrieval-Augmented Generation) tasks. Different models have
different optimal settings for temperature, max_tokens, context window utilization, etc.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Literal
import fnmatch


@dataclass
class RAGProfile:
    """Profile for optimizing a model for RAG tasks.

    Attributes:
        temperature: Sampling temperature (0.0-2.0). Higher = more creative/varied.
        max_tokens: Maximum output tokens. None = unlimited.
        timeout: Timeout in seconds for API calls.
        max_retries: Number of retry attempts on failure.
        max_context_nodes: Maximum number of retrieved documents to include.
        prompt_format: Format style - "standard", "xml", "reasoning-structured".
        reasoning_enabled: For Cohere Command-A-Reasoning - enable reasoning mode.
        token_budget: For Cohere Command-A-Reasoning - "low", "medium", "high".
        reasoning_mode: For Grok - "extended", "minimal", etc.
    """
    temperature: float
    max_tokens: Optional[int]
    timeout: float
    max_retries: int
    max_context_nodes: int
    prompt_format: str = "standard"

    # Provider-specific parameters
    reasoning_enabled: Optional[bool] = None
    token_budget: Optional[Literal["low", "medium", "high"]] = None
    reasoning_mode: Optional[str] = None


# Optimized profiles for each frontier model
MODEL_RAG_PROFILES: Dict[str, Dict[str, RAGProfile]] = {
    "openai": {
        "gpt-5*": RAGProfile(
            temperature=1.0,
            max_tokens=None,  # Unlimited
            timeout=300,
            max_retries=2,
            max_context_nodes=40,
            prompt_format="standard",
        ),
        "gpt-4.1*": RAGProfile(
            temperature=1.0,
            max_tokens=16384,
            timeout=240,
            max_retries=2,
            max_context_nodes=40,
            prompt_format="standard",
        ),
        "gpt-4*": RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=240,
            max_retries=2,
            max_context_nodes=40,
            prompt_format="standard",
        ),
    },

    "grok": {
        # Grok 4 Fast - RECOMMENDED for large-context RAG ⭐
        "grok-4-fast-reasoning": RAGProfile(
            temperature=1.0,
            max_tokens=16384,  # 2x others
            timeout=600,  # 2x GPT-5 for deep reasoning
            max_retries=3,
            max_context_nodes=200,  # Leverage 2M window!
            prompt_format="reasoning-structured",
            reasoning_mode="extended",
        ),
        "grok-4-fast-non-reasoning": RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=100,  # Still 2.5x default
            prompt_format="standard",
        ),
        "grok-4-fast": RAGProfile(  # Generic - route to reasoning
            temperature=1.0,
            max_tokens=16384,
            timeout=600,
            max_retries=3,
            max_context_nodes=200,
            prompt_format="reasoning-structured",
        ),
        # Grok 4 original - NOT RECOMMENDED (expensive, small context)
        "grok-4-0709": RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=50,  # Limited by 256k context
            prompt_format="standard",
        ),
        "grok-4*": RAGProfile(  # Fallback for grok-4 variants
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=50,
            prompt_format="standard",
        ),
        # Grok 3 family
        "grok-3*": RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=40,
            prompt_format="standard",
        ),
    },

    "xai": {  # Mirror of grok profiles (same provider)
        "grok-4-fast-reasoning": RAGProfile(
            temperature=1.0,
            max_tokens=16384,
            timeout=600,
            max_retries=3,
            max_context_nodes=200,
            prompt_format="reasoning-structured",
            reasoning_mode="extended",
        ),
        "grok-4-fast-non-reasoning": RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=100,
            prompt_format="standard",
        ),
        "grok-4-fast": RAGProfile(
            temperature=1.0,
            max_tokens=16384,
            timeout=600,
            max_retries=3,
            max_context_nodes=200,
            prompt_format="reasoning-structured",
        ),
        "grok-4*": RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=50,
            prompt_format="standard",
        ),
        "grok-3*": RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=40,
            prompt_format="standard",
        ),
    },

    "cohere": {
        # Command-A-Reasoning - purpose-built for RAG ⭐
        "command-a-reasoning*": RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=80,  # 256K context
            prompt_format="command-a-reasoning",  # Optimized prompt with preamble & reasoning instructions
            reasoning_enabled=True,  # Enable reasoning for RAG
            token_budget="high",  # Max quality for synthesis
        ),
        "command-a*": RAGProfile(  # Base Command-A (no reasoning)
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=80,
            prompt_format="standard",
        ),
        "command-r-plus*": RAGProfile(  # Older model
            temperature=1.0,
            max_tokens=4000,
            timeout=240,
            max_retries=2,
            max_context_nodes=40,
            prompt_format="standard",
        ),
        "command-r*": RAGProfile(  # Older model
            temperature=1.0,
            max_tokens=4000,
            timeout=240,
            max_retries=2,
            max_context_nodes=40,
            prompt_format="standard",
        ),
    },

    "anthropic": {
        # Claude Sonnet 4.5 - Most intelligent, tends toward brevity ⭐
        "claude-sonnet-4-5*": RAGProfile(  # API uses hyphens: claude-sonnet-4-5
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=80,  # 1M context
            prompt_format="claude-sonnet-4-5",  # Optimized: explicit thoroughness guidance
        ),
        # Claude Opus 4.1 - Extended reasoning, autonomous operation ⭐
        "claude-opus-4-1*": RAGProfile(  # API uses hyphens: claude-opus-4-1
            temperature=1.0,
            max_tokens=8192,
            timeout=360,  # Longer for extended thinking
            max_retries=2,
            max_context_nodes=60,  # 200K context
            prompt_format="claude-opus-4-1",  # Optimized: reasoning-focused with thinking tags
        ),
        # Generic Claude Sonnet 4 (earlier versions)
        "claude-sonnet-4*": RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=80,  # 1M context
            prompt_format="xml",  # Basic XML
        ),
        # Generic Claude Opus 4 (earlier versions)
        "claude-opus-4*": RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=60,  # 200K context
            prompt_format="xml",  # Basic XML
        ),
        "claude-*": RAGProfile(  # Fallback for other Claude models
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=60,
            prompt_format="xml",
        ),
    },

    "gemini": {
        # Gemini 2.5 Pro - Advanced reasoning, complex data synthesis ⭐
        "gemini-2.5-pro*": RAGProfile(
            temperature=1.0,
            max_tokens=16384,  # Increased from 8192 (model supports 65K)
            timeout=300,
            max_retries=2,
            max_context_nodes=80,  # 1M context window (2M coming soon)
            prompt_format="gemini-2.5-pro",  # Optimized: markdown structure, clear delimiters, role definition
        ),
        "gemini-2*": RAGProfile(  # Fallback for other Gemini 2.x versions
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=80,  # 1M context
            prompt_format="standard",
        ),
        "gemini-1.5*": RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=80,
            prompt_format="standard",
        ),
        "gemini-*": RAGProfile(  # Fallback
            temperature=1.0,
            max_tokens=8192,
            timeout=240,
            max_retries=2,
            max_context_nodes=60,
            prompt_format="standard",
        ),
    },
}


def get_rag_profile(provider: str, model: str) -> RAGProfile:
    """Get RAG-optimized parameters for a specific model.

    Args:
        provider: Provider name (e.g., "openai", "anthropic", "cohere", "grok")
        model: Model name (e.g., "gpt-5", "claude-sonnet-4", "grok-4-fast-reasoning")

    Returns:
        RAGProfile with optimized settings for the specified model.
        Falls back to sensible defaults if model not found.

    Examples:
        >>> profile = get_rag_profile("grok", "grok-4-fast-reasoning")
        >>> print(profile.max_context_nodes)  # 200
        >>> print(profile.prompt_format)  # "reasoning-structured"
    """
    provider = provider.lower()

    if provider not in MODEL_RAG_PROFILES:
        # Return safe defaults for unknown providers
        return RAGProfile(
            temperature=1.0,
            max_tokens=8192,
            timeout=300,
            max_retries=2,
            max_context_nodes=40,
            prompt_format="standard",
        )

    profiles = MODEL_RAG_PROFILES[provider]

    # Try exact match first
    if model in profiles:
        return profiles[model]

    # Match by pattern (e.g., "gpt-5*" matches "gpt-5", "gpt-5-mini", etc.)
    for pattern, profile in profiles.items():
        if fnmatch.fnmatch(model, pattern):
            return profile

    # Fallback to first profile if no match (better than generic defaults)
    if profiles:
        return list(profiles.values())[0]

    # Ultimate fallback
    return RAGProfile(
        temperature=1.0,
        max_tokens=8192,
        timeout=300,
        max_retries=2,
        max_context_nodes=40,
        prompt_format="standard",
    )


def list_supported_providers() -> list[str]:
    """Get list of providers with defined RAG profiles."""
    return list(MODEL_RAG_PROFILES.keys())


def list_provider_models(provider: str) -> list[str]:
    """Get list of model patterns for a provider."""
    provider = provider.lower()
    if provider in MODEL_RAG_PROFILES:
        return list(MODEL_RAG_PROFILES[provider].keys())
    return []


def get_context_capacity_ranking() -> list[tuple[str, str, int]]:
    """Get models ranked by context capacity (max_context_nodes).

    Returns:
        List of (provider, model_pattern, max_nodes) tuples, sorted descending.
    """
    capacities = []
    for provider, models in MODEL_RAG_PROFILES.items():
        for model_pattern, profile in models.items():
            capacities.append((provider, model_pattern, profile.max_context_nodes))

    return sorted(capacities, key=lambda x: x[2], reverse=True)
