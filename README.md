
# emailnator-wrapper

[![PyPI](https://img.shields.io/pypi/v/emailnator-wrapper.svg?color=blue)](https://pypi.org/project/emailnator-wrapper/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Docs](https://img.shields.io/badge/docs-online-success)](https://emailnator-wrapper.readthedocs.io/en/latest/)

Asynchronous and synchronous API wrapper for **EmailNator**.

Provides a small, well-typed SDK to generate temporary Gmail-style addresses and read incoming messages.
Designed for both standalone scripts and integration into automation or testing pipelines.

---

## 🚀 Features

✅ Fully **asynchronous core** using `httpx.AsyncClient`
✅ **Synchronous wrapper** for blocking workflows
✅ Automatic **XSRF token** management via `XsrfManager`
✅ Async-safe **singleton HTTP client** (`AsyncSingletonMeta`)
✅ YAML-based **configurable setup** with optional proxy
✅ Google-style **docstrings** and complete type hints
✅ **Thoroughly tested** with `pytest` (`tests/sync`, `tests/asyncio`)

📚 **Documentation:** [ReadTheDocs](https://emailnator-wrapper.readthedocs.io/en/latest/)

---

## 🧩 Requirements

* Python **3.9+** (tested on 3.13)
* Dependencies:

  * `httpx`
  * `PyYAML`
  * (for tests) `pytest`, `pytest-asyncio`

---

## 💾 Installation

```bash
pip install emailnator-wrapper
```

---

## ⚙️ Configuration

`emailnator/config/config.yaml` (example):

```yaml
BASE_URL: https://www.emailnator.com
TIMEOUT: 15
USE_HTTP2: true
USER_AGENT: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
GMAIL_CONFIG:
  - dotGmail
  - plusGmail
PROXY: null
```

**Notes:**

* Use `null` (not `"None"`) to disable proxies.
* Never store credentials or secrets in YAML files.

---

## 🚀 Quickstart — Asynchronous (recommended)

`examples/async_example.py`

```python
import asyncio
from emailnator.asyncio.email_generator import AsyncEmailGenerator

async def main():
    generator = await AsyncEmailGenerator()
    email = await generator.generate_email()
    messages = await generator.get_messages(email)
    print(f"Email: {email}\nMessages: {messages}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ⚡ Quickstart — Synchronous Wrapper

`examples/sync_example.py`

```python
from emailnator.sync.email_generator import EmailGenerator

def main():
    gen = EmailGenerator()
    email = gen.generate_email()
    messages = gen.get_messages(email)
    print(f"Email: {email}\nMessages: {messages}")

if __name__ == "__main__":
    main()
```

---

## 📚 Public API Overview

| Component               | Description                                        |
| ----------------------- | -------------------------------------------------- |
| `AsyncEmailGenerator`   | High-level async interface. Awaitable constructor. |
| `Generators`            | Wraps `/generate-email` endpoint (bulk + single).  |
| `MessageGetter`         | Retrieves and parses inbox messages.               |
| `AsyncEmailnatorClient` | Shared async HTTP client singleton.                |
| `XsrfManager`           | Manages XSRF lifecycle and headers.                |
| `config`                | Loads YAML into structured config attributes.      |

---

## 🧩 Behavior Notes

* Always **`await` the constructor** if using async metaclass (`await AsyncEmailGenerator()`).
* YAML `PROXY: null` means *no proxy* — don’t use `"None"`.
* Possible HTTP issues (`403`, `419`) may stem from **bot protection** — consider rotating proxies.
* Avoid using `asyncio.run()` inside an already running loop.

---

## 🧪 Tests

Tests are divided into two categories:

```
tests/
├── asyncio/
│   ├── test_generators.py
│   ├── test_message_getter.py
│   └── test_email_generator.py
└── sync/
    ├── test_generators_sync.py
    └── test_email_generator_sync.py
```

### Run all tests

```bash
pytest -v
```

### Run only async tests

```bash
pytest tests/asyncio -v
```

### Run only sync tests

```bash
pytest tests/sync -v
```

All tests use `pytest-asyncio` and can be executed locally or in CI (GitHub Actions workflow provided).

---

## 📘 Documentation

Full API documentation is available on ReadTheDocs:
-> [https://emailnator-wrapper.readthedocs.io/en/latest/](https://emailnator-wrapper.readthedocs.io/en/latest/)

You’ll find:

* Installation guide
* API references (async & sync layers)
* Architecture overview
* Examples & testing guide

---

## ⚠️ Troubleshooting

| Issue                                             | Cause / Fix                                         |
| ------------------------------------------------- | --------------------------------------------------- |
| `coroutine object has no attribute`               | Forgot to `await` async constructor.                |
| `RuntimeWarning: coroutine was never awaited`     | Created coroutine but didn’t await it.              |
| `ValueError: Unknown scheme for proxy URL "None"` | Fix YAML: use `null` instead of `"None"`.           |
| HTTP 419 / “Page Expired”                         | Missing or expired XSRF token — refresh it.         |
| HTTP 403                                          | Cloudflare or bot protection triggered — use proxy. |

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch (`feature/my-change`).
3. Add or update tests under `tests/`.
4. Open a Pull Request.

✅ Follow code style: type hints, async-safe patterns, Google-style docstrings.
✅ Keep public API backward-compatible when possible.

---

## 📄 License

Licensed under the **GNU Affero General Public License v3 (AGPL-3.0)**.
See [LICENSE](./LICENSE) for full details.

---

## 🌐 Project Links

| Resource                  | URL                                                                                       |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| 📘 Documentation          | [emailnator-wrapper.readthedocs.io](https://emailnator-wrapper.readthedocs.io/en/latest/) |
| 🐍 PyPI                   | [pypi.org/project/emailnator-wrapper](https://pypi.org/project/emailnator-wrapper/)       |

