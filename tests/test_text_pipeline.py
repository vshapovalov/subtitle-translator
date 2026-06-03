from game_subtitle_translator.cache import TranslationCache
from game_subtitle_translator.pipeline import TextStabilizer, normalize_subtitle_text
from game_subtitle_translator.translate import MockTranslator


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
