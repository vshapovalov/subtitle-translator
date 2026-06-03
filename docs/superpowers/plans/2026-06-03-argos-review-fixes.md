# Argos Review Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix Argos review issues without unrelated rewrites and commit verified local changes.

**Architecture:** Keep translation backend identity on translator instances, thread it into cache keys, and add a config-driven `SubtitlePipeline.from_config()` constructor. Optional Argos integration tests should skip only for absent dependency/model signals and fail on unexpected runtime/API failures.

**Tech Stack:** Python 3.11+, pytest, pydantic config, existing dataclass pipeline/cache modules.

---

### Task 1: Backend-Aware Translation Runtime

**Files:**
- Modify: `src/game_subtitle_translator/translate.py`
- Modify: `src/game_subtitle_translator/cache.py`
- Modify: `src/game_subtitle_translator/realtime.py`
- Modify: `src/game_subtitle_translator/test_scene.py`
- Test: `tests/test_text_pipeline.py`

- [ ] **Step 1: Write failing tests**

Add tests proving `TranslationCache` separates identical text/languages by backend and `SubtitlePipeline.from_config()` creates the translator selected by `config.translation.backend`.

- [ ] **Step 2: Run targeted tests to verify failure**

Run: `python -m pytest tests/test_text_pipeline.py -q`
Expected: FAIL until cache and pipeline constructor are implemented.

- [ ] **Step 3: Implement minimal runtime wiring**

Add `backend` properties to translator classes, include backend in cache key, update callers to pass backend, and add `SubtitlePipeline.from_config(config, ocr, cache=None, stabilizer=None)`.

- [ ] **Step 4: Run targeted tests to verify pass**

Run: `python -m pytest tests/test_text_pipeline.py -q`
Expected: PASS.

### Task 2: Optional Argos Skip Scope

**Files:**
- Modify: `tests/test_argos_optional.py`

- [ ] **Step 1: Replace broad catch**

Skip only when the optional package is missing through `pytest.importorskip`, or when Argos reports a missing package/model with its expected package-not-available exception. Let all other exceptions fail.

- [ ] **Step 2: Run optional test**

Run: `python -m pytest tests/test_argos_optional.py -q`
Expected: SKIP when Argos is unavailable in the environment, PASS if dependency and model are installed, FAIL for unexpected adapter/runtime errors.

### Task 3: README Accuracy

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update wording**

Keep the default mock backend language, state that real OCR is still not connected, and state that optional Argos offline translation is connected when installed and configured.

- [ ] **Step 2: Review Argos config claim**

Confirm README `translation.backend: argos` points to the runtime-backed `create_translator` path.

### Task 4: Verification and Commit

**Files:**
- Verify all modified files

- [ ] **Step 1: Run targeted tests**

Run: `python -m pytest tests/test_text_pipeline.py tests/test_argos_optional.py -q`
Expected: PASS/SKIP according to optional Argos availability.

- [ ] **Step 2: Run full tests and static checks**

Run: `python -m pytest tests -q`
Run: `python -m compileall src tests`
Run: `ruff check .`
Expected: all commands exit 0.

- [ ] **Step 3: Commit locally**

Commit only after verification passes, using the repo Lore commit protocol.
