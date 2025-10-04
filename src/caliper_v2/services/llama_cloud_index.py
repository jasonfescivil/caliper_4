from __future__ import annotations

import os
from typing import Any, List, Optional

from loguru import logger

try:
    # Official LlamaCloud SDK
    from llama_cloud_services import LlamaCloudIndex as _SDKLlamaCloudIndex  # type: ignore
except Exception as exc:  # pragma: no cover - dependency provided at runtime (Colab)
    _SDKLlamaCloudIndex = None  # type: ignore


class LlamaCloudIndex:
    """Thin wrapper around official LlamaCloud SDK `LlamaCloudIndex`.

    - Prefer index_id (UUID). If only a name is available, pass `name` and optional `project_name`.
    - Reads LLAMA_CLOUD_API_KEY from env if not provided.
    - Optional LLAMA_CLOUD_BASE_URL for region selection (EU SaaS, etc.).
    """

    def __init__(
        self,
        index_id: Optional[str] = None,
        *,
        name: Optional[str] = None,
        project_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        if _SDKLlamaCloudIndex is None:
            raise ImportError(
                "llama-cloud-services is not installed. Install with: pip install llama-cloud-services"
            )
        if not index_id and not name:
            raise ValueError("Provide either index_id or name for LlamaCloudIndex")

        self.api_key = api_key or os.getenv("LLAMA_CLOUD_API_KEY") or ""
        if not self.api_key:
            raise RuntimeError("LLAMA_CLOUD_API_KEY is required for LlamaCloudIndex")
        self.base_url = base_url or os.getenv("LLAMA_CLOUD_BASE_URL")

        # Construct underlying SDK index
        try:
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            if project_name:
                kwargs["project_name"] = project_name
            if index_id:
                self._sdk = _SDKLlamaCloudIndex(index_id=index_id, **kwargs)  # type: ignore[arg-type]
                self._label = index_id
            else:
                # name path (positional name per SDK docs)
                self._sdk = _SDKLlamaCloudIndex(name, **kwargs)  # type: ignore[arg-type]
                self._label = name or "unknown"
        except Exception as exc:
            logger.error("Failed to initialize LlamaCloudIndex: {}", exc)
            raise

    def as_retriever(self, similarity_top_k: int = 20, **kwargs):
        """Return an SDK retriever, forwarding hybrid params when provided.

        Supported forwarded kwargs include (subject to SDK version):
        - retrieval_mode
        - dense_similarity_top_k
        - sparse_similarity_top_k
        - alpha
        - enable_reranking
        - rerank_top_n
        - filters
        - enable_filter_inference
        - retrieve_page_figure_nodes, etc.
        """
        try:
            return self._sdk.as_retriever(similarity_top_k=similarity_top_k, **kwargs)
        except TypeError:
            # Fallback for older SDKs that don't accept extra kwargs
            return self._sdk.as_retriever(similarity_top_k=similarity_top_k)
        except Exception as exc:
            logger.error("Failed to obtain retriever for cloud index {}: {}", self._label, exc)
            raise

    def retrieve(self, query: str, top_k: int = 20, **kwargs) -> List[Any]:
        """Convenience method to retrieve from the cloud index.

        Forwards hybrid kwargs to the underlying SDK retriever (see as_retriever).
        """
        return self.as_retriever(similarity_top_k=top_k, **kwargs).retrieve(query)


