from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OverlayState:
    visible: bool = True
    text: str = ""


class ConsoleOverlay:
    """Headless-safe overlay used until the Qt renderer is enabled."""

    def __init__(self) -> None:
        self.state = OverlayState()

    def show_text(self, text: str) -> None:
        self.state.text = text
        if self.state.visible:
            print(text)

    def toggle(self) -> bool:
        self.state.visible = not self.state.visible
        return self.state.visible

    def clear(self) -> None:
        self.state.text = ""
