# File Sync: project structure

This is a build map, not a list of files that already exist. Start with the local version on the Windows laptop, then run the server on the Raspberry Pi 3 when it has power and an operating system.

## Working assumption

- The Windows laptop is where files are created and edited.
- The server keeps a second copy: first in a separate test folder on the laptop, later on the Pi.
- The first sync direction is **laptop → server**. Download/restore comes next. Editing the same file on both sides and automatic deletion are outside the first version.
- Saved product links are separate records shown in a local HTML page served by the same app.

## Intended layout

```text
file-sync/
├── PROJECT_STRUCTURE.md          # This build map
├── DOCUMENTATION.md              # Official references by build milestone
├── README.md                     # Short setup and usage instructions
├── pyproject.toml                # Runtime and development dependencies
├── uv.lock                       # Exact resolved dependency versions
├── .python-version               # Python version used for development
├── .gitignore
├── src/
│   └── file_sync/
│       ├── __init__.py
│       ├── inventory.py          # List files and calculate hashes
│       ├── sync.py               # Decide which files need transfer
│       ├── client.py             # Send inventory/files to the server
│       ├── api.py                # FastAPI endpoints and links page
│       ├── storage.py            # Validate paths and safely store uploads
│       ├── links.py              # Read/write saved-link records
│       ├── templates/
│       │   └── links.html         # HTML cards for saved links
│       └── static/
│           └── style.css          # Minimal page styling
└── tests/
    ├── test_inventory.py
    ├── test_sync.py
    ├── test_storage.py
    └── test_api.py
```

The current `src/api.py` is an early draft. When we build the server, move its useful parts into `src/file_sync/api.py` rather than keeping two competing API entry points.

## How the pieces fit

```text
chosen laptop folder
    ↓ inventory.py (relative path, size, hash)
    ↓ sync.py (what changed?)
    ↓ client.py (HTTP request)
    ↓ api.py (server endpoint)
    ↓ storage.py (validate, write temporary file, verify, replace)
server storage folder

browser → api.py → links.py → saved-link JSON files → links.html
```

The **server storage folder** is configured outside this repository. Personal files, saved links, passwords, and tokens do not belong in Git. Local tests use temporary folders so they cannot touch personal data.

## Build order

1. **Inventory:** scan a small test folder and print file paths, sizes, and SHA-256 hashes. Test nested folders and changed contents.
2. **Sync decisions:** compare laptop and server inventories. Initially plan copies only; report missing, changed, and unchanged files.
3. **Safe storage:** accept only paths inside the chosen server folder; write uploads to a temporary file, verify the hash, then replace the destination. Test invalid paths and interrupted uploads.
4. **Local transfer:** run the server on `127.0.0.1` and send files from another test folder on the same laptop. Run the same sync twice and verify that the second run transfers nothing.
5. **Saved Links page:** add a form for URL, title, brand, category, and note. Store one JSON file per link and render searchable cards with a button to open the original URL.
6. **Pi deployment:** once the Pi boots and is reachable, configure server storage, authentication, and startup on the Pi. Point the laptop client at the Pi and repeat the transfer tests with disposable files.
7. **Automation and recovery:** add scheduled scans or file watching, download/restore, and clear status/error reporting after manual transfer is dependable.

## First milestone

The first deliverable is **inventory only**: given a test folder, the program lists its files and hashes without copying or deleting anything. This gives us a small, checkable foundation before networking or Pi setup.
