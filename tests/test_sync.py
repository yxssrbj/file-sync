from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"


def test_compare_hash_separates_missing_changed_and_unchanged_files(monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(SRC))
    monkeypatch.chdir(SRC)
    from sync import compare_hash

    client_inventory = [
        {"path": "new.txt", "size": 1, "sha256": "new-hash"},
        {"path": "changed.txt", "size": 1, "sha256": "client-hash"},
        {"path": "same.txt", "size": 1, "sha256": "same-hash"},
    ]
    server_inventory = [
        {"path": "changed.txt", "size": 1, "sha256": "server-hash"},
        {"path": "same.txt", "size": 1, "sha256": "same-hash"},
    ]

    result = compare_hash(client_inventory, server_inventory)

    assert result == {
        "upload": ["new.txt", "changed.txt"],
        "unchanged": ["same.txt"],
    }
