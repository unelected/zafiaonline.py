<h1 align="center">
  Mafia Online API on Python
</h1>

<p align="center">This library for <a href="https://play.google.com/store/apps/details?id=com.tokarev.mafia">Mafia Online</a></p>

![Python version](https://img.shields.io/badge/python-3.9+-blue.svg)

## ⚠️ Important Update: API Changes!

The original app developer suddenly **changed their API**, which means **most of the requests through the old wrapper are now broken**. Yeah… we weren’t ready for that either.

But here’s the good news:  
The library now supports the new **WebSocket server (wss://)**! 

If you don’t have root access on your device, you can still try to **sniff the server traffic through this library** and interact with the app that way. For now, it’s the best (and only) option without root.

We’ll do our best to keep things up to date. Stay tuned for updates!

P.S. If you run into bugs — feel free to fork ths repository.


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
