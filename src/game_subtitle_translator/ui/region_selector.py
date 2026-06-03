from __future__ import annotations

from typing import Callable

from game_subtitle_translator.config import CaptureRegion


RegionCallback = Callable[[CaptureRegion], None]


class RegionSelector:
    """Transparent drag selector used to choose a capture region on Windows."""

    def __init__(self, on_selected: RegionCallback) -> None:
        from PySide6.QtCore import QPoint, QRect, Qt
        from PySide6.QtGui import QColor, QPainter, QPen
        from PySide6.QtWidgets import QWidget

        class _Selector(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self._origin: QPoint | None = None
                self._current_rect = QRect()
                self.setWindowTitle("Select translation region")
                self.setWindowFlags(
                    Qt.WindowType.FramelessWindowHint
                    | Qt.WindowType.WindowStaysOnTopHint
                    | Qt.WindowType.Tool
                )
                self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                screen = self.screen().geometry()
                self.setGeometry(screen)
                self.setCursor(Qt.CursorShape.CrossCursor)

            def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
                if event.button() == Qt.MouseButton.LeftButton:
                    self._origin = event.globalPosition().toPoint()
                    self._current_rect = QRect(self._origin, self._origin)
                    self.update()

            def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt override
                if self._origin is not None:
                    self._current_rect = QRect(
                        self._origin, event.globalPosition().toPoint()
                    ).normalized()
                    self.update()

            def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt override
                if event.button() == Qt.MouseButton.LeftButton and self._origin is not None:
                    rect = QRect(self._origin, event.globalPosition().toPoint()).normalized()
                    self._origin = None
                    self.hide()
                    if rect.width() > 0 and rect.height() > 0:
                        screen = self.geometry()
                        on_selected(
                            CaptureRegion(
                                left=rect.left() - screen.left(),
                                top=rect.top() - screen.top(),
                                width=rect.width(),
                                height=rect.height(),
                            )
                        )
                    self.close()

            def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
                if event.key() == Qt.Key.Key_Escape:
                    self.hide()
                    self.close()

            def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
                painter = QPainter(self)
                painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
                if not self._current_rect.isNull():
                    local = QRect(
                        self.mapFromGlobal(self._current_rect.topLeft()),
                        self.mapFromGlobal(self._current_rect.bottomRight()),
                    ).normalized()
                    painter.fillRect(local, QColor(80, 160, 255, 60))
                    painter.setPen(QPen(QColor(80, 160, 255), 2))
                    painter.drawRect(local)

        self._widget = _Selector()

    def show(self) -> None:
        self._widget.showFullScreen()
        self._widget.raise_()
        self._widget.activateWindow()
