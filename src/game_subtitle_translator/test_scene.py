from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

from game_subtitle_translator.cache import TranslationCache
from game_subtitle_translator.ocr import ImageLike, OcrEngine
from game_subtitle_translator.pipeline import TextStabilizer
from game_subtitle_translator.translate import MockTranslator, Translator

SUBTITLE_METADATA_KEY = "game_subtitle_translator.subtitle"
FONT_ENV_VAR = "GAME_SUBTITLE_TRANSLATOR_FONT"
UNICODE_FONT_NAMES: tuple[str, ...] = (
    "DejaVuSans.ttf",
    "DejaVuSans-Bold.ttf",
    "NotoSans-Regular.ttf",
    "NotoSansCJK-Regular.ttc",
    "FreeSans.ttf",
    "Arial Unicode.ttf",
    "Arial Unicode MS.ttf",
)
FONT_SEARCH_DIRS: tuple[Path, ...] = (
    Path("/usr/share/fonts"),
    Path("/usr/local/share/fonts"),
    Path("/Library/Fonts"),
    Path("/System/Library/Fonts"),
    Path("C:/Windows/Fonts"),
    Path.home() / ".local/share/fonts",
    Path.home() / ".fonts",
)
LAST_RESORT_FONT_SEARCH_DIRS: tuple[Path, ...] = (
    Path("/var/lib"),
)
CYRILLIC_GLYPH_PROBE = "В"
REPLACEMENT_GLYPH_PROBE = "\N{REPLACEMENT CHARACTER}"


@dataclass(frozen=True)
class TestSceneCue:
    subtitle: str


@dataclass(frozen=True)
class TestSceneFrame:
    index: int
    cue_index: int
    subtitle: str
    image: Image.Image


@dataclass(frozen=True)
class TestScenePipelineOutput:
    frame_index: int
    source_text: str
    translated_text: str
    from_cache: bool


TEST_SCENE_CUES: tuple[TestSceneCue, ...] = (
    TestSceneCue("Hold the gate!"),
    TestSceneCue("We need more light."),
    TestSceneCue("Hold the gate!"),
)


class DeterministicSceneOcrEngine(OcrEngine):
    """Reads subtitles embedded by the deterministic test scene renderer."""

    def recognize(self, image: ImageLike) -> str:
        info = getattr(image, "info", {})
        return str(info.get(SUBTITLE_METADATA_KEY, ""))


def render_test_scene_frames(
    *,
    width: int = 640,
    height: int = 360,
    frames_per_cue: int = 2,
) -> list[TestSceneFrame]:
    if frames_per_cue <= 0:
        raise ValueError("frames_per_cue must be positive")

    frames: list[TestSceneFrame] = []
    for cue_index, cue in enumerate(TEST_SCENE_CUES):
        for repeat_index in range(frames_per_cue):
            frame_index = len(frames)
            image = _render_frame(
                subtitle=cue.subtitle,
                frame_index=frame_index,
                cue_index=cue_index,
                repeat_index=repeat_index,
                width=width,
                height=height,
            )
            frames.append(
                TestSceneFrame(
                    index=frame_index,
                    cue_index=cue_index,
                    subtitle=cue.subtitle,
                    image=image,
                )
            )
    return frames


def save_test_scene_frames(frames: list[TestSceneFrame], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for frame in frames:
        path = output_dir / f"frame-{frame.index:03d}.png"
        png_info = PngImagePlugin.PngInfo()
        png_info.add_text(SUBTITLE_METADATA_KEY, frame.subtitle)
        png_info.add_text("game_subtitle_translator.frame", str(frame.index))
        frame.image.save(path, pnginfo=png_info)
        paths.append(path)
    return paths


def run_test_scene_pipeline(
    frames: list[TestSceneFrame],
    *,
    ocr: OcrEngine | None = None,
    stabilizer: TextStabilizer | None = None,
    translator: Translator | None = None,
    cache: TranslationCache | None = None,
    source_lang: str = "en",
    target_lang: str = "uk",
) -> list[TestScenePipelineOutput]:
    ocr_engine = ocr or DeterministicSceneOcrEngine()
    text_stabilizer = stabilizer or TextStabilizer(min_repeats=2, similarity_threshold=92)
    text_translator = translator or MockTranslator()
    translation_cache = cache or TranslationCache()

    outputs: list[TestScenePipelineOutput] = []
    for frame in frames:
        raw_text = ocr_engine.recognize(frame.image)
        stable_text = text_stabilizer.update(raw_text)
        if stable_text is None:
            continue

        backend = text_translator.backend
        cached = translation_cache.get(stable_text, source_lang, target_lang, backend)
        if cached is None:
            translated = text_translator.translate(stable_text, source_lang, target_lang)
            translation_cache.set(stable_text, source_lang, target_lang, backend, translated)
            from_cache = False
        else:
            translated = cached
            from_cache = True

        outputs.append(
            TestScenePipelineOutput(
                frame_index=frame.index,
                source_text=stable_text,
                translated_text=translated,
                from_cache=from_cache,
            )
        )
    return outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a deterministic subtitle test scene and run the mock pipeline."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("build/test-scene"),
        help="Directory for rendered PNG frames.",
    )
    parser.add_argument("--frames-per-cue", type=int, default=2)
    parser.add_argument("--target-lang", default="uk")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    frames = render_test_scene_frames(frames_per_cue=args.frames_per_cue)
    paths = save_test_scene_frames(frames, args.output_dir)
    outputs = run_test_scene_pipeline(frames, target_lang=args.target_lang)

    print(f"Rendered {len(paths)} deterministic PNG frames to {args.output_dir}")
    for output in outputs:
        cache_note = " cache" if output.from_cache else ""
        print(
            f"frame {output.frame_index:03d}: "
            f"{output.source_text} -> {output.translated_text}{cache_note}"
        )
    return 0


