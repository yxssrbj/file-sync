import hashlib
import os
from pathlib import Path


def scan_inventory(root):
    inventory = []
    for folder, subfolders, filenames in root.walk(on_error=print):
        for name in filenames:
            file_path = folder / name
            relative_path = file_path.relative_to(root)
            # content = Path(file_path).read_text()
            size = os.path.getsize(file_path)
            digest = ''
            with open(file_path, "rb") as f:
                digest = hashlib.file_digest(f, "sha256").hexdigest()
            inventory.append(
                {
                    "path":relative_path.as_posix(),
                    "size":size,
                    "sha256":digest
                    # "content":content
                }
            )
    return inventory
