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
Emailnator HTTP client singleton module.

This module provides a thread-safe singleton wrapper around `httpx.Client` that
handles automatic fetching, decoding, and refreshing of XSRF tokens from cookies,
as well as preparation of standard HTTP headers.

Typical Usage Example:
    from emailnator.asyncio.builders.builders import AsyncEmailnatorClient

    # Use as a context manager
    with emailnator_client as client:
        headers = client.get_headers()
        token = client.get_xsrf_token()
        http_client = client.get_client()

    # Or use methods directly
    emailnator_client.refresh_token()
    emailnator_client.close()
"""
from __future__ import annotations

import asyncio
import httpx

from emailnator.asyncio.builders.helpers.metaclass import AsyncSingletonMeta
from emailnator.asyncio.builders.helpers.xsrf_token_service import XsrfManager
from emailnator.config.config import config
from emailnator.helpers import logger


class AsyncEmailnatorClient(metaclass=AsyncSingletonMeta):
    """
    A singleton wrapper around `httpx.AsyncClient` that manages XSRF tokens and standard headers.

    This class ensures that only one instance exists and provides thread-safe methods
    to interact with the HTTP client. It automatically handles fetching, decoding, 
    and refreshing the XSRF token from cookies, as well as preparing default headers.

    The following functionality is provided:
        - Access to the HTTP client via `get_client()`.
        - Fetching or automatically ensuring the XSRF token and headers.
        - Forcibly refreshing the XSRF token with `refresh_token()`.
        - Closing the client and clearing internal state with `close()`.
        - Context manager support via `with` statements.

    Attributes:
        _client (httpx.AsyncClient): The HTTP client used for making requests.
        _xsrf_token (Optional[str]): The XSRF token for CSRF protection, initially None.
        _headers (dict[str, str]): A dictionary storing HTTNoneinternal_lock (threading.Lock): A reentrant lock for thread-safe operations.
        _initialized (bool): Flag indicating whether the instance has been initialized.
    """
    async def __ainit__(self) -> None:
        self._client: httpx.AsyncClient = httpx.AsyncClient(
            proxy=config.PROXY if config.PROXY else None,
            http2=config.USE_HTTP2,
            timeout=config.TIMEOUT,
            trust_env=False
        )
        self._internal_lock: asyncio.Lock = asyncio.Lock()
        self._xsrf: XsrfManager = XsrfManager(self._client)

    # --- Life-cycle ---
    async def close(self) -> None:
        """
        Closes the HTTP client and resets internal state.

        This method should be called when the application is shutting down
        to properly close the `httpx.AsyncClient` and clear session-related data.

        It performs the following actions:
            - Closes the HTTP client (`_client`) safely.
            - Resets the XSRF token (`_xsrf_token`) to None.
            - Clears the HTTP headers (`_headers`).

        """
        assert self._internal_lock is not None, "_internal_lock not initialized"
        async with self._internal_lock:
            try:
                client = await self.get_client()
                await client.aclose()
            except Exception:
                pass
            self._xsrf_token = None
            self._headers = {}

    def __enter__(self) -> "AsyncEmailnatorClient":
        """
        Enters the runtime context for the singleton instance.

        Returns:
            EmailnatorClientSingleton: The singleton instance itself, 
            allowing usage with the `with` statement.
        """
        return self

    async def __exit__(self, exc_type, exc, tb) -> None:
        """
        Exits the runtime context and cleans up the singleton instance.

        This method is called when exiting a `with` block. It closes the HTTP client
        and resets internal state by delegating to the `close()` method.

        Args:
            exc_type (Optional[Type[BaseException]]): The exception type if an exception
                was raised, else None.
            exc (Optional[BaseException]): The exception instance if an exception
                was raised, else None.
            tb (Optional[TracebackType]): The traceback object if an exception
                was raised, else None.
        """
        logger.debug(
            f"Builders service was closed exception type: {exc_type}, exception: {exc}, traceback: {tb}"
        )
        await self.close()

    # --- Public API ---
    async def get_client(self) -> httpx.AsyncClient:
        """
        Returns the underlying HTTP client for making requests.

        Returns:
            httpx.Client: The `httpx.AsyncClient` instance used by this singleton.
        """
        return self._client

    # --- Delegate to XsrfManager ---
    async def get_xsrf_token(self) -> str:
        assert self._xsrf is not None
        return await self._xsrf.get_token()

    async def get_headers(self) -> dict[str, str]:
        assert self._xsrf is not None
        return await self._xsrf.get_headers()

    async def refresh_token(self) -> None:
        assert self._xsrf is not None
        await self._xsrf.refresh()