def _render_frame(
    *,
    subtitle: str,
    frame_index: int,
    cue_index: int,
    repeat_index: int,
    width: int,
    height: int,
) -> Image.Image:
    image = Image.new("RGB", (width, height), (7, 10, 18))
    draw = ImageDraw.Draw(image)
    label_font = _load_overlay_font(14)
    subtitle_font = _load_overlay_font(28)

    horizon = height // 2
    draw.rectangle((0, horizon, width, height), fill=(10, 14, 24))
    draw.rectangle((48, 92, 180, 190), fill=(24, 34, 56), outline=(82, 108, 146), width=2)
    draw.rectangle((390, 78, 525, 188), fill=(28, 29, 42), outline=(115, 92, 64), width=2)
    draw.ellipse((282, 46, 326, 90), fill=(246, 201, 96))
    draw.line((0, horizon + cue_index * 8, width, horizon + cue_index * 8), fill=(32, 47, 69), width=2)

    marker_x = 78 + frame_index * 17
    draw.rectangle((marker_x, 222, marker_x + 28, 246), fill=(96, 156, 210))
    draw.text(
        (16, 14),
        f"deterministic test scene frame {frame_index}",
        fill=(148, 160, 178),
        font=label_font,
    )

    bar_top = height - 86
    draw.rectangle((0, bar_top, width, height), fill=(0, 0, 0))
    draw.rectangle((0, bar_top, width, bar_top + 2), fill=(74, 87, 108))
    draw.text((32, bar_top + 18), subtitle, fill=(255, 255, 255), font=subtitle_font)
    draw.text(
        (width - 116, bar_top + 58),
        f"cue {cue_index}.{repeat_index}",
        fill=(138, 148, 164),
        font=label_font,
    )

    image.info[SUBTITLE_METADATA_KEY] = subtitle
    image.info["game_subtitle_translator.frame"] = str(frame_index)
    return image


@lru_cache(maxsize=8)
def _load_overlay_font(size: int) -> ImageFont.ImageFont:
    for font_path in _discover_unicode_font_paths():
        try:
            font = ImageFont.truetype(str(font_path), size=size)
        except OSError:
            continue
        if _font_has_distinct_cyrillic_glyph(font):
            return font

    for font_name in UNICODE_FONT_NAMES:
        try:
            font = ImageFont.truetype(font_name, size=size)
        except OSError:
            continue
        if _font_has_distinct_cyrillic_glyph(font):
            return font

    return ImageFont.load_default(size=size)


def _discover_unicode_font_paths() -> list[Path]:
    paths: list[Path] = []
    configured = os.environ.get(FONT_ENV_VAR)
    if configured:
        paths.append(Path(configured).expanduser())

    for search_dir in FONT_SEARCH_DIRS:
        paths.extend(_matching_font_paths(search_dir))

    if not paths:
        for search_dir in LAST_RESORT_FONT_SEARCH_DIRS:
            paths.extend(_matching_font_paths(search_dir, limit=25))
            if paths:
                break

    return paths


def _matching_font_paths(search_dir: Path, *, limit: int | None = None) -> list[Path]:
    if not search_dir.exists():
        return []

    matches: list[Path] = []
    wanted = {name.lower() for name in UNICODE_FONT_NAMES}
    for path in search_dir.rglob("*"):
        if path.name.lower() in wanted:
            matches.append(path)
            if limit is not None and len(matches) >= limit:
                break
    return matches


def _font_has_distinct_cyrillic_glyph(font: ImageFont.ImageFont) -> bool:
    try:
        cyrillic = font.getmask(CYRILLIC_GLYPH_PROBE)
        replacement = font.getmask(REPLACEMENT_GLYPH_PROBE)
    except (AttributeError, OSError, UnicodeEncodeError):
        return False

    return cyrillic.size != replacement.size or bytes(cyrillic) != bytes(replacement)


if __name__ == "__main__":
    raise SystemExit(main())
