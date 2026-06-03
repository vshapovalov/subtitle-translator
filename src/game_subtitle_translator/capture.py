from __future__ import annotations

from PIL import Image

from game_subtitle_translator.config import CaptureConfig, CaptureRegion


class ScreenCapture:
    def __init__(self, capture: CaptureConfig | CaptureRegion) -> None:
        if isinstance(capture, CaptureConfig):
            self.config: CaptureConfig | None = capture
            self.region = capture.region
        else:
            self.config = None
            self.region = capture

    def grab_frame(self) -> Image.Image:
        import mss

        with mss.mss() as sct:
            raw = sct.grab(self._grab_region(sct.monitors))
            return Image.frombytes("RGB", raw.size, raw.rgb)

    def _grab_region(self, monitors: list[dict[str, int]]) -> dict[str, int]:
        region = self.region.as_mss_dict()
        if self.config is None:
            return region

        monitor = self.config.monitor
        if monitor >= len(monitors):
            available = max(len(monitors) - 1, 0)
            raise ValueError(
                f"capture.monitor {monitor} is out of range; "
                f"available monitors: 1-{available}"
            )

        selected = monitors[monitor]
        return {
            **region,
            "left": selected["left"] + region["left"],
            "top": selected["top"] + region["top"],
        }
