from __future__ import annotations

import argparse
from pathlib import Path

from game_subtitle_translator.config import default_config_path, load_config
from game_subtitle_translator.config import AppConfig
from game_subtitle_translator.ocr import create_ocr_engine
from game_subtitle_translator.realtime import SubtitlePipeline


def build_runtime(config: AppConfig) -> SubtitlePipeline:
    ocr = create_ocr_engine(config.ocr.engine, config.ocr.source_lang)
    return SubtitlePipeline.from_config(config, ocr=ocr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Real-time game subtitle translator overlay")
    parser.add_argument("--config", type=str, default=None, help="Path to config.yaml")
    parser.add_argument("--print-config", action="store_true", help="Print resolved config and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config_path = default_config_path() if args.config is None else Path(args.config)
    config = load_config(config_path)

    if args.print_config:
        print(config.model_dump_json(indent=2))
        return 0

    runtime = build_runtime(config)
    print("Game Subtitle Translator MVP skeleton")
    print(f"Config: {config_path}")
    print(f"OCR engine: {config.ocr.engine}")
    print(f"Translation backend: {runtime.translator.backend}")
    print("Next: run with --print-config, then enable OCR/overlay adapters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
