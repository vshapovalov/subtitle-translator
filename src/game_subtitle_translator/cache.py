from __future__ import annotations

from dataclasses import dataclass, field

from game_subtitle_translator.pipeline import normalize_subtitle_text


@dataclass
class TranslationCache:
    _items: dict[tuple[str, str, str, str], str] = field(default_factory=dict)

    def get(self, text: str, source_lang: str, target_lang: str, backend: str) -> str | None:
        return self._items.get(self._key(text, source_lang, target_lang, backend))

    def set(self, text: str, source_lang: str, target_lang: str, backend: str, translated: str) -> None:
        self._items[self._key(text, source_lang, target_lang, backend)] = translated

    def _key(self, text: str, source_lang: str, target_lang: str, backend: str) -> tuple[str, str, str, str]:
        return (
            normalize_subtitle_text(text).casefold(),
            source_lang.lower(),
            target_lang.lower(),
            backend.lower().strip(),
        )
