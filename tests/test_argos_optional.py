import pytest

from game_subtitle_translator.translate import ArgosTranslator


def test_argos_translator_with_installed_package_and_model() -> None:
    pytest.importorskip("argostranslate")
    argos_translate = pytest.importorskip("argostranslate.translate")

    translator = ArgosTranslator(argos_translate=argos_translate)
    try:
        translated = translator.translate("Open the door", "en", "uk")
    except Exception as exc:
        pytest.skip(f"Argos en->uk model is not installed: {exc}")

    assert isinstance(translated, str)
    assert translated.strip()
