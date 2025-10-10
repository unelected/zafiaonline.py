# Copyright (C) 2025 unelected
#
# This file is part of email_generator.
#
# account_generator is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# account_generator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with account_generator. If not, see
# <https://www.gnu.org/licenses/>.

"""
Asynchronous initialization metaclass.

This module defines `AsyncInitMeta`, a metaclass that enables classes to
support asynchronous initialization via an `__ainit__` method. When a class
uses this metaclass, calling the class returns a coroutine that must be awaited
to obtain the fully constructed and initialized instance.

Typical usage example:

    class MyAsyncClass(metaclass=AsyncInitMeta):
        async def __ainit__(self, value: int) -> None:
            await asyncio.sleep(1)
            self.value = value

    async def main():
        obj = await MyAsyncClass(42)
        print(obj.value)  # 42
"""
from typing import Any, Coroutine

class AsyncInitMeta(type):
    def __call__(cls, *args: Any, **kwargs: Any) -> Coroutine[Any, Any, Any]:
        """
        Create an instance of a class with asynchronous initialization support.

        This method overrides the default metaclass `__call__` to allow
        asynchronous construction of objects. It wraps the normal instance
        creation in a coroutine (`init_and_return`) that checks for and
        awaits an `__ainit__` method if it exists.

        Args:
            *args (Any): Positional arguments forwarded to the class constructor.
            **kwargs (Any): Keyword arguments forwarded to the class constructor.

        Returns:
            Coroutine[Any, Any, Any]: A coroutine that resolves to the fully
            constructed and asynchronously initialized instance.
        """
        async def init_and_return() -> Any:
            """
            Create and asynchronously initialize an instance of the class.

            This function first creates an instance of the class using the
            standard constructor (`__init__` if defined). If the created
            instance implements an asynchronous initializer (`__ainit__`),
            it is awaited to complete additional setup. The fully
            initialized instance is then returned.

            Returns:
                Any: The fully constructed and asynchronously initialized
                instance of the class.
            """
            self: Any = super(AsyncInitMeta, cls).__call__(*args, **kwargs)
            if hasattr(self, "__ainit__"):
                await self.__ainit__(*args, **kwargs)
            return self
        return init_and_return()
