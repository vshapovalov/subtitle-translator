from __future__ import annotations

import argparse
from pathlib import Path

from game_subtitle_translator.config import AppConfig, default_config_path, load_config
from game_subtitle_translator.ocr import create_ocr_engine
from game_subtitle_translator.realtime import SubtitlePipeline


def build_runtime(config: AppConfig) -> SubtitlePipeline:
    ocr = create_ocr_engine(config.ocr.engine, config.ocr.source_lang)
    return SubtitlePipeline.from_config(config, ocr=ocr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Real-time game subtitle translator overlay")
    parser.add_argument("--config", type=str, default=None, help="Path to config.yaml")
    parser.add_argument("--print-config", action="store_true", help="Print resolved config and exit")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config/runtime wiring without opening the Windows UI",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config_path = default_config_path() if args.config is None else Path(args.config)
    config = load_config(config_path)

    if args.print_config:
        print(config.model_dump_json(indent=2))
        return 0

    if args.dry_run:
        runtime = build_runtime(config)
        print("Game Subtitle Translator Windows UI runtime")
        print(f"Config: {config_path}")
        print(f"OCR engine: {config.ocr.engine}")
        print(f"Translation backend: {runtime.translator.backend}")
        return 0

    try:
        from game_subtitle_translator.ui.app import run_ui
    except ImportError as exc:
        raise RuntimeError(
            "Windows UI requires the optional ui dependency. "
            'Install it with: pip install -e ".[ui,ocr,argos]"'
        ) from exc

    return run_ui(config, config_path)


if __name__ == "__main__":
    raise SystemExit(main())
