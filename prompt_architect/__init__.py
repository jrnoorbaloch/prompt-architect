"""Prompt Architect — turn any basic prompt into a professional one, with any LLM."""
__version__ = "1.0.0"

from .engine import Result, engineer  # noqa: E402
from .providers import complete  # noqa: E402

__all__ = ["engineer", "Result", "complete", "__version__"]
