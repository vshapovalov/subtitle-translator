from __future__ import annotations

from PIL import Image

from game_subtitle_translator.config import CaptureRegion


class ScreenCapture:
    def __init__(self, region: CaptureRegion) -> None:
        self.region = region

    def grab_frame(self) -> Image.Image:
        import mss

        with mss.mss() as sct:
            raw = sct.grab(self.region.as_mss_dict())
            return Image.frombytes("RGB", raw.size, raw.rgb)
