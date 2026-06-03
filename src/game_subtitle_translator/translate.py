from __future__ import annotations

from abc import ABC, abstractmethod
from importlib import import_module
from typing import Any


class Translator(ABC):
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        raise NotImplementedError


class MockTranslator(Translator):
    """Network-free translator for TDD, demos and pipeline smoke tests."""

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        return f"[{target_lang}] {text}"


class ArgosTranslator(Translator):
    """Offline translator backed by the optional argostranslate package."""

    def __init__(self, argos_translate: Any | None = None) -> None:
        self._argos_translate = argos_translate

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        argos_translate = self._load_argos_translate()
        return str(argos_translate.translate(text, source_lang, target_lang))

    def _load_argos_translate(self) -> Any:
        if self._argos_translate is None:
            try:
                self._argos_translate = import_module("argostranslate.translate")
            except ImportError as exc:
                raise RuntimeError(
                    "Argos translation backend requires the optional argos dependency. "
                    'Install it with: pip install "game-subtitle-translator[argos]"'
                ) from exc
        return self._argos_translate


def create_translator(backend: str) -> Translator:
    normalized = backend.lower().strip()
    if normalized == "mock":
        return MockTranslator()
    if normalized == "argos":
        return ArgosTranslator()
    raise ValueError(f"Unsupported translation backend: {backend}")
