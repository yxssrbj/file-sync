import tempfile
from pathlib import Path
from inventory import scan_inventory
from sync import compare_hash
import shutil
import requests
import httpx


source_root = Path("demo/source").resolve()
server_root = Path("demo/server-storage").resolve()


client_inventory = scan_inventory(source_root)
server_inventory = scan_inventory(server_root)

inventory_by_path = {item["path"]: item for item in client_inventory}

def send_files(client_inventory):

    url = 'http://127.0.0.1:8000/api'
    comparison_result = requests.post(f"{url}/inventory", json=client_inventory).json()
    print(comparison_result)

    if len(comparison_result['upload']) == 0:
        print("No documents to upload - Server up to date !")
    else:
       for relative_path in comparison_result['upload']:
           record = inventory_by_path[relative_path]
           source_file = source_root / relative_path

           with source_file.open("rb") as file_handle:
               response = httpx.post(f"{url}/uploadfile",
                   data={
                       "path":relative_path,
                       "sha256":record["sha256"],
                   },
                   files={
                       "file":(
                           source_file.name,
                           file_handle,
                           "application/octet-stream"
                       )
                   })
               response.raise_for_status()





#    for file in client_inventory:
#
#        source_file = source_root / file['path']
#        destination = server_root / file['path']
#        destination.parent.mkdir(parents=True, exist_ok=True)
#
#        with tempfile.NamedTemporaryFile(
#            mode="wb",
#            dir=destination.parent,
#            prefix=f".{destination.name}",
#            suffix=".tmp",
#            delete=False
#        ) as temp_file:
#            temp_path = Path(temp_file.name)
#            with source_file.open("rb") as source:
#                shutil.copyfileobj(source, temp_file)
#            print(temp_path)


send_files(client_inventory)
