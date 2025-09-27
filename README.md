<h1 align="center">
  Mafia Online API for Python
</h1>

<p align="center">
  A Python client library for <a href="https://play.google.com/store/apps/details?id=com.tokarev.mafia">Mafia Online</a>.
</p>

<p align="center">
  <img alt="PyPI" src="https://img.shields.io/pypi/v/zafiaonline.svg">
  <img alt="Read the Docs" src="https://img.shields.io/readthedocs/zafiaonlinepy?label=docs">
  <img alt="Python version" src="https://img.shields.io/badge/python-3.9%2B-blue.svg">
  <img alt="License" src="https://img.shields.io/badge/license-GPL--3.0--or--later-red.svg">
</p>

---

## Overview

`zafiaonline` is a small library providing utilities and client functionality for interacting with the **Mafia Online** service. It includes:
- an async `Client` for authentication and API calls,
- anti-ban utilities and message tracking helpers,
- transport layers and ancillary utilities.

Full documentation is available at:  
https://zafiaonlinepy.readthedocs.io/en/latest/

---

## Install

Install from PyPI:

```bash
pip install zafiaonline
````

Install for development from source:

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
pip install -e .
pip install -r docs/requirements.txt   # optional: build docs locally
```

> Note: Read the Docs builds use Python **3.12** (RTD may not support 3.13). The library is compatible with Python 3.9+.

---

## Quickstart — Import and Auth

Example using the async `Client`:

```python
import asyncio
import zafiaonline

async def main():
    client = zafiaonline.Client()
    await client.auth.sign_in("email@example.com", "your_password")
    # Use the client for API calls, then sign out
    await client.auth.sign_out()

asyncio.run(main())
```

If you prefer a synchronous helper wrapper, wrap async calls via `asyncio.run()` or your own event loop.

---

## Examples

Create a client and fetch some data (pseudo-code):

```python
import asyncio
import zafiaonline

async def example():
    client = zafiaonline.Client()
    await client.auth.sign_in("email", "password")
    profile = await client.users.get_profile()   # example API
    print(profile)
    await client.auth.sign_out()

asyncio.run(example())
```

Adjust imports and method names to the actual API surface of your package.

---

## Documentation

Docs are published at:
[https://zafiaonlinepy.readthedocs.io/en/latest/](https://zafiaonlinepy.readthedocs.io/en/latest/)

Build docs locally:

```bash
cd docs
make html
# Open docs/_build/html/index.html
```

If you use the `src/` layout, ensure `docs/source/conf.py` contains:

```python
import os
import sys
sys.path.insert(0, os.path.abspath("../../src"))
master_doc = "index"
```

---

## Read the Docs (CI) config

Example `.readthedocs.yaml` to place in the repo root:

```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: latest

sphinx:
  configuration: docs/source/conf.py

python:
  install:
    - method: pip
      path: .
    - requirements: docs/requirements.txt
```

And `docs/requirements.txt` (basic):

```
sphinx
sphinx-rtd-theme
```

---

## Configuration (YAML)

The library also supports configuration via a **YAML** file for WebSocket connection parameters.  
Example `config.yaml`:

```yaml
host: "dottap.com"
port: 7091
connect_type: "wss"
````

You can then load and use it inside your project:

```python
class Config:
    def __init__(self, path: str = "ws_config.yaml") -> None:
        config_path = files('zafiaonline.transport.websocket').joinpath(path)
        with as_file(config_path) as resource_file:
            with open(resource_file, "r") as config_file:
                config: dict = yaml.safe_load(config_file)
        self.address: str = config.get("address", "dottap.com")
        self.port: int = config.get("port", 7091)
        self.connect_type: str = config.get("connect_type", "wss")
```

This way, connection details are kept separate from your code and can be changed without modifying Python files.

---

## Troubleshooting Sphinx / Documentation

* **`Unexpected indentation`** — fix docstring code examples: use `:` then an indented literal block:

  ```python
  """Typical Usage Example:

      messages = SentMessages(enable_logging=True)
      messages.add_message("hello")
  """
  ```

* **`Index file is not present`** — ensure `docs/source/index.rst` exists and `master_doc = "index"` in `conf.py`.

* **Duplicate or ambiguous cross-references** — avoid re-exporting the same object in `__init__.py` or use fully-qualified cross-references (e.g. `:class:\`zafiaonline.main.Client``) or `:no-index:` to suppress duplicates.

---

## Contributing

1. Fork the repo → create a feature branch → open a PR.
2. Follow code style and include tests for non-trivial changes.
3. In PR description, explain changes and link documentation where applicable.

---

## License

This project is licensed under **GNU GPL v3.0 or later**. See the `LICENSE` file for details.

---

## Contact

Author: `unelected`
Bugs & feature requests: open an issue on the repository.
