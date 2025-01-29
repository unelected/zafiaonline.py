<h1 align="center">
  Mafia Online API on Python
</h1>

<p align="center">This library for <a href="https://play.google.com/store/apps/details?id=com.tokarev.mafia">Mafia Online</a></p>

![Python version](https://img.shields.io/badge/python-3.9+-blue.svg)


# Install
```
git clone https://github.com/unelected/zafiaonline.py.git
```
## Requirements

For correct operation of the library, you will need to install the following libraries:

- [websockets](https://github.com/python-websockets/websockets)
- [msgspec](https://github.com/jcrist/msgspec)
- [requests](https://github.com/psf/requests)

You can install them using `pip`:

```bash
pip install websockets msgspec requests
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
