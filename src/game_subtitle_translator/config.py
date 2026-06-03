from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt


class CaptureRegion(BaseModel):
    left: int = 300
    top: int = 760
    width: PositiveInt = 1320
    height: PositiveInt = 220

    def as_mss_dict(self) -> dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }


class CaptureConfig(BaseModel):
    monitor: PositiveInt = 1
    region: CaptureRegion = Field(default_factory=CaptureRegion)
    fps: PositiveFloat = 8.0


class OcrConfig(BaseModel):
    engine: str = "mock"
    source_lang: str = "en"


class PreprocessConfig(BaseModel):
    scale: PositiveFloat = 2.0
    grayscale: bool = True
    contrast: PositiveFloat = 1.4
    threshold: bool = False


class TranslationConfig(BaseModel):
    backend: str = "mock"
    source_lang: str = "en"
    target_lang: str = "uk"


class OverlayConfig(BaseModel):
    x: int = 300
    y: int = 760
    width: PositiveInt = 1320
    height: PositiveInt = 220
    font_size: PositiveInt = 32
    text_color: str = "#FFFFFF"
    outline_color: str = "#000000"
    background_opacity: float = Field(default=0.25, ge=0.0, le=1.0)


class AppConfig(BaseModel):
    capture: CaptureConfig = Field(default_factory=CaptureConfig)
    ocr: OcrConfig = Field(default_factory=OcrConfig)
    preprocess: PreprocessConfig = Field(default_factory=PreprocessConfig)
    translation: TranslationConfig = Field(default_factory=TranslationConfig)
    overlay: OverlayConfig = Field(default_factory=OverlayConfig)


def default_config_path() -> Path:
    return Path.home() / ".game-subtitle-translator" / "config.yaml"


def _to_yamlable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return _to_yamlable(value.model_dump())
    if isinstance(value, dict):
        return {k: _to_yamlable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_yamlable(v) for v in value]
    return value


def save_config(config: AppConfig, path: Path | None = None) -> None:
    target = path or default_config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        yaml.safe_dump(_to_yamlable(config), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def load_config(path: Path | None = None) -> AppConfig:
    target = path or default_config_path()
    if not target.exists():
        config = AppConfig()
        save_config(config, target)
        return config

    raw = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    config = AppConfig.model_validate(raw)
    return config
