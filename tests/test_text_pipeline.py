import pytest

from game_subtitle_translator.cache import TranslationCache
from game_subtitle_translator.pipeline import TextStabilizer, normalize_subtitle_text
from game_subtitle_translator.translate import ArgosTranslator, MockTranslator, create_translator


def test_normalize_subtitle_text_collapses_whitespace_and_strips_prompt_garbage():
    assert normalize_subtitle_text("  >> Hello,   world!\n") == "Hello, world!"
    assert normalize_subtitle_text("[Music]") == ""
    assert normalize_subtitle_text("♪ dramatic music ♪") == ""


def test_text_stabilizer_emits_once_after_required_repeats():
    stabilizer = TextStabilizer(min_repeats=2, similarity_threshold=92)

    assert stabilizer.update("Hello world") is None
    assert stabilizer.update("Hello world") == "Hello world"
    assert stabilizer.update("Hello world") is None


def test_text_stabilizer_treats_small_ocr_variation_as_same_subtitle():
    stabilizer = TextStabilizer(min_repeats=2, similarity_threshold=85)

    assert stabilizer.update("I cannot open this door") is None
    assert stabilizer.update("I can not open this door") == "I cannot open this door"
    assert stabilizer.update("I cannot open this door") is None


def test_text_stabilizer_emits_new_subtitle_after_previous_one():
    stabilizer = TextStabilizer(min_repeats=2, similarity_threshold=92)

    assert stabilizer.update("Hello") is None
    assert stabilizer.update("Hello") == "Hello"
    assert stabilizer.update("Goodbye") is None
    assert stabilizer.update("Goodbye") == "Goodbye"


def test_text_stabilizer_emits_distinct_similar_subtitle_after_repeats():
    stabilizer = TextStabilizer(min_repeats=2, similarity_threshold=92)

    assert stabilizer.update("Open the door") is None
    assert stabilizer.update("Open the door") == "Open the door"
    assert stabilizer.update("Open the doors") is None
    assert stabilizer.update("Open the doors") == "Open the doors"


def test_text_stabilizer_requires_repeats_without_blank_frames_between_them():
    stabilizer = TextStabilizer(min_repeats=2, similarity_threshold=92)

    assert stabilizer.update("Hello") is None
    assert stabilizer.update("") is None
    assert stabilizer.update("Hello") is None
    assert stabilizer.update("Hello") == "Hello"


def test_translation_cache_keys_by_languages_and_normalized_text():
    cache = TranslationCache()

    cache.set(" Hello   world ", "en", "uk", "Привіт, світе")

    assert cache.get("Hello world", "en", "uk") == "Привіт, світе"
    assert cache.get("Hello world", "en", "de") is None


def test_mock_translator_makes_pipeline_visible_without_network():
    translator = MockTranslator()

    assert translator.translate("Open the door", "en", "uk") == "[uk] Open the door"


def test_create_translator_supports_argos_backend_without_loading_optional_dependency():
    translator = create_translator(" Argos ")

    assert isinstance(translator, ArgosTranslator)


def test_argos_translator_delegates_to_argostranslate_module():
    class FakeArgosTranslate:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str, str]] = []

        def translate(self, text: str, source_lang: str, target_lang: str) -> str:
            self.calls.append((text, source_lang, target_lang))
            return "Відчиніть двері"

    fake_argos_translate = FakeArgosTranslate()
    translator = ArgosTranslator(argos_translate=fake_argos_translate)

    assert translator.translate("Open the door", "en", "uk") == "Відчиніть двері"
    assert fake_argos_translate.calls == [("Open the door", "en", "uk")]


def test_argos_translator_reports_missing_optional_dependency(monkeypatch):
    def missing_import(name: str):
        assert name == "argostranslate.translate"
        raise ImportError("argostranslate is not installed")

    monkeypatch.setattr("game_subtitle_translator.translate.import_module", missing_import)

    translator = ArgosTranslator()

    with pytest.raises(RuntimeError, match=r"pip install .*argos"):
        translator.translate("Open the door", "en", "uk")
