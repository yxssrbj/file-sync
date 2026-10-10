from fastapi import FastAPI, File, UploadFile
from typing import Annotated
from pydantic import BaseModel
from inventory import scan_inventory
from pathlib import Path
from sync import compare_hash


app = FastAPI()

class FileReq(BaseModel):
    path: str
    size: int
    sha256: str


@app.post("/api/inventory")
async def create_file(request: list[FileReq]):
    server_inventory = scan_inventory(Path("demo/server-storage").resolve())
    client_inventory = [file.model_dump() for file in request]
    comparison_result = compare_hash(client_inventory, server_inventory)
    return comparison_result


@app.post('/api/uploadfile')
async def create_upload_file(files: list[UploadFile]):
