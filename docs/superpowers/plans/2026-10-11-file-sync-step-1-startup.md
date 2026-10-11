# File Sync Step 1: Predictable Server Startup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the FastAPI app import and start from either the repository root or `src`, without scanning the client folder during import, and always use one absolute storage path.

**Architecture:** Move the storage-root setting into `src/config.py`, remove the source-folder scan from `src/sync.py` module import, and keep `api.py` importing only the setting and comparison function it needs. Add subprocess tests that import the app from both working directories and check default and overridden storage paths.

**Tech Stack:** Python 3.14, FastAPI, Uvicorn, pathlib, pytest; no new dependencies.

**Spec:** `docs/superpowers/specs/2026-10-11-personal-file-sync-security-design.md`, Step 1.

## Global Constraints

- Keep FastAPI bound to loopback; use `127.0.0.1` explicitly in startup commands.
- Default storage remains `Path.home() / "Desktop" / "file-sync-storage"`.
- Preserve `FILE_SYNC_STORAGE` as the storage override; reject a relative override so startup cannot silently pick a different folder based on the current directory.
- Do not scan or read client source files while importing the API or comparison helper.
- Do not change hash comparison behavior or add remote access in this step.
- Keep existing uncommitted changes outside this plan untouched.

## Review Focus

- Repository-root startup currently makes `sync.py` scan a nonexistent `demo/source`; test import from repository root and from `src`.
- Relative `FILE_SYNC_STORAGE` values can change meaning with the working directory; test that the setting rejects a relative value with a clear error.
- Default and absolute override storage paths must be identical regardless of working directory; assert both from subprocess imports.
- Removing the global scan must not alter upload/unchanged classification; retain a small `compare_hash` regression test.
- The app must remain local-only; start Uvicorn with `--host 127.0.0.1` from both working directories and check its startup address.

---

### Task 1: Make imports side-effect-free and storage configuration stable

**Files:**
- Create: `src/config.py`
- Modify: `src/api.py`
- Modify: `src/sync.py`
- Create: `tests/test_server_startup.py`
- Create: `tests/test_sync.py`

**Interfaces:**
- `src/config.py` produces `STORAGE_ROOT: pathlib.Path`, selected from absolute `FILE_SYNC_STORAGE` or the default `Path.home() / "Desktop" / "file-sync-storage"`.
- `src/api.py` imports `STORAGE_ROOT` from `config.py`; API routes and response shapes remain unchanged.
- `src/sync.py` exports `compare_hash(client_inventory: list[dict], server_inventory: list[dict]) -> dict[str, list[str]]` and performs no filesystem scan at import time.

- [ ] **Step 1: Write failing startup tests**

Create subprocess tests that import `api` with `src` on `PYTHONPATH` while the subprocess working directory is each of the repository root and `src`. Assert that both imports succeed and print the same absolute default storage path. Add a case with an absolute `FILE_SYNC_STORAGE` override and assert both working directories use it. Add a case with a relative override and assert startup fails with a clear configuration error.

- [ ] **Step 2: Run the focused tests and confirm the current failure**

Run from the repository root: `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests\test_server_startup.py -q`.

Expected: repository-root import fails because `sync.py` scans `demo/source`; relative storage override is accepted instead of rejected.

- [ ] **Step 3: Add stable storage configuration**

In `src/config.py`, define `STORAGE_ROOT` from the `FILE_SYNC_STORAGE` environment variable or the Desktop default. Expand `~`; raise a clear `ValueError` if an explicitly configured path is not absolute.

- [ ] **Step 4: Remove the import-time source scan**

In `src/sync.py`, remove the module-level `Path("demo/source")` and `scan_inventory` call. Keep `compare_hash` unchanged. In `src/api.py`, import `STORAGE_ROOT` from `config.py` and remove its duplicate storage-setting block.

- [ ] **Step 5: Add comparison regression coverage**

In `tests/test_sync.py`, pass in-memory inventories covering one missing file, one changed hash, and one matching hash. Assert the missing and changed paths are in `upload`, and the matching path is in `unchanged`.

- [ ] **Step 6: Run focused and full tests**

Run from the repository root: `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests\test_server_startup.py tests\test_sync.py -q`, then `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q`.

Expected: all tests pass; importing `api` from both directories uses the same absolute storage root and does not inspect `demo/source`.

- [ ] **Step 7: Smoke-test both server launch locations**

From the repository root, run `.\.venv\Scripts\python.exe -m uvicorn api:app --app-dir src --host 127.0.0.1 --port 8001`. Stop it, then from `src` run `..\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8001`. Confirm each reports `http://127.0.0.1:8001` and starts without scanning the source folder.

Expected: both launches start successfully and bind only to loopback. Stop each server after confirming startup.

- [ ] **Step 8: Review the diff with the user before proceeding**

Show only this step's code and test changes, summarize the test and launch results, and wait for the user's decision. Do not start Step 2 until the user explicitly says to continue.
