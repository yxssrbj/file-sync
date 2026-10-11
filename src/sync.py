def compare_hash(
    client_inventory: list[dict], server_inventory: list[dict]
) -> dict[str, list[str]]:
    upload = []
    unchanged = []
    server_by_path = {
        item['path']:item
        for item in server_inventory
    }

    for client_file in client_inventory:
        path = client_file['path']
        server_file = server_by_path.get(path)


## add a clause for deleting server files that are absent from the laptop inventory
        if server_file is None:
            upload.append(path)
        elif client_file['sha256'] == server_file['sha256']:
            unchanged.append(path)
        else:
            upload.append(path)

    return {"upload":upload, "unchanged":unchanged}
