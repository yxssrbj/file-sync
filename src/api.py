import hashlib
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from config import STORAGE_ROOT
from inventory import scan_inventory
from sync import compare_hash


app = FastAPI()


class FileReq(BaseModel):
    path: str
    size: int
    sha256: str


@app.post("/api/inventory")
async def create_inventory(request: list[FileReq]):
    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    server_inventory = scan_inventory(STORAGE_ROOT)
    client_inventory = [file.model_dump() for file in request]
    return compare_hash(client_inventory, server_inventory)


@app.post("/api/uploadfile")
def create_upload_file(
    path: Annotated[str, Form()],
    sha256: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
):
    relative_path = PurePosixPath(path)
    windows_path = PureWindowsPath(path)

    if (
        not path
        or relative_path == PurePosixPath(".")
        or relative_path.is_absolute()
        or windows_path.drive
        or "\\" in path
        or ".." in relative_path.parts
    ):
        file.file.close()
        raise HTTPException(status_code=400, detail="Invalid relative file path")

    root = STORAGE_ROOT.resolve()
    destination = (root / Path(*relative_path.parts)).resolve()
    if not destination.is_relative_to(root):
        file.file.close()
        raise HTTPException(status_code=400, detail="Invalid relative file path")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".uploading",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            shutil.copyfileobj(file.file, temp_file)

        with temp_path.open("rb") as saved_file:
            received_sha256 = hashlib.file_digest(saved_file, "sha256").hexdigest()

        if received_sha256 != sha256.lower():
            raise HTTPException(status_code=400, detail="Uploaded file hash did not match")

        os.replace(temp_path, destination)
        return {
            "saved": relative_path.as_posix(),
            "sha256": received_sha256,
        }
    finally:
        file.file.close()
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
