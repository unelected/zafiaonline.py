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
Provides HTTP client functionality for Zafia and Mafia APIs.

This module defines two main classes for working with external services:
`Http`, a low-level HTTP client that handles headers, authentication, and
request execution; and `HttpWrapper`, a higher-level interface that simplifies
making API calls using the `Http` client.

Typical usage example:

    wrapper = Http()
    response = await wrapper.send_request("get", SomeEndpoint, {"key": "value"})
"""
import base64
import string
import random
import uuid

import aiohttp

from typing import Any
from urllib.parse import urljoin
from aiohttp import ClientError

from zafiaonline.structures.packet_data_keys import Endpoints, ZafiaEndpoints
from zafiaonline.utils.logging_config import logger
from zafiaonline.utils.proxy_store import store
from zafiaonline.structures.enums import HttpsTrafficTypes


class Http:
    """
    HTTP client for Zafia and Mafia services.

    Provides methods to build request URLs and headers (including randomized
    Dalvik User‑Agent and authorization tokens), and to send asynchronous HTTP
    requests via aiohttp with optional proxy support.

    Attributes:
        zafia_url (str): Base URL for the Zafia API.
        mafia_address (str): Hostname for the Mafia service.
        api_mafia_address (str): Subdomain for the Mafia API.
        mafia_url (str): HTTPS URL for the Mafia service.
        api_mafia_url (str): HTTPS URL for the Mafia API.
        zafia_endpoint (ZafiaEndpoints): Currently selected Zafia endpoint.
        zafia_headers (dict): Default headers for Zafia API requests.
        mafia_headers (dict): Default headers for Mafia API requests,
            including a randomized Dalvik User‑Agent.
    """
    def __init__(self) -> None:
        """
        Initializes the HTTP client with proxy and default API settings.

        Sets up base URLs, default headers for both Zafia and Mafia services,
        and stores the proxy configuration for future HTTP requests.
        """
        self.zafia_url: str = "http://185.188.183.144:5000/zafia/"
        self.mafia_address: str = "dottap.com"
        self.api_mafia_address: str = f"api.mafia.{self.mafia_address}"
        self.mafia_url: str = f"https://{self.mafia_address}/"
        self.api_mafia_url: str = f"https://{self.api_mafia_address}/"
        self.zafia_endpoint: ZafiaEndpoints
        self.proxy: str | None = store.get_random_proxy()
        self.zafia_headers: dict = {
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.12.0"
        }
        self.mafia_headers: dict = {
            "Host": self.mafia_address,
            "User-Agent": "okhttp/4.12.0",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    @staticmethod
    def __generate_random_token(length: int = 32) -> str:
        """
        Generates a random lowercase hexadecimal token.

        The token consists of random characters chosen from hexadecimal digits
        (0–9 and a–f). Useful for non-cryptographic identifiers, such as request
        IDs or temporary session tokens.

        Args:
            length (int, optional): The number of characters in the token. Defaults to 32.

        Returns:
            str: A lowercase hexadecimal string of the specified length.

            For example:
                'a9f1b3c7e0d45a67b21d09cf87bc1234'
        """
        return ''.join(
            random.choices(
                string.hexdigits.lower(),
                k = length
            )
        )

    async def mafia_request(
        self,
        url: str,
        method: HttpsTrafficTypes,
        endpoint: Endpoints | str,
        params: dict[str,Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any] | bytes:
        """
        Sends an HTTP request to a specified Mafia API endpoint.

        Constructs the full request URL by joining the base `url` with the
        `endpoint` path, then delegates to `send_request` to perform the HTTP
        operation. Supports GET, POST, PUT, and DELETE methods.

        Args:
            url (str): The base URL of the Mafia API.
            method (HttpsTrafficTypes): HTTP method to use.
            endpoint (Endpoints | str): Enum member representing the API endpoint path.
            params (dict[str, Any], optional): Query parameters or JSON body
                payload for the request. Defaults to None.
            headers (Dict[str, str], optional): Additional HTTP headers to include.
                Defaults to None.

        Returns:
            dict[str, Any] | bytes: Parsed JSON response as a dictionary if the
                server returns JSON; otherwise, raw response bytes.

                For example, when JSON is returned:
                    {'ty': 'siner', 'e': '-7'}

                When binary data is returned:
                    b'\x89PNG\r\n\x1a\n...'
        """
        # TODO: @unelected - add types for dynamic values
        if isinstance(endpoint, Endpoints):
            url = urljoin(url, endpoint.value)
        else:
            url = urljoin(url, endpoint)
        return await self.send_request(
            method,
            url,
            params,
            headers
        )

    def __build_headers(
        self,
        user_id: str,
        headers: dict
    ) -> tuple[str, dict[str, str]]:
        """
        Builds the request URL and HTTP headers based on the user context.

        This method first calls `__create_url` to obtain the request URL and a
        boolean flag indicating whether existing headers should be used. If the
        flag is True, it returns the URL with the original headers unchanged.
        Otherwise, it calls `__create_headers` to augment or override the headers
        with authentication or metadata specific to `user_id`.

        Args:
            user_id (str): Identifier for the current user, used to generate
                authenticated or user-specific headers.
            headers (dict): Existing HTTP headers to include in the request.

        Returns:
            tuple[str, Dict[str, str]]: A tuple containing:

                url (str): The request URL returned by `__create_url`.
                headers (Dict[str, str]): The final HTTP headers for the request.

            For example, if `__create_url` returns
                ("https://api.dottap.com/sign_up", False)
            and `__create_headers(headers, user_id)` returns
                {"Authorization": "Bearer abc123",
                "Content-Type": "application/json"},
            then this method returns:
                ("https://api.dottap.com/sign_up",
                {"Authorization": "Bearer abc123",
                "Content-Type": "application/json"})
        """
        data: tuple[str, bool] | str = self.__create_url()
        if isinstance(data, str):
            headers = self.__create_headers(headers, user_id)
            return data, headers
        url: str = data[0]
        return url, headers

    def __create_url(self) -> tuple[str, bool] | str:
        """
        Builds the full Zafia API request URL and indicates special handling.

        Uses the instance’s `zafia_url` and `zafia_endpoint` to construct the complete
        request URL. If the endpoint is `GET_VERIFICATIONS`, returns a tuple
        containing the URL and a flag indicating that existing headers should be
        preserved. Otherwise, returns just the URL string.

        Returns:
            tuple[str, bool] | str: 
                If `zafia_endpoint` is `GET_VERIFICATIONS`, returns a tuple
                `(url, True)` where `url` is the full request URL.
                Otherwise, returns the `url` string.

                For example:
                    ('http://185.188.183.144:5000/zafia/verify', True)
                or:
                    'http://185.188.183.144:5000/zafia/example'
        """
        url: str = urljoin(self.zafia_url, self.zafia_endpoint.value)
        if self.zafia_endpoint == ZafiaEndpoints.GET_VERIFICATIONS.value:
            return url, True
        return url

    def __create_headers(
            self,
            headers: dict,
            user_id: str
    ) -> dict:
        """
        Adds an Authorization header with a user-specific token.

        Generates a random token and combines it with `user_id` to create an
        authorization credential, then encodes it in Base64 and adds it to the
        provided headers dictionary under the "Authorization" key.

        Args:
            headers (dict): Existing HTTP headers to augment.
            user_id (str): Identifier for the user, used in token generation.

        Returns:
            Dict[str, str]: The updated headers dictionary including the
            "Authorization" header.

            For example, if `user_id` is "user_xxxx" and the generated token is
            "meow", the returned headers might look like:
                {
                    "Content-Type": "application/json",
                    "Authorization": "dXNlcl94eHh4PTo9bWVvdw=="
                }
        """
        token: str = self.__generate_random_token()
        auth_raw: str = f"{user_id}=:={token}"
        auth_token: str = base64.b64encode(auth_raw.encode()).decode()
        headers["Authorization"] = auth_token
        return headers

    def build_zafia_headers(
        self,
        endpoint: ZafiaEndpoints,
        user_id: str = str(uuid.uuid4())
    ) -> tuple[str, dict[str, str]]:
        """
        Prepares the full request URL and headers for a Zafia API call.

        Sets the target endpoint, copies the base headers stored in the instance,
        and delegates to `__build_headers` to generate the final URL and augmented
        headers (including the Authorization token).

        Args:
            endpoint (ZafiaEndpoints): Enum member representing the API endpoint.
            user_id (str, optional): Identifier for the user, used in token
                generation. Defaults to a newly generated UUID4 string.

        Returns:
            tuple[str, Dict[str, str]]: A tuple containing:
                url (str): The full request URL combining `zafia_url` and the
                endpoint path.
                headers (Dict[str, str]): The HTTP headers to use for the request,
                including any authentication fields.

            For example:
                (
                    "http://185.188.183.144:5000/zafia/gt",
                    {
                        "Content-Type": "application/json",
                        "Authorization": "dXNlcl94eHh4PTo9bWVvdw=="
                    }
                )
        """
        headers: dict = self.zafia_headers.copy() 
        self.zafia_endpoint = endpoint
        data: tuple[str, dict] = self.__build_headers(user_id, headers)
        url: str = data[0]
        headers: dict = data[1]
        return url, headers

    def build_mafia_headers(
        self,
        user_id: str = str(uuid.uuid4())
    ) -> dict[str, str]:
        """
        Constructs HTTP headers for Mafia API requests with authorization.

        Copies the instance’s default `mafia_headers` and adds an Authorization
        header generated from the provided `user_id`.

        Args:
            user_id (str, optional): Identifier for the user, used in token
                generation. Defaults to a newly generated UUID4 string.

        Returns:
            Dict[str, str]: A dictionary of HTTP headers including the
            original `mafia_headers` plus the `"Authorization"` header.

            For example:
                {
                    "Content-Type": "application/json",
                    "Authorization": "dXNlcl94eHh4PTo9bWVvdw=="
                }
        """
        headers: dict = self.mafia_headers.copy()
        headers: dict = self.__create_headers(headers, user_id)
        return headers

    def build_api_mafia_headers(
        self,
        user_id: str = str(uuid.uuid4())
    ) -> dict[str, str]:
        """
        Constructs HTTP headers for the Mafia API, including authorization and any future custom headers.

        Starts from the instance’s default `mafia_headers`, injects an Authorization
        header based on the provided `user_id`, and reserves space for additional
        headers to be added as needed.

        Args:
            user_id (str, optional): Identifier for the user, used in token
                generation. Defaults to a newly generated UUID4 string.

        Returns:
            Dict[str, str]: A dictionary of HTTP headers including:
                The original `mafia_headers`
                An `"Authorization"` header with a Base64‑encoded token

            For example:
                {
                    "Content-Type": "application/json",
                    "Authorization": "dXNlcl94eHh4PTo9bWVvdw=="
                }
        """
        #TODO: @unelected - add new headers
        headers: dict = self.mafia_headers.copy()
        headers["Host"] = self.api_mafia_address
        headers: dict = self.__create_headers(headers, user_id)
        return headers

    def _make_session(
            self,
            headers: dict[str, str] | None
    ) -> aiohttp.ClientSession:
        """
        Creates and returns a new aiohttp client session.

        The session is configured with the provided headers and the
        proxy setting defined in the class instance.

        Args:
            headers (dict[str, str] | None): Optional HTTP headers to
                include in all requests made through the session.

        Returns:
            aiohttp.ClientSession: A configured client session ready
            for sending HTTP requests.
        """
        return aiohttp.ClientSession(
            headers=headers,
            proxy=self.proxy
        )

    async def _handle_response(
            self,
            response: aiohttp.ClientResponse,
            url: str
    ) -> dict[str, Any] | bytes:
        """
        Processes an HTTP response and returns parsed data.

        If the response has a JSON content type, it is parsed and returned as
        a dictionary. Otherwise, the raw text is returned inside a dictionary
        with an "error" key, and a warning is logged.

        Args:
            response (aiohttp.ClientResponse): The HTTP response object to process.
            url (str): The request URL, used for logging.

        Returns:
            dict[str, Any] | bytes: Parsed JSON response as a dictionary if content 
            type is JSON, otherwise a dictionary with an "error" key containing the 
            raw response text.
        """
        if response.content_type == 'application/json':
            return await response.json()
        else:
            text: str = await response.text()
            logger.warning(f"Response from {url}: {text}")
            return {"error": text}

    async def _request_post(
        self,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        params: dict[str, Any] | None
    ) -> dict[str, Any] | bytes:
        """
        Executes an HTTP POST request using the given session.

        Sends a JSON payload if provided, then processes the server response.
        Delegates response parsing to `_handle_response`, which automatically
        parses JSON or wraps non-JSON text into a dictionary.

        Args:
            session (aiohttp.ClientSession): The active HTTP client session.
            url (str): The request URL.
            params (dict[str, Any] | None): The JSON payload for the POST request.

        Returns:
            dict[str, Any] | bytes: Parsed JSON response as a dictionary if the 
            response content type is JSON, otherwise a dictionary containing 
            an "error" key with the raw response text.

        Raises:
            aiohttp.ClientError: If a network-related error occurs.
            Exception: For any other unexpected error during request execution.
        """
        return await self._execute_request(session, method, url, json=params)

    @staticmethod
    def to_form(mapping: dict) -> dict:
        if not mapping:
            return {}
        return {
            (key.value if hasattr(key, "value") else key):
            (value.value if hasattr(value, "value") else value)
            for key, value in mapping.items()
        }
    async def _execute_request(
        self,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None
    ) -> dict[str, Any] | bytes:
        """
        Executes an HTTP request and handles errors in a unified way.

        Args:
            session (aiohttp.ClientSession): The active HTTP session.
            method (str): The HTTP method name (e.g., "post", "get").
            url (str): The target request URL.
            json (dict[str, Any] | None): JSON body for requests like POST.
            params (dict[str, Any] | None): Query parameters for requests like GET.

        Returns:
            dict[str, Any] | bytes: Parsed response data.
        """
        try:
            if isinstance(json, dict):
                async with getattr(session, method)(
                    url,
                    data=self.to_form(json)
                ) as response:
                    return await self._handle_response(response, url)
            elif isinstance(params, dict):
                async with getattr(session, method)(
                    url,
                    params=self.to_form(params)
                ) as response:
                    return await self._handle_response(response, url)
            raise RuntimeError("Unknown _execute_request error")
        except ClientError as e:
            logger.error(f"Network error during {method.upper()} {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error {method.upper()} {url}: {e}")
            raise

    async def _request_generic(
        self,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        params: dict[str, Any] | None
    ) -> dict[str, Any] | bytes:
        """
        Executes a generic HTTP request (e.g., GET, PUT, DELETE) using the given session.

        Handles sending the request, processing the response, and logging errors.
        Delegates response parsing to `_handle_response`, which automatically parses
        JSON or returns text content wrapped in a dictionary.

        Args:
            session (aiohttp.ClientSession): The active HTTP client session.
            method (str): The HTTP method name (e.g., "get", "put", "delete").
            url (str): The request URL.
            params (dict[str, Any] | None): Optional query parameters for the request.

        Returns:
            dict[str, Any] | bytes: The parsed JSON response as a dictionary if 
            the response is JSON, or a dictionary containing an "error" key with
            the raw text response otherwise.

        Raises:
            aiohttp.ClientError: If a network-related error occurs.
            Exception: For any other unexpected error during request execution.
        """
        return await self._execute_request(session, method, url, params=params)

    async def send_request(
        self,
        method: HttpsTrafficTypes,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None
    ) -> dict[str, Any] | bytes:
        """
        Sends an HTTP request and returns the parsed response.

        Uses `aiohttp.ClientSession` with the provided headers and proxy settings
        to perform the HTTP operation. Automatically parses JSON responses or
        returns error information for non-JSON content. Logs warnings and errors
        as appropriate.

        Args:
            method (HttpsTrafficTypes): HTTP method to use.
            url (str): The full request URL.
            params (dict[str, Any], optional): Query parameters or JSON payload.
                Defaults to None.
            headers (dict[str, str], optional): HTTP headers to include in the
                request. Defaults to None.

        Returns:
            dict[str, Any] | bytes: If the response content type is JSON, returns
            the parsed JSON as a dictionary. Otherwise, logs a warning and returns
            a dictionary with an `"error"` key containing the response text.

            For example, on a successful JSON response:
                {rs": [{'o': 'ru_6c98005e-aa6e-4886-a3e3-fc1e816fc863',
                'mnp': 18, 'mxp': 21, 'mnl': 1, 'venb': False, 's': 0, 'rs': 2, 
                'sr': [], 'fir': 0, 'tt': '!вики', 'pw': 0, 'pn': 1, 'iinvtd': 0}],
                "ty": "rs"}

            On non-JSON response:
                {"ty": "siner", "e": -1}

        Raises:
            aiohttp.ClientError: If a network-level error occurs during the request.
            Exception: For any other exceptions encountered while sending or
                processing the response.
        """
        async with self._make_session(headers) as session:
            request_method: str = method.value
            if request_method == HttpsTrafficTypes.POST.value:
                return await self._request_post(session, request_method, url, params)
            else:
                return await self._request_generic(session, request_method, url, params)
