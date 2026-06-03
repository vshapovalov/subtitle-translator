from __future__ import annotations

from game_subtitle_translator.config import OverlayConfig


class TextOverlay:
    """Always-on-top translated text overlay for the selected region.

    Click-through is intentionally not enabled for this MVP.
    """

    def __init__(self, config: OverlayConfig) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

        self._Qt = Qt
        self._QColor = QColor
        self._widget = QWidget()
        self._widget.setWindowTitle("Subtitle translation")
        self._widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self._widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._label = QLabel("")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setWordWrap(True)
        layout = QVBoxLayout(self._widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.addWidget(self._label)
        self.update_config(config)

    def update_config(self, config: OverlayConfig) -> None:
        self._config = config
        self._widget.setGeometry(config.x, config.y, config.width, config.height)
        bg_alpha = int(config.background_opacity * 255)
        self._label.setStyleSheet(
            "QLabel {"
            f" color: {config.text_color};"
            f" font-size: {config.font_size}px;"
            f" background-color: rgba(0, 0, 0, {bg_alpha});"
            f" border: 1px solid {config.outline_color};"
            " padding: 8px;"
            "}"
        )

    def show_text(self, text: str) -> None:
        self._label.setText(text)
        if text:
            self._widget.show()
            self._widget.raise_()
        else:
            self.clear()

    def clear(self) -> None:
        self._label.setText("")
        self._widget.hide()

    def close(self) -> None:
        self._widget.close()
