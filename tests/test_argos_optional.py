import pytest

from game_subtitle_translator.translate import ArgosTranslator


def _skip_if_argos_model_missing(argos_translate) -> None:
    installed_languages = argos_translate.get_installed_languages()
    source = next((language for language in installed_languages if language.code == "en"), None)
    target = next((language for language in installed_languages if language.code == "uk"), None)
    if source is None or target is None or source.get_translation(target) is None:
        pytest.skip("Argos en->uk model is not installed")


def test_argos_translator_with_installed_package_and_model() -> None:
    pytest.importorskip("argostranslate")
    argos_translate = pytest.importorskip("argostranslate.translate")
    _skip_if_argos_model_missing(argos_translate)

    translator = ArgosTranslator(argos_translate=argos_translate)
    translated = translator.translate("Open the door", "en", "uk")

    assert isinstance(translated, str)
    assert translated.strip()
