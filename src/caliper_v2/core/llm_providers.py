"""
Multi-provider LLM configuration for Caliper v2.

Supports OpenAI, Anthropic, Google Gemini, and xAI Grok models.
"""

from typing import Optional
import os

from llama_index.core import Settings
from loguru import logger


def configure_llm_provider(
    provider: str = "openai", model: Optional[str] = None, api_key: Optional[str] = None, **kwargs
) -> None:
    """
    Configure the LLM provider for LlamaIndex.

    Args:
        provider: One of "openai", "anthropic", "gemini", "grok", "google" (alias for gemini)
        model: Specific model to use (defaults to provider's best model)
        api_key: API key for the provider
        **kwargs: Additional provider-specific parameters
    """

    provider = provider.lower()
    
    # Normalize provider aliases
    if provider == "google":
        provider = "gemini"
    elif provider == "grok":
        provider = "xai"

    if provider == "openai":
        import os

        from llama_index.llms.openai import OpenAI

        # IMPORTANT: Do NOT up-convert stable aliases to dated variants.
        # Many OpenAI Projects allowlist aliases like 'gpt-5-mini' but not a
        # specific dated ID (e.g., 'gpt-5-mini-2025-08-07'). Converting aliases
        # to dated variants can trigger 403 model_not_found in allowed projects.
        #
        # Instead, preserve user-provided aliases and only normalize common
        # dated variants back to the stable alias so both forms work.
        model = (model or "gpt-5").strip()
        reverse_alias_map = {
            "gpt-5-2025-08-07": "gpt-5",
            "gpt-5-mini-2025-08-07": "gpt-5-mini",
            "gpt-5-nano-2025-08-07": "gpt-5-nano",
            "gpt-4o-mini": "gpt-5-mini",  # Map gpt-4o-mini to gpt-5-mini if that's what the user has access to
        }
        normalized_model = reverse_alias_map.get(model, model)
        if normalized_model != model:
            logger.warning(f"Normalizing OpenAI model '{model}' -> '{normalized_model}' (using stable alias)")
            model = normalized_model

        api_key = api_key or os.getenv("OPENAI_API_KEY")

        # Allow org/project scoping via env if provided (robust across client versions)
        # These are not secrets and help avoid 404/403 against non-default projects.
        org_env = os.getenv("OPENAI_ORG") or os.getenv("OPENAI_ORGANIZATION") or os.getenv("CALIPER_OPENAI_ORG_ID")
        proj_env = os.getenv("OPENAI_PROJECT") or os.getenv("CALIPER_OPENAI_PROJECT_ID")
        if org_env:
            os.environ.setdefault("OPENAI_ORG", org_env)
            os.environ.setdefault("OPENAI_ORGANIZATION", org_env)
        if proj_env:
            os.environ.setdefault("OPENAI_PROJECT", proj_env)

        # Runtime patch for llama_index openai utils when using newer models (e.g., GPT-5)
        # Older llama-index-llms-openai versions may not recognize these model IDs and will throw
        # in openai_modelname_to_contextsize(). Patch the registry to avoid hard failures.
        try:
            from llama_index.llms.openai import utils as openai_utils  # type: ignore
            # Ensure dicts exist
            for dict_name in ("ALL_AVAILABLE_MODELS", "CHAT_MODELS"):
                if not hasattr(openai_utils, dict_name):
                    setattr(openai_utils, dict_name, {})
            if not hasattr(openai_utils, "O1_MODELS"):
                openai_utils.O1_MODELS = {}
            # Canonical GPT-5 family entries (frontier models)
            gpt5_variants = {
                "gpt-5": 400000,
                "gpt-5-2025-08-07": 400000,
                "gpt-5-mini": 400000,
                "gpt-5-mini-2025-08-07": 400000,
                "gpt-5-nano": 400000,
                "gpt-5-nano-2025-08-07": 400000,
                "gpt-5-chat-latest": 400000,
                "gpt-4o": 128000,
                "gpt-4o-mini": 128000,
            }
            # Populate submaps consistently
            openai_utils.O1_MODELS.update({k: v for k, v in gpt5_variants.items()})
            if isinstance(openai_utils.ALL_AVAILABLE_MODELS, dict):
                openai_utils.ALL_AVAILABLE_MODELS.update({k: v for k, v in gpt5_variants.items()})
            if isinstance(openai_utils.CHAT_MODELS, dict):
                openai_utils.CHAT_MODELS.update({k: v for k, v in gpt5_variants.items()})
            logger.debug("Patched llama_index OpenAI model registry with GPT-5 variants")
        except Exception as _patch_exc:
            logger.debug(f"Could not patch OpenAI utils registry for GPT-5: {_patch_exc}")

        # Handle newer models that aren't in LlamaIndex validation yet
        newer_models = [
            "gpt-5",
            "gpt-5-",  # any dated variant
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "o3",
            "o3-mini",
            "o3-pro",
            "o4",
            "o4-mini",
        ]
        if any(model.startswith(nm) for nm in newer_models):
            # GPT-5 and newer models: default to temperature=1.0 unless explicitly set
            if "temperature" not in kwargs:
                kwargs["temperature"] = 1.0

            # Increase default timeout/retries for GPT-5 family (configurable via env)
            is_gpt5 = model.startswith("gpt-5")
            try:
                timeout_env = os.getenv("CALIPER_OPENAI_TIMEOUT_S") or os.getenv("CALIPER_LLM_TIMEOUT_S")
                max_retries_env = os.getenv("CALIPER_OPENAI_MAX_RETRIES") or os.getenv("CALIPER_LLM_MAX_RETRIES")
                default_timeout = 300.0 if is_gpt5 else 120.0
                default_retries = 2 if is_gpt5 else 1
                eff_timeout = float(timeout_env) if timeout_env else default_timeout
                eff_retries = int(max_retries_env) if max_retries_env else default_retries
                if "timeout" not in kwargs:
                    kwargs["timeout"] = eff_timeout
                if "max_retries" not in kwargs:
                    kwargs["max_retries"] = eff_retries
                logger.info(f"OpenAI model={model}: timeout={kwargs.get('timeout')}s, max_retries={kwargs.get('max_retries')}")
            except Exception as _to_exc:
                logger.debug(f"Timeout/retry config parse skipped: {_to_exc}")

            # Use OpenAI-like wrapper to bypass model validation when available
            try:
                from llama_index.llms.openai_like import OpenAILike
                try:
                    llm = OpenAILike(
                        model=model,
                        api_key=api_key,
                        api_base="https://api.openai.com/v1",
                        is_chat_model=True,
                        **kwargs
                    )
                except TypeError as te:
                    # Drop unsupported kwargs for older adapters
                    _filtered = {k: v for k, v in kwargs.items() if k not in ("timeout", "max_retries")}
                    llm = OpenAILike(
                        model=model,
                        api_key=api_key,
                        api_base="https://api.openai.com/v1",
                        is_chat_model=True,
                        **_filtered
                    )
                logger.info(f"Configured OpenAI LLM (bypass validation): {model}")
            except ImportError:
                # Fallback to regular OpenAI with validation bypass attempt
                try:
                    try:
                        llm = OpenAI(model=model, api_key=api_key, validate_model=False, **kwargs)
                    except TypeError as te:
                        # Drop unsupported kwargs and/or validate_model for older versions
                        _filtered = {k: v for k, v in kwargs.items() if k not in ("timeout", "max_retries")}
                        try:
                            llm = OpenAI(model=model, api_key=api_key, validate_model=False, **_filtered)
                        except TypeError:
                            llm = OpenAI(model=model, api_key=api_key, **_filtered)
                    logger.info(f"Configured OpenAI LLM (validation disabled): {model}")
                except TypeError:
                    # If validate_model param doesn't exist, try without it
                    try:
                        llm = OpenAI(model=model, api_key=api_key, **kwargs)
                    except TypeError:
                        _filtered = {k: v for k, v in kwargs.items() if k not in ("timeout", "max_retries")}
                        llm = OpenAI(model=model, api_key=api_key, **_filtered)
                    logger.info(f"Configured OpenAI LLM (forced): {model}")
        else:
            # Non-newer models: still respect env timeouts if provided
            try:
                timeout_env = os.getenv("CALIPER_OPENAI_TIMEOUT_S") or os.getenv("CALIPER_LLM_TIMEOUT_S")
                max_retries_env = os.getenv("CALIPER_OPENAI_MAX_RETRIES") or os.getenv("CALIPER_LLM_MAX_RETRIES")
                if timeout_env and "timeout" not in kwargs:
                    kwargs["timeout"] = float(timeout_env)
                if max_retries_env and "max_retries" not in kwargs:
                    kwargs["max_retries"] = int(max_retries_env)
            except Exception:
                pass
            try:
                llm = OpenAI(model=model, api_key=api_key, **kwargs)
            except TypeError:
                _filtered = {k: v for k, v in kwargs.items() if k not in ("timeout", "max_retries")}
                llm = OpenAI(model=model, api_key=api_key, **_filtered)
            logger.info(f"Configured OpenAI LLM: {model}")

    elif provider == "anthropic":
        import os

        from llama_index.llms.anthropic import Anthropic
        
        # Add runtime mapping for Claude 4.x models that aren't in the adapter yet
        try:
            from llama_index.llms.anthropic import utils as anthropic_utils
            
            # Add Claude 4.x models to the mapping if not present (frontier models)
            claude_4_models = {
                "claude-opus-4-1-20250805": 200000,  # 200k context window
                "claude-opus-4": 200000,  # Alias for Claude Opus 4
                "claude-opus-4.1": 200000,  # Alias for Claude Opus 4.1
                "claude-sonnet-4-20250514": 1000000,  # 1M token context window
                "claude-sonnet-4": 1000000,  # Alias for Claude Sonnet 4
            }
            
            for model_id, context_window in claude_4_models.items():
                if model_id not in anthropic_utils.CLAUDE_MODELS:
                    anthropic_utils.CLAUDE_MODELS[model_id] = context_window
                    logger.debug(f"Added Claude 4.x model to runtime mapping: {model_id}")
        except Exception as e:
            logger.warning(f"Could not add Claude 4.x model mappings: {e}")

        # Default to frontier model, but normalize model names if needed
        model = model or "claude-sonnet-4"  # Default to frontier model
        
        # Normalize model names for consistency
        model_aliases = {
            "claude-opus-4.1": "claude-opus-4-1-20250805",
            "claude-opus-4": "claude-opus-4-1-20250805",  # Use latest Opus 4.1
        }
        
        if model in model_aliases:
            normalized_model = model_aliases[model]
            logger.info(f"Normalizing Anthropic model name from '{model}' to '{normalized_model}'")
            model = normalized_model
            
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        # Try to use the direct Anthropic client if available for better compatibility
        try:
            import importlib.util
            if importlib.util.find_spec("anthropic"):
                import anthropic as anthropic_direct
                
                # Check if we can use the direct client
                if hasattr(anthropic_direct, "Anthropic") and callable(getattr(anthropic_direct, "Anthropic")):
                    logger.info(f"Using direct Anthropic client with model: {model}")
                    
                    # Create a wrapper function that uses the direct client
                    def anthropic_direct_complete(prompt, **kwargs):
                        from llama_index.core.llms import ChatResponse, ChatMessage
                        client = anthropic_direct.Anthropic(api_key=api_key)
                        response = client.messages.create(
                            model=model,
                            max_tokens=kwargs.get("max_tokens", 4096),
                            temperature=kwargs.get("temperature", 0.7),
                            messages=[{"role": "user", "content": prompt}]
                        )
                        return ChatResponse(message=ChatMessage(role="assistant", content=response.content[0].text))
                    
                    # Create a simple LLM class that uses our wrapper
                    from llama_index.core.llms import LLM
                    class AnthropicDirectChat(LLM):
                        def complete(self, prompt, **kwargs):
                            return anthropic_direct_complete(prompt, **kwargs)
                        
                        def chat(self, messages, **kwargs):
                            # Extract the last user message if it's a list of messages
                            if isinstance(messages, list) and messages:
                                last_msg = messages[-1]
                                if hasattr(last_msg, "content"):
                                    prompt = last_msg.content
                                else:
                                    prompt = str(last_msg)
                            else:
                                prompt = str(messages)
                            return anthropic_direct_complete(prompt, **kwargs)
                    
                    llm = AnthropicDirectChat()
                    logger.info(f"Configured Anthropic LLM with direct client: {model}")
                    return
        except Exception as direct_exc:
            logger.debug(f"Could not use direct Anthropic client: {direct_exc}")
        
        # Fall back to LlamaIndex adapter
        llm = Anthropic(model=model, api_key=api_key, **kwargs)
        logger.info(f"Configured Anthropic LLM via LlamaIndex adapter: {model}")

    elif provider == "gemini":
        import os

        # Mode selection: 'auto' (default), 'api', or 'vertex'
        mode = (os.getenv("GEMINI_MODE") or os.getenv("GOOGLE_MODE") or "auto").lower()

        have_api_key = bool(api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
        have_sa = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

        # In 'auto' mode prefer API key if available (more portable for local dev)
        use_api = (mode == "api") or (mode == "auto" and have_api_key)
        use_vertex = (mode == "vertex") or (mode == "auto" and not have_api_key and have_sa)

        if use_api:
            api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY or GOOGLE_API_KEY not set. Provide an API key in your .env."
                )
        # Default to frontier model if none specified
        model = (model or "models/gemini-2.5-pro-preview").strip()
        
        # Ensure model has the 'models/' prefix for the native adapter
        if not model.startswith("models/") and not model.startswith("gemini-"):
            model = f"models/{model}"
        elif not model.startswith("models/") and model.startswith("gemini-"):
            model = f"models/{model}"
            
        try:
            # Try to install the missing protobuf dependency
            try:
                import importlib.util
                if importlib.util.find_spec("google.generativeai") and not importlib.util.find_spec("google.protobuf"):
                    import subprocess
                    import sys
                    logger.info("Installing missing protobuf dependency for Gemini native adapter")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "protobuf"])
            except Exception as pip_exc:
                logger.debug(f"Could not auto-install protobuf: {pip_exc}")
                
            from llama_index.llms.gemini import Gemini
            llm = Gemini(model=model, api_key=api_key, **kwargs)
            logger.info(f"Configured Google Gemini (native adapter) with model: {model}")
        except Exception as exc:
            # Fallback: use Google's OpenAI-compatible endpoint via the OpenAI-like adapter
            try:
                from llama_index.llms.openai_like import OpenAILike  # type: ignore
                # Strip leading 'models/' for OpenAI-compat if present
                compat_model = model.split("/", 1)[1] if model.startswith("models/") else model
                # Opportunistic downgrade for models that may not be available via OpenAI-compat yet
                if os.getenv("DISABLE_GEMINI_COMPAT_DOWNGRADE", "0") not in ("1", "true", "True"):
                    downgrade_map = {
                        "gemini-2.5-pro": "gemini-1.5-pro",
                        "gemini-2.5-flash": "gemini-1.5-flash",
                        "gemini-2.5-flash-lite": "gemini-1.5-flash",
                    }
                    if compat_model in downgrade_map:
                        mapped = downgrade_map[compat_model]
                        logger.warning(
                            f"Gemini model '{compat_model}' may not be available on the OpenAI-compatible endpoint; using '{mapped}' instead. Install google-generativeai+protobuf to use native '{compat_model}'."
                        )
                        compat_model = mapped
                # Build base URL (include '/v1') for openai-like adapter
                api_base = os.getenv("GOOGLE_OPENAI_COMPAT_BASE", "https://generativelanguage.googleapis.com/openai").rstrip("/") + "/v1"
                # Also set common environment variables some clients read
                os.environ.setdefault("OPENAI_BASE_URL", api_base)
                os.environ.setdefault("OPENAI_API_BASE", api_base)
                os.environ.setdefault("OPENAI_BASE", api_base)
                try:
                    llm = OpenAILike(
                        model=compat_model,
                        api_key=api_key,
                        api_base=api_base,
                        is_chat_model=True,
                        **kwargs
                    )
                except TypeError:
                    _filtered = {k: v for k, v in kwargs.items() if k not in ("timeout", "max_retries")}
                    llm = OpenAILike(
                        model=compat_model,
                        api_key=api_key,
                        api_base=api_base,
                        is_chat_model=True,
                        **_filtered
                    )
                logger.warning(
                    f"Gemini native adapter unavailable ({exc}); using OpenAI-compatible endpoint at {api_base} with model: {compat_model}"
                )
            except Exception as exc2:
                # Second fallback: use the OpenAI adapter pointed at Google's OpenAI-compatible endpoint
                try:
                    from llama_index.llms.openai import OpenAI as _OpenAI  # type: ignore
                    compat_model = model.split("/", 1)[1] if model.startswith("models/") else model
                    # Build a safe base URL to avoid '/v1/v1' issues across OpenAI SDK versions
                    base_root = os.getenv("GOOGLE_OPENAI_COMPAT_BASE", "https://generativelanguage.googleapis.com/openai").rstrip("/")
                    base_url = f"{base_root}/v1"
                    # Expose base URL via common env vars for downstream clients
                    os.environ.setdefault("OPENAI_BASE_URL", base_url)
                    os.environ.setdefault("OPENAI_API_BASE", base_url)
                    os.environ.setdefault("OPENAI_BASE", base_url)
                    # Patch OpenAI utils registries so Gemini model ids don't trigger validation errors
                    try:
                        from llama_index.llms.openai import utils as openai_utils  # type: ignore
                        for dict_name in ("ALL_AVAILABLE_MODELS", "CHAT_MODELS", "O1_MODELS"):
                            if not hasattr(openai_utils, dict_name):
                                setattr(openai_utils, dict_name, {})
                        gemini_models = {
                            # Common Gemini API-compatible ids (strip 'models/')
                            "gemini-1.0-pro": 200000,
                            "gemini-1.5-pro": 1000000,
                            "gemini-1.5-flash": 1000000,
                            "gemini-2.0-flash": 1000000,
                            "gemini-2.0-pro": 1000000,
                            "gemini-2.5-pro": 1000000,
                            "gemini-2.5-pro-preview": 1000000,  # Frontier model
                            "gemini-2.5-flash": 1000000,
                            "gemini-2.5-flash-lite": 1000000,
                        }
                        if isinstance(openai_utils.ALL_AVAILABLE_MODELS, dict):
                            openai_utils.ALL_AVAILABLE_MODELS.update(gemini_models)
                        if isinstance(openai_utils.CHAT_MODELS, dict):
                            openai_utils.CHAT_MODELS.update(gemini_models)
                        if hasattr(openai_utils, "O1_MODELS") and isinstance(openai_utils.O1_MODELS, dict):
                            openai_utils.O1_MODELS.update(gemini_models)
                        logger.debug("Patched OpenAI utils registry to include Gemini model ids for OpenAI-compatible endpoint")
                    except Exception as _patch_exc:
                        logger.debug(f"Could not patch OpenAI utils registry for Gemini models: {_patch_exc}")
                    # Try a few instantiation permutations for broad adapter compatibility
                    try:
                        # Prefer passing ONLY base_url to avoid '/v1/v1' path duplication on older clients
                        llm = _OpenAI(model=compat_model, api_key=api_key, base_url=base_url, validate_model=False, **kwargs)
                    except TypeError:
                        # Drop possibly unsupported kwargs
                        _filtered = {k: v for k, v in kwargs.items() if k not in ("timeout", "max_retries")}
                        try:
                            llm = _OpenAI(model=compat_model, api_key=api_key, base_url=base_url, validate_model=False, **_filtered)
                        except TypeError:
                            try:
                                # Fallback for very old adapters expecting 'api_base' (without appending another '/v1')
                                llm = _OpenAI(model=compat_model, api_key=api_key, api_base=base_url, validate_model=False, **_filtered)
                            except TypeError:
                                llm = _OpenAI(model=compat_model, api_key=api_key, base_url=base_url, **_filtered)
                    logger.warning(
                        f"Gemini native adapter unavailable ({exc}); using OpenAI adapter at {base_url} with model: {compat_model}"
                    )
                except Exception as exc3:
                    raise ImportError(
                        "Gemini configuration failed: native adapter import failed and both compatibility paths were unavailable. "
                        "Install 'google-generativeai' and 'protobuf' OR ensure your llama-index OpenAI adapter is recent."
                    ) from exc3

        if use_vertex and not use_api:
            try:
                from llama_index.llms.vertex import Vertex
            except ImportError:
                raise ImportError(
                    "Vertex AI dependencies not found. Please run 'poetry install' "
                    "or 'pip install llama-index-llms-vertex google-cloud-aiplatform'."
                )

            # Project and location configurable via env; no hardcoded default project
            project_id = (
                os.getenv("GCP_PROJECT")
                or os.getenv("VERTEX_PROJECT")
                or os.getenv("GOOGLE_CLOUD_PROJECT")
            )
            location = os.getenv("GCP_LOCATION") or os.getenv("VERTEX_LOCATION") or "us-central1"
            if not project_id:
                raise ValueError(
                    "Vertex mode selected but GCP project not set. Set GCP_PROJECT or VERTEX_PROJECT."
                )
            # Vertex model names typically omit the 'models/' prefix
            model = model or "gemini-1.0-pro-001"
            llm = Vertex(model=model, project=project_id, location=location, **kwargs)
            logger.info(
                f"Configured Google Vertex AI (service account) with model: {model}, project: {project_id}, location: {location}"
            )

        if not (use_api or use_vertex):
            # No Google credentials available
            raise ValueError(
                "No Google credentials found. Provide GEMINI_API_KEY/GOOGLE_API_KEY in .env for API mode, "
                "or GOOGLE_APPLICATION_CREDENTIALS for Vertex mode."
            )

    elif provider == "grok" or provider == "xai":
        # xAI Grok uses an OpenAI-compatible API; ensure the client points at xAI's base URL.
        import os

        model = model or os.getenv("XAI_MODEL") or "grok-4-fast-reasoning"  # Frontier model default - 2M context
        api_key = api_key or os.getenv("XAI_API_KEY")
        api_base = os.getenv("XAI_API_BASE", "https://api.x.ai/v1")

        # Support for grok-4-fast model variants
        if model in ["grok-4-fast", "grok-4-fast-reasoning", "grok-4-fast-non-reasoning"]:
            logger.info(f"Using Grok-4-Fast model variant: {model}")
        
        if not api_key:
            raise ValueError("XAI_API_KEY required for xAI/Grok provider")

        # Also set common environment variables used by various OpenAI clients
        # Different versions read different names; set several for robustness.
        os.environ.setdefault("OPENAI_BASE_URL", api_base)
        os.environ.setdefault("OPENAI_API_BASE", api_base)
        os.environ.setdefault("OPENAI_BASE", api_base)

        # Prefer the OpenAI-like adapter to bypass OpenAI model-name validation entirely.
        try:
            from llama_index.llms.openai_like import OpenAILike  # type: ignore
            llm = OpenAILike(
                model=model,
                api_key=api_key,
                api_base=api_base,
                is_chat_model=True,
                **kwargs
            )
            logger.info(f"Configured xAI Grok via OpenAI-like adapter: {model} at {api_base}")
        except Exception as openai_like_exc:
            # Fallback: use the OpenAI adapter but patch model registries so 'grok-*' doesn't error.
            try:
                from llama_index.llms.openai import OpenAI as _OpenAI
                try:
                    from llama_index.llms.openai import utils as openai_utils  # type: ignore
                    # Ensure registries exist
                    for dict_name in ("ALL_AVAILABLE_MODELS", "CHAT_MODELS", "O1_MODELS"):
                        if not hasattr(openai_utils, dict_name):
                            setattr(openai_utils, dict_name, {})
                    # Add xAI Grok model ids to avoid Unknown model errors during context window lookup (frontier models)
                    grok_models = {
                        # Grok 1-2 family
                        "grok-1": 131072,
                        "grok-2": 128000,
                        "grok-2-1212": 128000,
                        "grok-beta": 131072,

                        # Grok 3 family (supports reasoning_effort parameter)
                        "grok-3": 128000,
                        "grok-3-mini": 128000,
                        "grok-3-fast": 128000,
                        "grok-3-mini-fast": 128000,

                        # Grok 4 original (July 2025) - 256K context
                        "grok-4": 256000,
                        "grok-4-0709": 256000,
                        "grok-4-latest": 256000,

                        # Grok 4 Fast (September 2025) - 2M context - LARGEST FRONTIER MODEL ⭐
                        "grok-4-fast": 2000000,  # 2M tokens - generic alias
                        "grok-4-fast-reasoning": 2000000,  # 2M tokens - RECOMMENDED for RAG
                        "grok-4-fast-non-reasoning": 2000000,  # 2M tokens - fast responses
                    }
                    if isinstance(openai_utils.ALL_AVAILABLE_MODELS, dict):
                        openai_utils.ALL_AVAILABLE_MODELS.update(grok_models)
                    if isinstance(openai_utils.CHAT_MODELS, dict):
                        openai_utils.CHAT_MODELS.update(grok_models)
                    if hasattr(openai_utils, "O1_MODELS") and isinstance(openai_utils.O1_MODELS, dict):
                        openai_utils.O1_MODELS.update(grok_models)
                    logger.debug("Patched OpenAI utils registry to include xAI Grok model ids")
                except Exception as _patch_exc:
                    logger.debug(f"Could not patch OpenAI utils registry for xAI models: {_patch_exc}")
                # Instantiate OpenAI adapter pointing at x.ai endpoint; try both base_url and api_base
                try:
                    llm = _OpenAI(model=model, api_key=api_key, api_base=api_base, base_url=api_base, validate_model=False, **kwargs)
                    logger.info(f"Configured xAI Grok via OpenAI adapter (api_base/base_url): {model} at {api_base}")
                except TypeError:
                    try:
                        llm = _OpenAI(model=model, api_key=api_key, base_url=api_base, validate_model=False, **kwargs)
                        logger.info(f"Configured xAI Grok via OpenAI adapter (base_url): {model} at {api_base}")
                    except TypeError:
                        llm = _OpenAI(model=model, api_key=api_key, api_base=api_base, validate_model=False, **kwargs)
                        logger.info(f"Configured xAI Grok via OpenAI adapter (api_base): {model} at {api_base}")
            except Exception as exc2:
                raise ImportError(
                    "xAI/Grok configuration failed: neither OpenAI-like nor OpenAI adapter could be configured. "
                    "Please update llama-index-llms-openai to a recent version."
                ) from exc2

    elif provider == "cohere":
        # Cohere Command models. Use LlamaIndex Cohere adapter which routes to the Chat API.
        import os
        
        try:
            from llama_index.llms.cohere import Cohere
        except Exception as exc:
            raise ImportError(
                "Missing Cohere adapter. Install 'llama-index-llms-cohere' package."
            ) from exc
        
        # Normalize known Cohere chat model names and avoid deprecated Generate API
        # Accept model aliases like command-r-plus, command-r, and the new command-a-reasoning-08-2025 (frontier models)
        default_model = os.getenv("COHERE_MODEL") or "command-a-reasoning-08-2025"  # Frontier model default
        model = (model or default_model).strip()
        api_key = api_key or os.getenv("COHERE_API_KEY")
        
        if not api_key:
            raise ValueError("COHERE_API_KEY required for Cohere provider")
        
        # Force use of the Chat API instead of the deprecated Generate API
        # This is a critical fix for the September 2025 Cohere API change
        try:
            # Try to import the Cohere client directly to check if it supports chat
            import importlib.util
            if importlib.util.find_spec("cohere"):
                import cohere
                # Use ClientV2 for Command-A models (requires v2 API)
                is_command_a = model.startswith("command-a")
                if is_command_a and hasattr(cohere, "ClientV2"):
                    client = cohere.ClientV2(api_key=api_key)
                else:
                    client = cohere.Client(api_key=api_key)
                
                # Test if the chat method exists and use it directly
                if hasattr(client, "chat") and callable(client.chat):
                    logger.info(f"Using Cohere Chat API directly with model: {model}")
                    
                    # Create a wrapper function that uses the chat API
                    def cohere_chat_complete(prompt, **kwargs):
                        from llama_index.core.llms import ChatResponse, ChatMessage

                        # Detect Command-A models for proper parameter defaults
                        is_command_a_model = model.startswith("command-a")
                        is_command_r_plus = "command-r-plus" in model.lower() or "plus" in model.lower()

                        # Extract reasoning parameters for Command-A-Reasoning models
                        reasoning_enabled = kwargs.pop("reasoning", None)
                        token_budget = kwargs.pop("token_budget", None)

                        # v2 API uses different parameter structure
                        if is_command_a_model and isinstance(client, cohere.ClientV2):
                            # v2 API format
                            chat_params = {
                                "model": model,
                                "messages": [{"role": "user", "content": prompt}],
                                "temperature": kwargs.get("temperature", 1.0),
                                "max_tokens": kwargs.get("max_tokens", 8192),
                            }
                            # Add reasoning parameters for Command-A-Reasoning models
                            if "reasoning" in model.lower():
                                if reasoning_enabled is not None:
                                    chat_params["reasoning"] = reasoning_enabled
                                if token_budget:
                                    chat_params["token_budget"] = token_budget

                            response = client.chat(**chat_params)
                            # Command-A-Reasoning returns multiple content items (thinking + text)
                            # Find the text content item
                            text_content = None
                            for content_item in response.message.content:
                                if hasattr(content_item, 'type') and content_item.type == 'text':
                                    text_content = content_item.text
                                    break
                                elif hasattr(content_item, 'text'):
                                    # Fallback if no type attribute
                                    text_content = content_item.text
                                    break

                            if text_content is None:
                                # If no text found, use the string representation
                                text_content = str(response.message.content)

                            return ChatResponse(message=ChatMessage(role="assistant", content=text_content))
                        else:
                            # v1 API format
                            chat_params = {
                                "message": prompt,
                                "model": model,
                                "temperature": kwargs.get("temperature", 1.0),  # Fixed: match GPT-5
                                "max_tokens": kwargs.get("max_tokens",
                                    8192 if is_command_a_model else  # Command-A can handle 8K+
                                    4000 if is_command_r_plus else
                                    2000
                                ),
                            }

                            # Add reasoning parameters for Command-A-Reasoning models
                            if "reasoning" in model.lower():
                                if reasoning_enabled is not None:
                                    chat_params["reasoning"] = reasoning_enabled
                                if token_budget:
                                    chat_params["token_budget"] = token_budget

                            response = client.chat(**chat_params)
                            return ChatResponse(message=ChatMessage(role="assistant", content=response.text))
                    
                    # Create a simple LLM class that uses our wrapper
                    from llama_index.core.llms import LLM, CompletionResponse
                    from llama_index.core.base.llms.types import LLMMetadata

                    class CohereDirectChat(LLM):
                        @property
                        def metadata(self) -> LLMMetadata:
                            return LLMMetadata(
                                model_name=model,
                                context_window=256000,  # Command-A context
                                num_output=8192,
                                is_chat_model=True,
                            )

                        def complete(self, prompt, **kwargs):
                            response = cohere_chat_complete(prompt, **kwargs)
                            # Return CompletionResponse instead of ChatResponse for complete()
                            return CompletionResponse(text=response.message.content)

                        def chat(self, messages, **kwargs):
                            # Extract the last user message if it's a list of messages
                            if isinstance(messages, list) and messages:
                                last_msg = messages[-1]
                                if hasattr(last_msg, "content"):
                                    prompt = last_msg.content
                                else:
                                    prompt = str(last_msg)
                            else:
                                prompt = str(messages)
                            return cohere_chat_complete(prompt, **kwargs)

                        def stream_complete(self, prompt, **kwargs):
                            # Streaming not implemented - return regular response
                            return self.complete(prompt, **kwargs)

                        def stream_chat(self, messages, **kwargs):
                            # Streaming not implemented - return regular response
                            return self.chat(messages, **kwargs)

                        async def acomplete(self, prompt, **kwargs):
                            # Async not implemented - call sync version
                            return self.complete(prompt, **kwargs)

                        async def achat(self, messages, **kwargs):
                            # Async not implemented - call sync version
                            return self.chat(messages, **kwargs)

                        async def astream_complete(self, prompt, **kwargs):
                            # Async streaming not implemented - call sync version
                            return self.complete(prompt, **kwargs)

                        async def astream_chat(self, messages, **kwargs):
                            # Async streaming not implemented - call sync version
                            return self.chat(messages, **kwargs)
                    
                    llm = CohereDirectChat()
                    Settings.llm = llm  # Set global LLM before early return
                    logger.info(f"Configured Cohere LLM with direct Chat API: {model}")
                    return
        except Exception as direct_exc:
            logger.debug(f"Could not use Cohere Chat API directly: {direct_exc}")
        
        # If direct chat API approach failed, try the LlamaIndex adapter
        # The adapter should use the Chat API under the hood in newer versions

        # Detect Command-A models for proper parameter defaults
        is_command_a = model.startswith("command-a")
        is_command_r_plus = "command-r-plus" in model.lower() or "plus" in model.lower()

        cohere_kwargs = {"model": model, "api_key": api_key}
        # Sensible defaults; allow overrides
        cohere_kwargs.update({
            "max_tokens": kwargs.get("max_tokens",
                8192 if is_command_a else  # Command-A can handle 8K+
                4000 if is_command_r_plus else
                2000
            ),
            "temperature": kwargs.get("temperature", 1.0),  # Fixed: match GPT-5
        })
        for k, v in kwargs.items():
            if k not in ["model", "api_key"]:
                cohere_kwargs[k] = v
        
        # Try to use the chat_model parameter if available (newer adapter versions)
        try:
            llm = Cohere(chat_model=model, api_key=api_key, **{k: v for k, v in cohere_kwargs.items() if k not in ["model"]})
            logger.info(f"Configured Cohere LLM with chat_model parameter: {model}")
        except Exception as chat_exc:
            # Fall back to standard initialization and hope the adapter handles it
            llm = Cohere(**cohere_kwargs)
            logger.info(f"Configured Cohere LLM (standard): {model}")

        # Register Cohere model context windows for proper validation
        try:
            from llama_index.llms.openai import utils as openai_utils
            if hasattr(openai_utils, "ALL_AVAILABLE_MODELS"):
                cohere_models = {
                    # Command-A family (2025) - 256K context
                    "command-a-reasoning-08-2025": 256000,
                    "command-a-reasoning": 256000,
                    "command-a-03-2025": 256000,
                    "command-a": 256000,
                    # Command R family (2024) - 128K context
                    "command-r-plus-08-2024": 128000,
                    "command-r-plus": 128000,
                    "command-r-08-2024": 128000,
                    "command-r": 128000,
                }
                if isinstance(openai_utils.ALL_AVAILABLE_MODELS, dict):
                    openai_utils.ALL_AVAILABLE_MODELS.update(cohere_models)
                if hasattr(openai_utils, "CHAT_MODELS") and isinstance(openai_utils.CHAT_MODELS, dict):
                    openai_utils.CHAT_MODELS.update(cohere_models)
                logger.debug("Registered Cohere model context windows")
        except Exception as e:
            logger.debug(f"Could not register Cohere context windows: {e}")

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

    # Set the global LLM
    Settings.llm = llm


