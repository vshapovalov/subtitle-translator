from __future__ import annotations

import sys
from pathlib import Path

from game_subtitle_translator.capture import ScreenCapture
from game_subtitle_translator.config import (
    AppConfig,
    CaptureRegion,
    apply_translation_region,
    save_config,
)
from game_subtitle_translator.ocr import create_ocr_engine
from game_subtitle_translator.realtime import SubtitlePipeline
from game_subtitle_translator.scanner import RegionScanner
from game_subtitle_translator.ui.control_overlay import ControlOverlay
from game_subtitle_translator.ui.region_selector import RegionSelector
from game_subtitle_translator.ui.text_overlay import TextOverlay


class TranslatorApp:
    """Windows-focused long-lived utility app."""

    def __init__(self, config: AppConfig, config_path: Path) -> None:
        from PySide6.QtCore import QTimer
        from PySide6.QtGui import QAction, QIcon
        from PySide6.QtWidgets import QMenu, QApplication, QSystemTrayIcon

        self._QApplication = QApplication
        self.config = config
        self.config_path = config_path
        ocr = create_ocr_engine(config.ocr.engine, config.ocr.source_lang)
        self.runtime = SubtitlePipeline.from_config(config, ocr=ocr)
        self.capture = ScreenCapture(config.capture)
        self.text_overlay = TextOverlay(config.overlay)
        self.scanner = RegionScanner(
            self.capture,
            self.runtime,
            on_translation=self._show_translation,
            on_error=self._show_error,
        )
        self.controls = ControlOverlay(
            on_select_region=self.select_region,
            on_start=self.start_scanning,
            on_stop=self.stop_scanning,
            on_minimize_to_tray=self.minimize_to_tray,
        )
        self.timer = QTimer()
        self.timer.timeout.connect(self.scanner.scan_once)
        self.timer.setInterval(max(1, int(1000 / self.config.capture.fps)))

        self.tray = QSystemTrayIcon(QIcon(), None)
        self.tray.setToolTip("Subtitle Translator")
        menu = QMenu()
        show_action = QAction("Show controls")
        start_action = QAction("Start scanning")
        stop_action = QAction("Stop scanning")
        quit_action = QAction("Quit")
        show_action.triggered.connect(self.show_controls)
        start_action.triggered.connect(self.start_scanning)
        stop_action.triggered.connect(self.stop_scanning)
        quit_action.triggered.connect(self.quit)
        menu.addAction(show_action)
        menu.addAction(start_action)
        menu.addAction(stop_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def show_controls(self) -> None:
        self.controls.show()

    def minimize_to_tray(self) -> None:
        self.controls.hide()
        # Deliberately do not stop scanning; user requested scanning to continue.

    def select_region(self) -> None:
        self.controls.set_status("Выберите регион мышкой. Esc отменяет выбор.")
        self._selector = RegionSelector(self._region_selected)
        self._selector.show()

    def _region_selected(self, region: CaptureRegion) -> None:
        apply_translation_region(self.config, region)
        save_config(self.config, self.config_path)
        self.capture = ScreenCapture(self.config.capture)
        self.scanner.capture = self.capture
        self.text_overlay.update_config(self.config.overlay)
        self.controls.set_status(
            f"Регион: {region.left},{region.top} {region.width}x{region.height}"
        )

    def start_scanning(self) -> None:
        self.scanner.start()
        self.controls.set_running(True)
        self.controls.set_status("Scanning...")
        self.timer.start()

    def stop_scanning(self) -> None:
        self.timer.stop()
        self.scanner.stop()
        self.text_overlay.clear()
        self.controls.set_running(False)
        self.controls.set_status("Stopped")

    def _show_translation(self, text: str) -> None:
        self.text_overlay.show_text(text)
        self.controls.set_status("Translated")

    def _show_error(self, exc: Exception) -> None:
        self.controls.set_status(f"Error: {exc}")

    def quit(self) -> None:
        self.stop_scanning()
        self.text_overlay.close()
        self.tray.hide()
        self._QApplication.quit()


def run_ui(config: AppConfig, config_path: Path) -> int:
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setQuitOnLastWindowClosed(False)
    translator_app = TranslatorApp(config, config_path)
    translator_app.show_controls()
    return int(app.exec())
