from __future__ import annotations

import argparse

from game_subtitle_translator.config import default_config_path, load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Real-time game subtitle translator overlay")
    parser.add_argument("--config", type=str, default=None, help="Path to config.yaml")
    parser.add_argument("--print-config", action="store_true", help="Print resolved config and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config_path = default_config_path() if args.config is None else __import__("pathlib").Path(args.config)
    config = load_config(config_path)

    if args.print_config:
        print(config.model_dump_json(indent=2))
        return 0

    print("Game Subtitle Translator MVP skeleton")
    print(f"Config: {config_path}")
    print("Next: run with --print-config, then enable OCR/overlay adapters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
