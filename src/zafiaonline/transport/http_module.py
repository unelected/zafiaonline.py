# Copyright (C) 2025 unelected
#
# This file is part of the zafiaonline project.
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU Lesser General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>.

"""
Provides HTTP client functionality for Zafia and Mafia APIs.

This module defines two main classes for working with external services:
`Http`, a low-level HTTP client that handles headers, authentication, and
request execution; and `HttpWrapper`, a higher-level interface that simplifies
making API calls using the `Http` client.

Typical usage example:

    wrapper = HttpWrapper(proxy="http://127.0.0.1:8080")
    response = await wrapper.api_mafia_request("get", SomeEndpoint, {"key": "value"})
"""


import base64
import string
import random
import uuid

import aiohttp

from typing import Any, Dict, Literal
from urllib.parse import urljoin
from aiohttp import ClientError

from zafiaonline.structures.packet_data_keys import Endpoints, ZafiaEndpoints
from zafiaonline.utils.logging_config import logger


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
        proxy (str | None): Proxy URL to use for HTTP sessions.
        zafia_headers (dict): Default headers for Zafia API requests.
        mafia_headers (dict): Default headers for Mafia API requests,
            including a randomized Dalvik User‑Agent.
    """
    def __init__(self, proxy):
        """
        Initializes the HTTP client with proxy and default API settings.

        Sets up base URLs, default headers for both Zafia and Mafia services,
        and stores the proxy configuration for future HTTP requests.

        Args:
        proxy (str | None): Proxy URL to use for all HTTP sessions. If None,
            no proxy will be applied.
        """
        self.zafia_url: str = "http://185.188.183.144:5000/zafia/"
        self.mafia_address: str = "dottap.com"
        self.api_mafia_address: str = f"api.mafia.{self.mafia_address}"
        self.mafia_url: str = f"https://{self.mafia_address}/"
        self.api_mafia_url: str = f"https://{self.api_mafia_address}/"
        self.zafia_endpoint: ZafiaEndpoints
        self.proxy: str | None = proxy
        self.zafia_headers: dict = {
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.12.0"
        }
        self.mafia_headers: dict = {
            "HOST": self.mafia_address,
            "User-Agent": self.generate_dalvik_ua(),
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

    @staticmethod
    def generate_dalvik_ua() -> str:
        """
        Generates a randomized Dalvik user‑agent string for Android emulation.

        This function constructs a realistic Dalvik user‑agent header by randomly
        selecting a Dalvik runtime version, Android OS version, device model, and
        build number from predefined lists.

        Returns:
            str: A Dalvik user‑agent string suitable for HTTP requests.

            For example:
                'Dalvik/2.1.0 (Linux; U; Android 10; Pixel 4 XL Build/QP1A.190711.020)'
        """
        dalvik_versions: list = ["1.6.0", "2.1.0"]
        android_versions: list = ["5.1.1", "6.0", "7.0", "8.1.0", "9", "10", "11", "12"]
        devices: list = [
            "Pixel 3", "Pixel 4 XL", "Samsung SM-G960F", "OnePlus A6013",
            "Huawei P30", "Xiaomi Mi 9", "Moto G7", "Nexus 5X"
        ]
        builds: list = [
            "LMY47D", "NRD90M", "OPM1.171019.011", "QP1A.190711.020",
            "RP1A.200720.012", "SP1A.210812.015"
        ]

        dalvik_ver: str = random.choice(dalvik_versions)
        android_ver: str = random.choice(android_versions)
        device: str = random.choice(devices)
        build: str = random.choice(builds)
        return f"Dalvik/{dalvik_ver} (Linux; U; Android {android_ver}; {device} Build/{build})"

    def generate_agent(self) -> str:
        """
        Returns a randomized Dalvik user-agent string.

        Delegates to `generate_dalvik_ua` to produce a realistic Android user-agent
        header in Dalvik format.

        Returns:
            str: A Dalvik user-agent string constructed by the internal helper.

            For example:
                'Dalvik/2.1.0 (Linux; U; Android 10; Pixel 4 XL Build/QP1A.190711.020)'
        """
        user_agent: str = self.generate_dalvik_ua() 
        return user_agent

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
        return ''.join(random.choices(string.hexdigits.lower(), k = length))

    async def mafia_request(self, url: str, method: Literal["get", "post", "put",
                            "delete"], endpoint: Endpoints,
                            params: dict[str,Any] | None = None,
                            headers: Dict[str, str] | None = None,
                            ) -> dict[str, Any] | bytes:
        """
        Sends an HTTP request to a specified Mafia API endpoint.

        Constructs the full request URL by joining the base `url` with the
        `endpoint` path, then delegates to `send_request` to perform the HTTP
        operation. Supports GET, POST, PUT, and DELETE methods.

        Args:
            url (str): The base URL of the Mafia API.
            method (Literal["get", "post", "put", "delete"]): HTTP method to use.
            endpoint (Endpoints): Enum member representing the API endpoint path.
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
        url = urljoin(url, endpoint.value)
        return await self.send_request(method, url, params, headers)

    def __build_headers(self, user_id:
                        str, headers: dict) -> tuple[str, Dict[str, str]]:
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
        print(url)
        if self.zafia_endpoint == ZafiaEndpoints.GET_VERIFICATIONS.value:
            return url, True
        return url

    def __create_headers(self, headers: dict, user_id: str) -> Dict:
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

    def build_zafia_headers(self, endpoint: ZafiaEndpoints, user_id:
            str = str(uuid.uuid4())) -> tuple[str, Dict[str, str]]:
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

    def build_mafia_headers(self, user_id:
                            str = str(uuid.uuid4())) -> Dict[str, str]:
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

    def build_api_mafia_headers(self, user_id:
                                str = str(uuid.uuid4())) -> Dict[str, str]:
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
        headers: dict = self.__create_headers(headers, user_id)
        return headers

    async def send_request(self, method: Literal["get", "post", "put", "delete"],
                           url: str, params: dict[str, Any] | None = None,
                           headers: dict[str, str] | None = None
                           ) -> dict[str, Any] | bytes:
        """
        Sends an HTTP request and returns the parsed response.

        Uses `aiohttp.ClientSession` with the provided headers and proxy settings
        to perform the HTTP operation. Automatically parses JSON responses or
        returns error information for non-JSON content. Logs warnings and errors
        as appropriate.

        Args:
            method (Literal["get", "post", "put", "delete"]): HTTP method to use.
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
        async with aiohttp.ClientSession(headers = headers, proxy = self.proxy) as session:
            try:
                async with await getattr(session, method)(url, params = params) as response:
                    if response.content_type == 'application/json':
                        data: dict = await response.json()
                    else:
                        text: str = await response.text()
                        logger.warning(f"Response from {url}: {text}")
                        data: dict = {'error': text}
                    return data
            except ClientError as e:
                logger.error(
                    f"Network error during {method.upper()} request to"
                    f" {url}: {e}")
                raise
            except Exception as e:
                logger.error(f"Error {method.upper()} {url}: {e}")
                raise


class HttpWrapper:
    """
    Facade for the Http client, simplifying API request handling.

    This wrapper encapsulates the `Http` instance, providing a higher‑level
    interface for making Mafia and Zafia API calls without dealing directly
    with proxy configuration or header construction.

    Attributes:
        http (Http): The underlying HTTP client configured with the optional proxy.
    """
    def __init__(self, proxy: str | None = None):
        """
        Initializes the HTTP wrapper with an optional proxy.

        Creates an internal `Http` client instance using the given proxy
        settings, which will be used for all subsequent API requests.

        Args:
            proxy (str | None): Proxy URL to apply to the underlying HTTP client.
                If None, requests will be made without a proxy.
        """
        self.http = Http(proxy = proxy)

    async def zafia_request(self, method:
                            Literal["get", "post", "put", "delete"],
                            endpoint: ZafiaEndpoints, params: dict[str, Any],
                            user_id: str) -> Dict[str, Any] | bytes:
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
        data: tuple[str, dict[str, str]] = self.http.build_zafia_headers(endpoint, user_id)
        url: str = data[0]
        headers: dict = data[1]
        print(url, headers)
        return await self.http.send_request(method = method, url = url,
                                params = params, headers = headers)

    async def mafia_request(self, method: Literal["get", "post", "put",
                            "delete"], endpoint: Endpoints,
                            params: dict[str, Any] | None = None) -> dict[str, str] | bytes:
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
        headers: Dict[str, str] = self.http.build_mafia_headers()
        return await (self.http.mafia_request(
            self.http.mafia_url, method, endpoint, params, headers))

    async def api_mafia_request(self, method: Literal["get", "post", "put",
                            "delete"], endpoint: Endpoints,
                            params: dict[str, Any] | None = None,) -> dict[str, Any] | bytes:
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
        headers: Dict[str, str] = self.http.build_api_mafia_headers()
        return await (self.http.mafia_request(
            self.http.api_mafia_url, method, endpoint, params, headers))
