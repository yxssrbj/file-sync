import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
IMPORT_API = "import api; print(api.STORAGE_ROOT)"
WORKING_DIRECTORIES = [
    pytest.param(REPO_ROOT, id="repository-root"),
    pytest.param(SRC, id="src"),
]


def import_api(cwd: Path, storage_override: str | None = None) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("FILE_SYNC_STORAGE", None)
    existing_pythonpath = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = os.pathsep.join(
        value for value in (str(SRC), existing_pythonpath) if value
    )
    if storage_override is not None:
        environment["FILE_SYNC_STORAGE"] = storage_override

    return subprocess.run(
        [sys.executable, "-c", IMPORT_API],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("cwd", WORKING_DIRECTORIES)
def test_api_import_uses_same_default_storage_root_from_any_directory(cwd: Path) -> None:
    result = import_api(cwd)

    expected = str(Path.home() / "Desktop" / "file-sync-storage")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == expected


@pytest.mark.parametrize("cwd", WORKING_DIRECTORIES)
def test_api_import_uses_absolute_storage_override(cwd: Path, tmp_path: Path) -> None:
    override = tmp_path / "custom-storage"
    result = import_api(cwd, str(override))

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(override)


def test_api_rejects_relative_storage_override() -> None:
    result = import_api(SRC, "relative-storage")

    assert result.returncode != 0
    assert "FILE_SYNC_STORAGE must be an absolute path" in result.stderr
