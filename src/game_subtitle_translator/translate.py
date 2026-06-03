from __future__ import annotations

from abc import ABC, abstractmethod


class Translator(ABC):
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        raise NotImplementedError


class MockTranslator(Translator):
    """Network-free translator for TDD, demos and pipeline smoke tests."""

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        return f"[{target_lang}] {text}"


def create_translator(backend: str) -> Translator:
    normalized = backend.lower().strip()
    if normalized == "mock":
        return MockTranslator()
    raise ValueError(f"Unsupported translation backend: {backend}")