def configure_embedding_provider(
    provider: str = "openai", model: Optional[str] = None, api_key: Optional[str] = None, **kwargs
) -> None:
    """
    Configure the embedding provider for LlamaIndex.

    Args:
        provider: One of "openai", "cohere", "huggingface"
        model: Specific model to use
        api_key: API key for the provider (if needed)
        **kwargs: Additional provider-specific parameters
    """

    provider = provider.lower()

    if provider == "openai":
        from llama_index.embeddings.openai import OpenAIEmbedding

        model = model or "text-embedding-3-small"
        embed_model = OpenAIEmbedding(model=model, api_key=api_key, **kwargs)
        logger.info(f"Configured OpenAI embeddings: {model}")

    elif provider == "cohere":
        from llama_index.embeddings.cohere import CohereEmbedding

        # Default (preserve current behavior); can be overridden via COHERE_EMBED_MODEL
        model = model or os.getenv("COHERE_EMBED_MODEL", "embed-v4.0")
        api_key = api_key or os.getenv("COHERE_API_KEY")

        if not api_key:
            logger.warning("COHERE_API_KEY not found, falling back to OpenAI embeddings")
            # Fall back to OpenAI if no Cohere key
            configure_embedding_provider("openai")
            return

        # Normalize common aliases/mistypes for Cohere v4 embeddings
        original_model = str(model)
        m_lower = original_model.strip().lower()
        alias_map = {
            # Map all known v4 aliases (including light/mini) to canonical embed-v4.0
            "embed-english-v4.0": "embed-v4.0",
            "embed-english-v4": "embed-v4.0",
            "embed-v4": "embed-v4.0",
            "embed-english-light-v4.0": "embed-v4.0",
            "embed-light-v4.0": "embed-v4.0",
            "embed-english-mini-v4.0": "embed-v4.0",
        }
        if m_lower in alias_map:
            model = alias_map[m_lower]
            logger.warning(f"Normalized Cohere embedding model '{original_model}' -> '{model}'")

        # Warn when mixing embeddings across indexes
        if os.getenv("EMBEDDING_PROVIDER") == "cohere" and os.getenv("WARN_EMBED_MIGRATION") != "false":
            logger.warning(
                "Using Cohere embeddings. If indexes were built with different embeddings, "
                "they may need rebuilding. Set WARN_EMBED_MIGRATION=false to suppress."
            )

        # Prefer 'model' kwarg on newer adapters; fall back to 'model_name' for older versions
        try:
            embed_model = CohereEmbedding(
                model=model,
                api_key=api_key,
                input_type="search_document",  # Optimize for search
                **kwargs
            )
        except TypeError:
            embed_model = CohereEmbedding(
                model_name=model,
                api_key=api_key,
                input_type="search_document",
                **kwargs
            )
        logger.info(f"Configured Cohere embeddings: {model}")

    elif provider == "huggingface":
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding

        model = model or "BAAI/bge-small-en-v1.5"
        embed_model = HuggingFaceEmbedding(model_name=model, **kwargs)
        logger.info(f"Configured HuggingFace embeddings: {model}")

    else:
        raise ValueError(f"Unknown embedding provider: {provider}")

    # Set the global embedding model
    Settings.embed_model = embed_model


