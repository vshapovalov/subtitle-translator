from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from game_subtitle_translator.capture import ScreenCapture
from game_subtitle_translator.config import CaptureConfig, CaptureRegion


class FakeShot:
    size = (2, 1)
    rgb = b"\x00\x00\x00\xff\xff\xff"


class FakeMss:
    monitors = [
        {"left": 0, "top": 0, "width": 3840, "height": 1080},
        {"left": 0, "top": 0, "width": 1920, "height": 1080},
        {"left": 1920, "top": 0, "width": 1920, "height": 1080},
    ]

    def __init__(self) -> None:
        self.grabbed_region: dict[str, int] | None = None

    def __enter__(self) -> "FakeMss":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def grab(self, region: dict[str, int]) -> FakeShot:
        self.grabbed_region = region
        return FakeShot()


def install_fake_mss(monkeypatch: pytest.MonkeyPatch) -> FakeMss:
    fake = FakeMss()
    monkeypatch.setitem(sys.modules, "mss", SimpleNamespace(mss=lambda: fake))
    return fake


def test_screen_capture_offsets_region_by_selected_monitor(monkeypatch: pytest.MonkeyPatch):
    fake = install_fake_mss(monkeypatch)
    capture = ScreenCapture(
        CaptureConfig(
            monitor=2,
            region=CaptureRegion(left=10, top=20, width=300, height=80),
        )
    )

    image = capture.grab_frame()

    assert image.size == (2, 1)
    assert fake.grabbed_region == {
        "left": 1930,
        "top": 20,
        "width": 300,
        "height": 80,
    }


def test_screen_capture_keeps_region_constructor_backward_compatible(
    monkeypatch: pytest.MonkeyPatch,
):
    fake = install_fake_mss(monkeypatch)
    capture = ScreenCapture(CaptureRegion(left=10, top=20, width=300, height=80))

    capture.grab_frame()

    assert fake.grabbed_region == {
        "left": 10,
        "top": 20,
        "width": 300,
        "height": 80,
    }


def test_screen_capture_rejects_unknown_monitor_at_grab_time(
    monkeypatch: pytest.MonkeyPatch,
):
    install_fake_mss(monkeypatch)
    capture = ScreenCapture(CaptureConfig(monitor=3))

    with pytest.raises(ValueError, match="capture.monitor 3 is out of range"):
        capture.grab_frame()
