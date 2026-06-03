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
- Argos Translate adapter for offline translation when optional packages and language models are installed
- image preprocessing helper
- text normalization and subtitle stability filter
- in-memory translation cache
- headless-safe console overlay stub
- CLI skeleton

Not implemented yet:

- Qt transparent always-on-top overlay
- region selection UI
- real OCR backend adapter
- global hotkeys
- Windows packaging

## Development

```bash
python -m pytest tests -q
python -m game_subtitle_translator.main --print-config
```

## Запуск и тестовый демо-сценарий

Проект сейчас работает как безопасный MVP для Linux/headless и локальной разработки:
захват области экрана, OCR-абстракция, стабилизация текста, кэш перевода и
консольный overlay. Реальный OCR-адаптер еще не подключен; перевод по
умолчанию использует mock-бэкенд без сети, а optional Argos offline backend
можно включить при установленных пакетах и языковой модели.

Установить проект для разработки:

```bash
python -m pip install -e ".[test]"
```

Показать текущую конфигурацию:

```bash
game-subtitle-translator --print-config
# или
python -m game_subtitle_translator.main --print-config
```

Запустить MVP CLI:

```bash
game-subtitle-translator
```

Сгенерировать детерминированную тестовую сцену с английскими субтитрами:

```bash
game-subtitle-test-scene --output-dir build/test-scene
# или
python -m game_subtitle_translator.test_scene --output-dir build/test-scene
```

Этот demo harness рендерит PNG-кадры через Pillow: темная игровая сцена,
subtitle bar и английский текст. Для автоматических тестов субтитры также
записаны в PNG metadata; `DeterministicSceneOcrEngine` читает эту metadata через
обычный OCR-интерфейс. Это намеренно не имитация реального OCR, а стабильный
E2E-контур для проверки пути:

```text
rendered test frames -> OCR abstraction -> TextStabilizer -> Translator/cache
```

Когда появится реальный OCR-адаптер, его можно подключить к тому же интерфейсу
и оставить этот deterministic harness как быстрый regression test.

Запустить тесты:

```bash
python -m pytest tests -q
python -m compileall src tests
ruff check .
```

## Translation backends

The default backend is `mock`, which is deterministic and requires no network,
optional packages, or translation models:

```yaml
translation:
  backend: mock
  source_lang: en
  target_lang: uk
```

Argos Translate is available as an optional offline backend:

```bash
python -m pip install -e ".[argos]"
```

Then configure:

```yaml
translation:
  backend: argos
  source_lang: en
  target_lang: uk
```

Argos language packages/models are installed separately from the Python package.
The runtime pipeline factory reads `translation.backend` and constructs the
configured translator backend.
If `argostranslate` or the requested language model is missing, Argos-specific
tests skip explicitly instead of failing CI for absent optional dependencies.

## Safety notes

Prefer borderless fullscreen/windowed games for overlay compatibility. Avoid process injection and memory inspection, especially around anti-cheat protected games.
