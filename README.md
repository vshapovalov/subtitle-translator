# Subtitle Translator

Real-time game subtitle translator overlay MVP.

The first implementation is intentionally safe: it uses screen-region capture, OCR, translation, and an overlay. It does **not** inject into games, read process memory, or hook DirectX/Vulkan.

## MVP pipeline

```text
selected screen region -> preprocessing -> OCR -> text stabilization -> translation cache -> overlay
```

## Current status

Implemented and tested:

- config models and default `config.yaml` creation
- screen region capture adapter
- OCR and translation interfaces with mock backends
- image preprocessing helper
- text normalization and subtitle stability filter
- in-memory translation cache
- headless-safe console overlay stub
- CLI skeleton

Not implemented yet:

- Qt transparent always-on-top overlay
- region selection UI
- real OCR backend adapter
- real translation backend adapter
- global hotkeys
- Windows packaging

## Development

```bash
python -m pytest tests -q
python -m game_subtitle_translator.main --print-config
```

## Safety notes

Prefer borderless fullscreen/windowed games for overlay compatibility. Avoid process injection and memory inspection, especially around anti-cheat protected games.
