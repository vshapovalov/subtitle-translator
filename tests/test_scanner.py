from __future__ import annotations

from game_subtitle_translator.scanner import RegionScanner


class FakeCapture:
    def __init__(self) -> None:
        self.calls = 0

    def grab_frame(self):
        self.calls += 1
        return object()


class FakePipeline:
    def __init__(self, result: str | None = "Переклад") -> None:
        self.result = result
        self.calls = 0

    def process_frame(self, image) -> str | None:
        self.calls += 1
        return self.result


def test_region_scanner_scans_only_when_running() -> None:
    capture = FakeCapture()
    pipeline = FakePipeline()
    scanner = RegionScanner(capture, pipeline)

    assert scanner.scan_once() is None
    assert capture.calls == 0

    scanner.start()

    assert scanner.scan_once() == "Переклад"
    assert capture.calls == 1
    assert pipeline.calls == 1


def test_region_scanner_calls_translation_callback() -> None:
    seen: list[str] = []
    scanner = RegionScanner(FakeCapture(), FakePipeline("Hello"), on_translation=seen.append)

    scanner.start()
    scanner.scan_once()

    assert seen == ["Hello"]


def test_region_scanner_stop_prevents_more_scans() -> None:
    capture = FakeCapture()
    scanner = RegionScanner(capture, FakePipeline())

    scanner.start()
    scanner.stop()

    assert scanner.scan_once() is None
    assert capture.calls == 0


def test_region_scanner_routes_errors_to_callback() -> None:
    class BrokenCapture:
        def grab_frame(self):
            raise ValueError("camera failed")

    errors: list[Exception] = []
    scanner = RegionScanner(BrokenCapture(), FakePipeline(), on_error=errors.append)
    scanner.start()

    assert scanner.scan_once() is None
    assert len(errors) == 1
    assert str(errors[0]) == "camera failed"
