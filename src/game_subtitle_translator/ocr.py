from __future__ import annotations

from abc import ABC, abstractmethod
from importlib import import_module
from typing import Any, Protocol


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


class EasyOcrEngine(OcrEngine):
    """Real OCR backend backed by the optional easyocr package."""

    def __init__(
        self,
        source_lang: str,
        *,
        easyocr_module: Any | None = None,
        reader: Any | None = None,
    ) -> None:
        self.source_lang = source_lang.lower().strip()
        self._easyocr = easyocr_module
        self._reader = reader

    def recognize(self, image: ImageLike) -> str:
        reader = self._load_reader()
        numpy = import_module("numpy")
        frame = numpy.array(image)
        result = reader.readtext(frame, detail=0, paragraph=True)
        if isinstance(result, str):
            return result.strip()
        return " ".join(str(item).strip() for item in result if str(item).strip())

    def _load_reader(self) -> Any:
        if self._reader is None:
            if self._easyocr is None:
                try:
                    self._easyocr = import_module("easyocr")
                except ImportError as exc:
                    raise RuntimeError(
                        "EasyOCR backend requires the optional ocr dependency. "
                        'Install it with: pip install -e ".[ocr]"'
                    ) from exc
            self._reader = self._easyocr.Reader([self.source_lang], gpu=False)
        return self._reader


def create_ocr_engine(engine: str, source_lang: str) -> OcrEngine:
    normalized = engine.lower().strip()
    if normalized == "mock":
        return MockOcrEngine()
    if normalized == "easyocr":
        return EasyOcrEngine(source_lang)
    raise ValueError(
        f"Unsupported OCR engine: {engine}. Supported engines: easyocr, mock."
    )
