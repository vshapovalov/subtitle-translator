from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


class ImageLike(Protocol):
    pass


class OcrEngine(ABC):
    @abstractmethod
    def recognize(self, image: ImageLike) -> str:
        raise NotImplementedError


class MockOcrEngine(OcrEngine):
    def __init__(self, text: str = "") -> None:
        self.text = text

    def recognize(self, image: ImageLike) -> str:
        return self.text


def create_ocr_engine(engine: str, source_lang: str) -> OcrEngine:
    normalized = engine.lower().strip()
    if normalized == "mock":
        return MockOcrEngine()
    raise ValueError(
        f"Unsupported OCR engine: {engine}. Install optional OCR extras and add an adapter."
    )
