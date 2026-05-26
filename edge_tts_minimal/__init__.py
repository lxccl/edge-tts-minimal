"""Edge TTS Minimal — text-to-speech via Microsoft Edge's free TTS service."""

from .client import build_ssml, list_voices, synthesize

__all__ = ["synthesize", "list_voices", "build_ssml"]
__version__ = "0.1.0"
