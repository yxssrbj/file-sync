# Documentation reading guide

Use this alongside [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md). Read the **current milestone** first; the later sections are references for when we reach them. The laptop currently uses Python 3.14. These are official Python, library, and Raspberry Pi documentation pages.

## Start here: project tools

| Read | What to learn for this project |
| --- | --- |
| [uv: working on projects](https://docs.astral.sh/uv/guides/projects/) | What `pyproject.toml` and `uv.lock` do; how `uv add` and `uv run` work. |
| [pytest: temporary folders](https://docs.pytest.org/en/stable/how-to/tmp_path.html) | Use `tmp_path` to test scanning and copying without touching personal files. |

The first milestone needs only Python's standard library and pytest. FastAPI, HTTPX, Jinja2, and `python-multipart` are already declared in `pyproject.toml`, but you do not need to study them yet.

## Milestone 1: inventory, no copying

Build a function that receives a folder and reports each file's relative path, size, and SHA-256 hash.

| Read | Use it for |
| --- | --- |
| [`Path.walk()`](https://docs.python.org/3.14/library/pathlib.html#pathlib.Path.walk) | Visit files inside nested folders. |
| [`Path.relative_to()`](https://docs.python.org/3.14/library/pathlib.html#pathlib.PurePath.relative_to) | Store `photos/cat.jpg` instead of a machine-specific absolute path. |
| [`hashlib.file_digest()`](https://docs.python.org/3.14/library/hashlib.html#hashlib.file_digest) | Calculate a SHA-256 hash from a file opened in binary mode. |

Try these with a disposable folder containing one file, one nested file, and an empty folder. Then change a file and check that its hash changes.

## Milestone 2: decide what needs syncing

Compare two inventories by relative path and hash. Classify each source file as **missing**, **changed**, or **unchanged** on the server. For this first version, only missing and changed files are transfer candidates. Use the same [`tmp_path` pytest guide](https://docs.pytest.org/en/stable/how-to/tmp_path.html) to create the two sides in tests.

## Milestone 3: receive files safely

| Read | Use it for |
| --- | --- |
| [`Path.resolve()` and `is_relative_to()`](https://docs.python.org/3.14/library/pathlib.html) | Check the final destination stays inside the configured storage folder. `relative_to()` alone checks path text; it does not resolve symlinks. |
| [`tempfile.NamedTemporaryFile`](https://docs.python.org/3.14/library/tempfile.html#tempfile.NamedTemporaryFile) | Receive into a temporary file before touching an existing file. |
| [`os.replace()`](https://docs.python.org/3.14/library/os.html#os.replace) | Replace the destination after the complete upload and hash check. |

Test a normal nested path, a path containing `..`, a hash mismatch, and an interrupted upload before using personal files.

## Milestone 4: transfer over local HTTP

Run the server on the laptop first and connect to `127.0.0.1`. The Pi comes later.

| Read | Use it for |
| --- | --- |
| [FastAPI: first steps](https://fastapi.tiangolo.com/tutorial/first-steps/) | Create an app and understand routes such as `GET` and `POST`. |
| [FastAPI: request files](https://fastapi.tiangolo.com/tutorial/request-files/) | Receive an upload with `UploadFile`; this is why `python-multipart` is installed. |
| [HTTPX: quickstart](https://www.python-httpx.org/quickstart/) | Send JSON metadata and a multipart file from the client. |
| [HTTPX: timeouts](https://www.python-httpx.org/advanced/timeouts/) | Handle a server that cannot be reached or stops responding. |
| [FastAPI: testing](https://fastapi.tiangolo.com/tutorial/testing/) | Call endpoints with `TestClient` without starting a real server. |

When we start the server, follow [FastAPI's server guide](https://fastapi.tiangolo.com/deployment/manually/). The current project does not yet declare a server runner such as Uvicorn; we will add one at that milestone.

## Milestone 5: saved links and HTML page

| Read | Use it for |
| --- | --- |
| [Python `json`](https://docs.python.org/3.14/library/json.html) | Store one product link and its title, brand, category, and note in a JSON file. |
| [FastAPI: request bodies](https://fastapi.tiangolo.com/tutorial/body/) | Validate submitted link fields with a Pydantic model. |
| [FastAPI: templates](https://fastapi.tiangolo.com/advanced/templates/) | Pass saved links to a Jinja2 HTML template and render cards. |
| [MDN: HTML links](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/a) | Make each card open its original product URL. |

## Milestone 6: Raspberry Pi deployment

Only use these once the Pi 3 has a proper micro-USB power supply and boots. Do not re-image the existing SD card until its contents are understood; writing an image erases it.

| Read | Use it for |
| --- | --- |
| [Raspberry Pi: getting started](https://www.raspberrypi.com/documentation/installation/installing-images/raspberry-pi.html) | Power, SD card, Raspberry Pi OS, and first boot. |
| [Raspberry Pi: remote access](https://www.raspberrypi.com/documentation/computers/remote-access.html) | Enable SSH and connect from Windows. |
| [Raspberry Pi: external storage](https://www.raspberrypi.com/documentation/computers/configuration.html) | Mount the drive that will hold the server's file copy. |

## Milestone 7: automatic checks

After manual sync works, read [watchdog's quickstart](https://python-watchdog.readthedocs.io/en/latest/quickstart.html) for `Observer`, event handlers, and recursive watching. `watchdog` is **not installed yet**. We will still perform periodic full scans so the app can detect changes missed while it was stopped.
