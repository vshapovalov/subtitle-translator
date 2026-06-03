from __future__ import annotations

from PIL import Image, ImageEnhance, ImageOps

from game_subtitle_translator.config import PreprocessConfig


def preprocess_frame(image: Image.Image, config: PreprocessConfig) -> Image.Image:
    result = image
    if config.scale != 1.0:
        width = max(1, int(result.width * config.scale))
        height = max(1, int(result.height * config.scale))
        result = result.resize((width, height))
    if config.grayscale:
        result = ImageOps.grayscale(result)
    if config.contrast != 1.0:
        result = ImageEnhance.Contrast(result).enhance(config.contrast)
    if config.threshold:
        gray = ImageOps.grayscale(result)
        result = gray.point(lambda pixel: 255 if pixel > 140 else 0)
    return result
