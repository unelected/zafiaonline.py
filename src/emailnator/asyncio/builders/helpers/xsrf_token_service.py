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
XSRF token management module for EmailNator API.

This module provides the `XsrfManager` class, which is responsible for
handling the lifecycle of XSRF authentication tokens used when making
requests to the EmailNator API. It ensures that valid tokens are fetched,
decoded, refreshed, and included in the request headers.

The manager is designed for asynchronous environments and uses an
`asyncio.Lock` to guarantee safe concurrent access to token initialization
and refresh operations.

Typical Usage Example:
    import httpx, asyncio
    from emailnator.security.xsrf_manager import XsrfManager

    async def main():
        async with httpx.AsyncClient() as client:
            manager = XsrfManager(client)
            headers = await manager.get_headers()
            print(headers)

        asyncio.run(main())
"""
import urllib.parse
import httpx
import asyncio

from emailnator.config.config import config


class XsrfManager:
    """
    Manage XSRF token lifecycle for the EmailNator API.

    This class is responsible for securely handling XSRF tokens used in
    requests to the EmailNator API. It provides methods to fetch, decode,
    refresh, and ensure that a valid token and corresponding HTTP headers
    are always available.

    Attributes:
        _client (httpx.AsyncClient): The asynchronous HTTP client used for
            making requests to the EmailNator API.
        _token (str | None): Cached XSRF token. None if not yet initialized.
        _headers (dict[str, str]): Default HTTP headers containing the XSRF
            token and other required metadata.
        _lock (asyncio.Lock): Concurrency lock to ensure thread-safe token
            initialization and refresh operations.
    """
    def __init__(self, client: httpx.AsyncClient) -> None:
        """
        Initialize the token manager.

        Args:
            client (httpx.AsyncClient): An asynchronous HTTP client instance
                used to communicate with the EmailNator API.
        """
        self._client = client
        self._token: str | None = None
        self._headers: dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def _fetch_raw_token(self) -> str | None:
        """
        Fetch the raw XSRF token from the EmailNator API.

        This method sends a GET request to the EmailNator base URL and
        attempts to extract the ``XSRF-TOKEN`` from the response cookies.

        Returns:
            str | None: The raw XSRF token if found in cookies, otherwise ``None``.

        Raises:
            httpx.HTTPStatusError: If the response status code indicates an error.
        """
        response = await self._client.get(config.BASE_URL)
        response.raise_for_status()
        return self._client.cookies.get("XSRF-TOKEN")

    async def _decode(self, raw: str) -> str:
        """
        Decode a raw token string.

        This method URL-decodes the given raw token string.

        Args:
            raw (str): The raw token string to decode.

        Returns:
            str: The decoded token string.
        """
        return urllib.parse.unquote(raw)

    async def ensure_token(self) -> None:
        """
        Ensure that an XSRF authentication token is available.

        If no token is currently stored, this method acquires an asynchronous
        lock to safely initialize it. A raw token is fetched and decoded,
        after which the authentication headers are set up.

        Raises:
            RuntimeError: If the raw token could not be retrieved from cookies.
        """
        if self._token is None:
            async with self._lock:
                if self._token is None:
                    raw: str | None = await self._fetch_raw_token()
                    if not raw:
                        raise RuntimeError("XSRF-TOKEN not found in cookies")
                    self._token = await self._decode(raw)
                    self._headers = {
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                        "X-XSRF-TOKEN": self._token,
                        "DNT": "1",
                        "Referer": config.BASE_URL + "/",
                        "User-Agent": config.USER_AGENT,
                    }

    async def refresh(self) -> None:
        """
        Refresh the XSRF authentication token.

        This method acquires an asynchronous lock to ensure that only one
        refresh operation is performed at a time. It fetches a new raw token,
        decodes it, and updates the internal authentication headers.

        Raises:
            RuntimeError: If the raw token could not be fetched or decoded.
        """
        async with self._lock:
            raw: str | None = await self._fetch_raw_token()
            if not raw:
                raise RuntimeError(
                    "Failed to refresh XSRF-TOKEN: no raw token received."
                )

            self._token = await self._decode(raw)
            if not self._token:
                raise RuntimeError(
                    "Failed to refresh XSRF-TOKEN: decoding returned empty token."
                )

            self._headers["X-XSRF-TOKEN"] = self._token

    async def get_token(self) -> str:
        """
        Retrieve the current authentication token.

        This method ensures that a valid token is available by calling
        `ensure_token()`. If no token is present after validation, an
        error is raised.

        Returns:
            str: The current authentication token.

        Raises:
            RuntimeError: If the token could not be obtained.
        """
        await self.ensure_token()
        if self._token is None:
            raise RuntimeError("Failed to obtain authentication token.")
        return self._token

    async def get_headers(self) -> dict[str, str]:
        """
        Retrieve a copy of the current request headers.

        This method ensures that a valid XSRF token is available before
        returning the headers. The headers are returned as a shallow copy
        to prevent external modifications from affecting the internal state.

        Returns:
            dict[str, str]: A copy of the current request headers.
        """
        await self.ensure_token()
        return self._headers.copy()
