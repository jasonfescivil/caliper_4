# Python Standards

Formatting & style
- PEP 8 with black formatting awareness (target line length ~100; do not hard-wrap docstrings unnecessarily).
- Type hints mandatory for all public functions. Use typing and collections.abc.
- Google-style docstrings for non-trivial modules/classes/functions with Args/Returns/Raises.
- Imports: stdlib, third-party, local; no unused imports.

Error handling & logging
- Use explicit exceptions (FileNotFoundError, ValueError, etc.) and log with context.
- For CLI commands, surface user-facing hints via typer.secho; log stack traces with logger.exception.

I/O & paths
- Use pathlib.Path exclusively for filesystem paths.
- No hardcoded absolute paths. Use settings and environment variables.
- Respect Windows paths and case sensitivity; avoid POSIX-only assumptions.

Env & secrets
- Never hardcode API keys; rely on .env loader and settings.
- Read-only access to .env values; never print secret values.

Testing & reliability
- Design functions to be testable; avoid singletons where possible.
- Prefer pure functions for transformations and side-effect isolation for I/O.

Performance
- Avoid O(n^2) on large collections; stream or batch where feasible.
- Chunk sizes configurable via settings; no magic constants.

Concurrency
- Prefer simple synchronous code unless there is a clear benefit to async.
