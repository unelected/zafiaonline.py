# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 unelected
#
# This file is part of the zafiaonline project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Wrapper for handling HTTP requests to Zafia and Mafia APIs.

This module defines the `HttpWrapper` class, which simplifies authenticated
requests to Zafia and Mafia services. It delegates low-level operations to
the `Http` client while managing headers, and API
endpoints.

Typical usage example:
    http = HttpWrapper()
    response = await http.zafia_request(
        method="get",
        endpoint=ZafiaEndpoints.USER_PROFILE,
        params={"uid": "123456"},
        user_id="123456"
    )
"""
from typing import Any

from zafiaonline.structures.enums import HttpsTrafficTypes
from zafiaonline.transport.http.http_module import Http
from zafiaonline.structures.packet_data_keys import Endpoints, ZafiaEndpoints


class HttpWrapper:
    """
    Facade for the Http client, simplifying API request handling.

    This wrapper encapsulates the `Http` instance, providing a higher‑level
    interface for making Mafia and Zafia API calls.

    Attributes:
        http (Http): The underlying HTTP client.
    """
    def __init__(self) -> None:
        """
        Initializes the HTTP wrapper.

        Creates an internal `Http` client instance.
        """
        self.http = Http()

    async def zafia_request(
        self,
        method: HttpsTrafficTypes,
        endpoint: ZafiaEndpoints,
        params: dict[str, Any],
        user_id: str
    ) -> dict[str, Any] | bytes:
        """
        Sends an authenticated request to the Zafia API.

        Builds the full request URL and headers using `build_zafia_headers`, then
        delegates to the internal `send_request` method to perform the HTTP operation.
        Supports GET, POST, PUT, and DELETE methods.

        Args:
            method (Literal["get", "post", "put", "delete"]): HTTP method to use.
            endpoint (ZafiaEndpoints): Enum member representing the Zafia endpoint path.
            params (dict[str, Any]): Query parameters or JSON body payload for the request.
            user_id (str): Identifier for the user, used to generate the Authorization header.

        Returns:
            Dict[str, Any] | bytes: Parsed JSON response as a dictionary if the server
                returns JSON; otherwise, raw response bytes.

                For example, on JSON success:
                    {"type": "cfs", "status": True

                On non-JSON response:
                    b'\x89PNG\r\n\x1a\n...'

        Raises:
            aiohttp.ClientError: If a network-level error occurs during the request.
            Exception: For any other errors encountered while sending or processing the response.
        """
        data: tuple[str, dict[str, str]] = self.http.build_zafia_headers(
            endpoint,
            user_id
        )
        url: str = data[0]
        headers: dict = data[1]
        return await self.http.send_request(
            method=method,
            url=url,
            params=params,
            headers=headers
        )

    async def mafia_request(
        self,
        method: HttpsTrafficTypes,
        endpoint: Endpoints | str,
        params: dict[str, Any] | None = None
    ) -> dict[str, str] | bytes:
        """
        Sends an authenticated request to the Mafia service.

        Constructs headers via `build_mafia_headers`, then delegates to the internal
        `mafia_request` implementation to perform the HTTP call against the Mafia API URL.

        Args:
            method (Literal["get", "post", "put", "delete"]): HTTP method to use.
            endpoint (Endpoints): Enum member representing the API endpoint path.
            params (dict[str, Any], optional): Query parameters or JSON body payload.
                Defaults to None.

        Returns:
            dict[str, str] | bytes: Parsed JSON response as a dictionary if the
            server returns JSON; otherwise, raw response bytes.

            For example, on JSON success:
                {"uu": {player_data}, "ty": "usi"}

            On non-JSON response:
                b'\x89PNG\r\n\x1a\n...'
        """
        headers: dict[str, str] = self.http.build_mafia_headers()
        return await self.http.mafia_request(
            self.http.mafia_url,
            method,
            endpoint,
            params,
            headers
        )

    async def api_mafia_request(
        self,
        method: HttpsTrafficTypes,
        endpoint: Endpoints,
        params: dict[str, Any] | None = None
    ) -> dict[str, Any] | bytes:
        """
        Sends an authenticated request to the Mafia API.

        Builds the appropriate headers using `build_api_mafia_headers` and delegates
        to `mafia_request` to perform the HTTP operation against the Mafia API URL.

        Args:
        method (Literal["get", "post", "put", "delete"]): HTTP method to use.
        endpoint (Endpoints): Enum member representing the API endpoint path.
        params (dict[str, Any], optional): Query parameters or JSON body payload.
            Defaults to None.

        Returns:
        dict[str, Any] | bytes: Parsed JSON response as a dict if the server
        returns JSON; otherwise, raw response bytes.
        """
        headers: dict[str, str] = self.http.build_api_mafia_headers()
        return await self.http.mafia_request(
            self.http.api_mafia_url,
            method,
            endpoint,
            params,
            headers
        )
