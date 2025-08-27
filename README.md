<h1 align="center">
  Mafia Online API on Python
</h1>

<p align="center">This library for <a href="https://play.google.com/store/apps/details?id=com.tokarev.mafia">Mafia Online</a></p>

![Python version](https://img.shields.io/badge/python-3.9+-blue.svg)


# Install

To install the package from [PyPI](https://pypi.org/project/zafiaonline/), use:

```bash
pip install zafiaonline
```


# Import and Auth
```python
import zafiaonline
import asyncio

async def main():
    Mafia = zafiaonline.Client()
    await Mafia.auth.sign_in("email", "password")
asyncio.run(main())
```
