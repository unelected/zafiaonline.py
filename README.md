<h1 align="center">
  Mafia Online API on Python
</h1>


<p align="center">This library for <a href="https://play.google.com/store/apps/details?id=com.tokarev.mafia">Mafia Online</a></p>

# Install
```
git clone https://github.com/unelected/zafiaonline.py.git
```
## Requirements

For correct operation of the library, you will need to install the following libraries:

- [websocket-client](https://github.com/websocket-client/websocket-client)
- [msgspec](https://github.com/jcrist/msgspec)
- [requests](https://github.com/psf/requests)

You can install them using `pip`:

```bash
pip install websocket-client msgspec requests
```

# Import and Auth
```python
import zafiaonline

Mafia = zafiaonline.Client()
Mafia.sign_in("email", "password")
```