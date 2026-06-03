from __future__ import annotations

from pathlib import Path

from PIL import Image

from game_subtitle_translator.test_scene import (
    TEST_SCENE_CUES,
    DeterministicSceneOcrEngine,
    render_test_scene_frames,
    run_test_scene_pipeline,
    save_test_scene_frames,
)
from game_subtitle_translator.translate import MockTranslator


class CountingMockTranslator(MockTranslator):
    def __init__(self) -> None:
        self.calls: list[str] = []

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        self.calls.append(text)
        return super().translate(text, source_lang, target_lang)


def test_deterministic_scene_ocr_reads_rendered_frame_subtitle_metadata() -> None:
    frames = render_test_scene_frames(frames_per_cue=2)
    ocr = DeterministicSceneOcrEngine()

    assert ocr.recognize(frames[0].image) == TEST_SCENE_CUES[0].subtitle
    assert ocr.recognize(frames[-1].image) == TEST_SCENE_CUES[-1].subtitle


def test_test_scene_pipeline_stabilizes_and_translates_rendered_frames() -> None:
    translator = CountingMockTranslator()
    frames = render_test_scene_frames(frames_per_cue=2)

    outputs = run_test_scene_pipeline(
        frames,
        translator=translator,
        source_lang="en",
        target_lang="uk",
    )

    assert [output.source_text for output in outputs] == [
        "Hold the gate!",
        "We need more light.",
        "Hold the gate!",
    ]
    assert [output.translated_text for output in outputs] == [
        "[uk] Hold the gate!",
        "[uk] We need more light.",
        "[uk] Hold the gate!",
    ]
    assert translator.calls == ["Hold the gate!", "We need more light."]
    assert outputs[2].from_cache is True


def test_test_scene_frames_round_trip_as_pngs_for_cli_and_automation(tmp_path: Path) -> None:
    frames = render_test_scene_frames(frames_per_cue=1)
    ocr = DeterministicSceneOcrEngine()

    saved_paths = save_test_scene_frames(frames, tmp_path)

    assert len(saved_paths) == len(frames)
    assert saved_paths[0].name == "frame-000.png"
    assert saved_paths[0].read_bytes().startswith(b"\x89PNG")

    with Image.open(saved_paths[0]) as reopened:
        assert ocr.recognize(reopened) == TEST_SCENE_CUES[0].subtitle
