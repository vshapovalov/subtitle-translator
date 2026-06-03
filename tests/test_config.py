from pathlib import Path

import pytest
from pydantic import ValidationError

from game_subtitle_translator.config import AppConfig, CaptureRegion, load_config


def test_default_config_has_positive_capture_and_overlay_regions():
    cfg = AppConfig()

    assert cfg.capture.region.width > 0
    assert cfg.capture.region.height > 0
    assert cfg.capture.fps > 0
    assert cfg.translation.source_lang == "en"
    assert cfg.translation.target_lang == "uk"


def test_capture_region_rejects_non_positive_dimensions():
    with pytest.raises(ValidationError):
        CaptureRegion(left=0, top=0, width=0, height=100)

    with pytest.raises(ValidationError):
        CaptureRegion(left=0, top=0, width=100, height=-1)


def test_load_config_creates_default_file_when_missing(tmp_path: Path):
    config_path = tmp_path / "config.yaml"

    cfg = load_config(config_path)

    assert cfg.translation.target_lang == "uk"
    assert config_path.exists()
    text = config_path.read_text(encoding="utf-8")
    assert "translation:" in text
    assert "target_lang: uk" in text


def test_load_config_reads_yaml_overrides(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
capture:
  fps: 5
  region:
    left: 10
    top: 20
    width: 300
    height: 80
translation:
  backend: mock
  source_lang: en
  target_lang: uk
overlay:
  font_size: 28
""".strip(),
        encoding="utf-8",
    )

    cfg = load_config(config_path)

    assert cfg.capture.fps == 5
    assert cfg.capture.region.left == 10
    assert cfg.capture.region.width == 300
    assert cfg.overlay.font_size == 28


def test_load_config_rejects_unknown_top_level_key(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
capture:
  fps: 5
unexpected: true
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError) as exc_info:
        load_config(config_path)

    assert "unexpected" in str(exc_info.value)


def test_load_config_rejects_unknown_nested_key(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
capture:
  fps: 5
  typo: true
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError) as exc_info:
        load_config(config_path)

    assert "typo" in str(exc_info.value)
