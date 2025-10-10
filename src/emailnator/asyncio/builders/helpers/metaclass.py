# copyright (c) 2025 unelected
#
# this file is part of email_generator.
#
# account_generator is free software: you can redistribute it and/or modify
# it under the terms of the gnu affero general public license as published by
# the free software foundation, either version 3 of the license, or
# (at your option) any later version.
#
# account_generator is distributed in the hope that it will be useful,
# but without any warranty; without even the implied warranty of
# merchantability or fitness for a particular purpose. see the
# gnu affero general public license for more details.
#
# you should have received a copy of the gnu affero general public license
# along with account_generator. if not, see
# <https://www.gnu.org/licenses/>.

"""
Asynchronous singleton metaclass.

This module defines `AsyncSingletonMeta`, a metaclass that ensures a class
has only one instance in asynchronous contexts. It provides thread-safe
singleton behavior using an `asyncio.Lock` and supports asynchronous
initialization via the `__ainit__` method.

Typical Usage Example:
    class MySingleton(metaclass=AsyncSingletonMeta):
        async def __ainit__(self):
            await asyncio.sleep(1)
            self.value = 42

    async def main():
        obj1 = await MySingleton()
        obj2 = await MySingleton()
        assert obj1 is obj2
"""
import asyncio

from typing import Any


class AsyncSingletonMeta(type):
    """
    Asynchronous metaclass for implementing singleton classes with thread safety.

    This metaclass ensures that only one instance of a class exists, even in
    asynchronous contexts with potential concurrent instantiation. It uses an
    ``asyncio.Lock`` to guarantee that only one coroutine initializes the singleton
    at a time. If the class defines an asynchronous initializer (``__ainit__``),
    it will be awaited during instance creation.

    Attributes:
        _instances (dict): A mapping of classes to their singleton instances.
        _lock (asyncio.Lock): A global lock used to prevent race conditions during
            singleton initialization.
    """
    _instances: dict = {}
    _lock: asyncio.Lock = asyncio.Lock()

    async def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """
        Create or return the singleton instance of a class (with async initialization).

        This method overrides the default metaclass ``__call__`` to implement
        asynchronous singleton behavior. If an instance does not yet exist,
        it acquires a lock to ensure safe concurrent initialization, creates
        the instance, and calls its asynchronous initializer (``__ainit__``)
        if available.

        Args:
            *args (Any): Positional arguments forwarded to the class constructor.
            **kwargs (Any): Keyword arguments forwarded to the class constructor.

        Returns:
            Any: The existing or newly created singleton instance of the class.
        """
        if cls not in cls._instances:
            async with cls._lock:
                if cls not in cls._instances:
                    instance: Any = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
                    if hasattr(instance, "__ainit__"):
                        await instance.__ainit__(*args, **kwargs)
        return cls._instances[cls]
