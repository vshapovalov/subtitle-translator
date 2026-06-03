from __future__ import annotations

from dataclasses import dataclass

from difflib import SequenceMatcher

_NOISE_TOKENS = {
    "[music]",
    "(music)",
    "[applause]",
    "(applause)",
    "[laughter]",
    "(laughter)",
}


def normalize_subtitle_text(text: str | None) -> str:
    if not text:
        return ""
    normalized = " ".join(str(text).replace("\n", " ").split()).strip()
    normalized = normalized.strip(" ")
    while normalized.startswith(">"):
        normalized = normalized[1:].strip()
    if normalized.lower() in _NOISE_TOKENS:
        return ""
    if normalized.startswith("♪") and normalized.endswith("♪"):
        return ""
    return normalized


@dataclass
class TextStabilizer:
    min_repeats: int = 2
    similarity_threshold: int = 92

    def __post_init__(self) -> None:
        self._candidate: str = ""
        self._candidate_repeats: int = 0
        self._last_emitted: str = ""

    def update(self, raw_text: str | None) -> str | None:
        text = normalize_subtitle_text(raw_text)
        if not text:
            self._candidate = ""
            self._candidate_repeats = 0
            return None

        if not self._candidate:
            self._candidate = text
            self._candidate_repeats = 1
            return None

        if self._similar(text, self._candidate):
            self._candidate_repeats += 1
        else:
            self._candidate = text
            self._candidate_repeats = 1
            return None

        if self._candidate_repeats >= self.min_repeats:
            emitted = self._candidate
            if emitted == self._last_emitted:
                self._candidate = ""
                self._candidate_repeats = 0
                return None
            self._last_emitted = emitted
            self._candidate = ""
            self._candidate_repeats = 0
            return emitted

        return None

    def _similar(self, left: str, right: str) -> bool:
        score = SequenceMatcher(a=left, b=right).ratio() * 100
        return score >= self.similarity_threshold
