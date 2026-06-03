from __future__ import annotations

from dataclasses import dataclass, field

from game_subtitle_translator.cache import TranslationCache
from game_subtitle_translator.config import AppConfig
from game_subtitle_translator.ocr import OcrEngine
from game_subtitle_translator.pipeline import TextStabilizer
from game_subtitle_translator.preprocess import preprocess_frame
from game_subtitle_translator.translate import Translator


@dataclass
class SubtitlePipeline:
    config: AppConfig
    ocr: OcrEngine
    translator: Translator
    cache: TranslationCache = field(default_factory=TranslationCache)
    stabilizer: TextStabilizer = field(default_factory=TextStabilizer)

    def process_frame(self, image) -> str | None:
        preprocessed = preprocess_frame(image, self.config.preprocess)
        raw_text = self.ocr.recognize(preprocessed)
        stable_text = self.stabilizer.update(raw_text)
        if not stable_text:
            return None

        source = self.config.translation.source_lang
        target = self.config.translation.target_lang
        cached = self.cache.get(stable_text, source, target)
        if cached is not None:
            return cached

        translated = self.translator.translate(stable_text, source, target)
        self.cache.set(stable_text, source, target, translated)
        return translated
