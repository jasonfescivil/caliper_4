from __future__ import annotations

import re
from typing import Optional

MIN_PROMPT_LENGTH = 10
CONTEXT_FILE_REGEX = re.compile(r"@[\w\.\/\-_]+")

class PromptValidationError(ValueError):
    """Custom exception for prompt validation errors."""
    pass

def validate_prompt(prompt: Optional[str]) -> None:
    """
    Validates a user-provided prompt.

    Raises:
        PromptValidationError: If the prompt is invalid.
    """
    if not prompt or not prompt.strip():
        raise PromptValidationError("Prompt cannot be empty.")

    prompt = prompt.strip()

    if len(prompt) < MIN_PROMPT_LENGTH and not CONTEXT_FILE_REGEX.search(prompt):
        raise PromptValidationError(
            f"Prompt is very short ({len(prompt)} chars) and does not appear to reference a context file "
            f"(e.g., '@file.md'). Please provide a more descriptive question or reference a file."
        )