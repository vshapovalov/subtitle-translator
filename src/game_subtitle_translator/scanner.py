from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from game_subtitle_translator.realtime import SubtitlePipeline


class FrameCapture(Protocol):
    def grab_frame(self):
        raise NotImplementedError


TranslationCallback = Callable[[str], None]
ErrorCallback = Callable[[Exception], None]


@dataclass
class RegionScanner:
    """Long-lived scan controller independent from any UI toolkit."""

    capture: FrameCapture
    pipeline: SubtitlePipeline
    on_translation: TranslationCallback | None = None
    on_error: ErrorCallback | None = None
    is_running: bool = False
    is_busy: bool = False

    def start(self) -> None:
        self.is_running = True

    def stop(self) -> None:
        self.is_running = False
        self.is_busy = False

    def scan_once(self) -> str | None:
        if not self.is_running or self.is_busy:
            return None

        self.is_busy = True
        try:
            frame = self.capture.grab_frame()
            translated = self.pipeline.process_frame(frame)
            if translated and self.on_translation is not None:
                self.on_translation(translated)
            return translated
        except Exception as exc:
            if self.on_error is not None:
                self.on_error(exc)
                return None
            raise
        finally:
            self.is_busy = False
