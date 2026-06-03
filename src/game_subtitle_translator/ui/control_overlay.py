from __future__ import annotations

from collections.abc import Callable


class ControlOverlay:
    """Movable utility overlay with region/start/stop/tray controls."""

    def __init__(
        self,
        *,
        on_select_region: Callable[[], None],
        on_start: Callable[[], None],
        on_stop: Callable[[], None],
        on_minimize_to_tray: Callable[[], None],
    ) -> None:
        from PySide6.QtCore import QPoint, Qt
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QLabel,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        class _Overlay(QWidget):
            def __init__(self, owner: ControlOverlay) -> None:
                super().__init__()
                self._owner = owner
                self._drag_origin: QPoint | None = None
                self.setWindowTitle("Subtitle Translator")
                self.setWindowFlags(
                    Qt.WindowType.FramelessWindowHint
                    | Qt.WindowType.WindowStaysOnTopHint
                    | Qt.WindowType.Tool
                )
                self.setStyleSheet(
                    "QWidget { background: #20242b; color: white; }"
                    "QPushButton { padding: 6px 10px; }"
                )

            def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_origin = (
                        event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    )

            def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt override
                if self._drag_origin is not None:
                    self.move(event.globalPosition().toPoint() - self._drag_origin)

            def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt override
                self._drag_origin = None

            def closeEvent(self, event) -> None:  # noqa: N802 - Qt override
                event.ignore()
                self.hide()
                self._owner.minimize_requested()

        self._widget = _Overlay(self)
        self._on_minimize_to_tray = on_minimize_to_tray

        self._status = QLabel("Ready")
        self._select_button = QPushButton("Выбрать регион")
        self._start_button = QPushButton("Старт")
        self._stop_button = QPushButton("Стоп")
        self._tray_button = QPushButton("Свернуть в трей")

        self._select_button.clicked.connect(on_select_region)
        self._start_button.clicked.connect(on_start)
        self._stop_button.clicked.connect(on_stop)
        self._tray_button.clicked.connect(on_minimize_to_tray)

        row = QHBoxLayout()
        row.addWidget(self._select_button)
        row.addWidget(self._start_button)
        row.addWidget(self._stop_button)
        row.addWidget(self._tray_button)

        layout = QVBoxLayout(self._widget)
        layout.addWidget(self._status)
        layout.addLayout(row)
        self.set_running(False)
        self._widget.resize(560, 90)
        self._widget.move(80, 80)

    def minimize_requested(self) -> None:
        self._on_minimize_to_tray()

    def show(self) -> None:
        self._widget.show()
        self._widget.raise_()
        self._widget.activateWindow()

    def hide(self) -> None:
        self._widget.hide()

    def set_status(self, text: str) -> None:
        self._status.setText(text)

    def set_running(self, running: bool) -> None:
        self._start_button.setEnabled(not running)
        self._stop_button.setEnabled(running)

    def close(self) -> None:
        self._widget.close()
