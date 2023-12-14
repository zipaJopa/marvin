from .settings import settings

from .beta.assistants import Assistant

from .components import ai_fn, ai_model, ai_classifier

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

__all__ = [
    "ai_fn",
    "settings",
    "Assistant",
]
