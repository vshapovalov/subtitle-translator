from __future__ import annotations

import pytest

from game_subtitle_translator.ocr import EasyOcrEngine, MockOcrEngine, create_ocr_engine


def test_create_ocr_engine_supports_easyocr_without_loading_optional_dependency() -> None:
    engine = create_ocr_engine(" EasyOCR ", "en")

    assert isinstance(engine, EasyOcrEngine)


def test_create_ocr_engine_keeps_mock_for_tests() -> None:
    engine = create_ocr_engine("mock", "en")

    assert isinstance(engine, MockOcrEngine)


def test_easyocr_engine_reports_missing_optional_dependency(monkeypatch) -> None:
    def missing_import(name: str):
        if name == "easyocr":
            raise ImportError("easyocr is not installed")
        return __import__(name)

    monkeypatch.setattr("game_subtitle_translator.ocr.import_module", missing_import)

    engine = EasyOcrEngine("en")

    with pytest.raises(RuntimeError, match=r"pip install .*ocr"):
        engine.recognize(object())


def test_easyocr_engine_joins_reader_text_results(monkeypatch) -> None:
    class FakeReader:
        def readtext(self, frame, detail: int, paragraph: bool):
            assert detail == 0
            assert paragraph is True
            return ["Open", "the door"]

    class FakeNumpy:
        @staticmethod
        def array(image):
            return image

    def fake_import(name: str):
        assert name == "numpy"
        return FakeNumpy

    monkeypatch.setattr("game_subtitle_translator.ocr.import_module", fake_import)

    engine = EasyOcrEngine("en", reader=FakeReader())

    assert engine.recognize(object()) == "Open the door"
