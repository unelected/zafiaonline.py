<h1 align="center">
  Mafia Online API on Python
</h1>

<p align="center">This library for <a href="https://play.google.com/store/apps/details?id=com.tokarev.mafia">Mafia Online</a></p>

![Python version](https://img.shields.io/badge/python-3.9+-blue.svg)

# Install

To install the package, you can either use `pip` directly or clone the repository and install it manually:

## Option 1: Using pip (recommended)
```bash
pip install git+https://github.com/unelected/zafiaonline.py.git
```

## Option 2: Manual installation
If you prefer to clone the repository and install it manually, follow these steps:

```bash
git clone https://github.com/unelected/zafiaonline.py.git
cd zafiaonline.py
pip install .
```


# Import and Auth
```python
import zafiaonline
import asyncio

async def main():
    Mafia = zafiaonline.Client()
    await Mafia.sign_in("email", "password")
asyncio.run(main())
```
