from pathlib import Path

from game_subtitle_translator.config import AppConfig, TranslationConfig
from game_subtitle_translator.main import build_runtime, main
from game_subtitle_translator.translate import ArgosTranslator


def test_build_runtime_uses_configured_translation_backend() -> None:
    config = AppConfig(translation=TranslationConfig(backend="argos"))

    runtime = build_runtime(config)

    assert isinstance(runtime.translator, ArgosTranslator)


def test_main_bootstrap_reports_configured_translation_backend(
    tmp_path: Path,
    capsys,
) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
translation:
  backend: argos
""".strip(),
        encoding="utf-8",
    )

    exit_code = main(["--config", str(config_path)])

    assert exit_code == 0
    assert "Translation backend: argos" in capsys.readouterr().out