# Model recommendations for different use cases (updated with frontier models)
MODEL_RECOMMENDATIONS = {
    "fast": {
        "openai": "gpt-5-mini",  # Frontier model
        "anthropic": "claude-sonnet-4-20250514",  # Frontier model with 1M context
        "gemini": "gemini-2.5-pro-preview",  # Frontier model
        "grok": "grok-4-fast-reasoning",  # Frontier model - fast variant with reasoning
        "xai": "grok-4-fast-reasoning",  # Alternative provider name for grok
        "cohere": "command-a-reasoning-08-2025",  # Frontier model
    },
    "quality": {
        "openai": "gpt-5",  # Frontier model
        "anthropic": "claude-opus-4-1-20250805",  # Frontier model - most capable
        "gemini": "gemini-2.5-pro-preview",  # Frontier model
        "grok": "grok-4-fast-reasoning",  # Frontier model - full quality version
        "xai": "grok-4-fast-reasoning",  # Alternative provider name for grok
        "cohere": "command-a-reasoning-08-2025",  # Frontier model
    },
    "balanced": {
        "openai": "gpt-4.1",  # Frontier model with 1M context, excellent for coding
        "anthropic": "claude-sonnet-4-20250514",  # Frontier model balanced performance
        "gemini": "gemini-2.5-pro-preview",  # Frontier model
        "grok": "grok-4-fast-reasoning",  # Frontier model
        "xai": "grok-4-fast-reasoning",  # Alternative provider name for grok
        "cohere": "command-a-reasoning-08-2025",  # Frontier model
    },
}


def get_recommended_model(provider: str, use_case: str = "balanced") -> str:
    """Get recommended model for a provider and use case."""
    provider = provider.lower()
    use_case = use_case.lower()

    if use_case not in MODEL_RECOMMENDATIONS:
        use_case = "balanced"

    if provider not in MODEL_RECOMMENDATIONS[use_case]:
        raise ValueError(f"Unknown provider: {provider}")

    return MODEL_RECOMMENDATIONS[use_case][provider]
