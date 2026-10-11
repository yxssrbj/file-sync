import os
from pathlib import Path


_configured_storage = os.environ.get("FILE_SYNC_STORAGE")
if _configured_storage:
    STORAGE_ROOT = Path(_configured_storage).expanduser()
    if not STORAGE_ROOT.is_absolute():
        raise ValueError("FILE_SYNC_STORAGE must be an absolute path")
else:
    STORAGE_ROOT = Path.home() / "Desktop" / "file-sync-storage"
