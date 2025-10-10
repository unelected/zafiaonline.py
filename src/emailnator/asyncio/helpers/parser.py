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
Utility helper functions used across the project.

This module provides stateless helper functions for general use. Currently,
it exposes the `Parser` class with static methods to simplify common tasks,
such as parsing HTTP responses safely as JSON.

Typical Usage Example:
    import httpx
    from helpers import Helpers
    resp = httpx.Response(200, content=b'{"key": ["value"]}')
    Helpers.parse_email_response(resp, "get-items")
    ['value']
"""
import httpx

from typing import Any


class Parser:
    """
    Utility helpers used across the project.

    A small container for stateless helper functions. Currently this class
    exposes a static method `parse_json_response` that validates an httpx
    response and returns its JSON payload, raising a `RuntimeError` for
    HTTP errors (status >= 400) or invalid JSON.

    Attributes:
        None
    """
    @staticmethod
    async def parse_email_response(
        response: httpx.Response,
        context: str
    ) -> list[str]:
        """
        Parse and extract email addresses from an HTTP JSON response.

        This coroutine validates the HTTP response and attempts to parse its content
        as JSON. It expects the JSON to contain an "email" field, which should be a
        list of strings (email addresses).

        Args:
            response (httpx.Response): The HTTP response object to parse.
            context (str): A short description of the request context, used for
                more informative error messages.

        Returns:
            list[str]: A list of email addresses extracted from the response.

        Raises:
            RuntimeError: If the response status code is 400 or higher.
            RuntimeError: If the response content is not valid JSON.
            RuntimeError: If the "email" field is missing or not a list of strings.
        """
        if response.status_code >= 400:
            raise RuntimeError(f"{context} returned {response.status_code}: {response.text}")

        try:
            data: Any = response.json()
        except ValueError:
            raise RuntimeError(f"{context} response is not valid JSON: {response.text[:400]}")

        emails = data.get("email")

        if isinstance(emails, str):
            return [emails]
        if isinstance(emails, list) and all(isinstance(e, str) for e in emails):
            return emails

        raise RuntimeError(f"{context} response does not contain valid 'email' data: {response.text[:400]}")

    @staticmethod
    async def parse_message_response(
        response: httpx.Response,
        context: str
    ) -> list[dict[str, str]]:
        """
        Parse and validate a message list response from the API.

        This coroutine checks the HTTP response for errors and attempts to parse its
        content as JSON. It extracts the "messageData" field, which is expected to
        contain a list of message objects.

        Args:
            response (httpx.Response): The HTTP response object to parse.
            context (str): Description of the request context, used in error messages.

        Returns:
            list[dict[str, str]]: A list of message dictionaries parsed from the response.

        Raises:
            RuntimeError: If the response has a status code >= 400.
            RuntimeError: If the response body is not valid JSON.
            RuntimeError: If the JSON structure does not contain a valid "messageData" list.
        """
        if response.status_code >= 400:
            raise RuntimeError(f"{context} returned {response.status_code}: {response.text}")

        try:
            data: Any = response.json()
        except ValueError:
            raise RuntimeError(f"{context} response is not valid JSON: {response.text[:400]}")

        message_data = data.get("messageData")

        if not isinstance(message_data, list) or not all(isinstance(m, dict) for m in message_data):
            raise RuntimeError(f"{context} response does not contain valid 'messageData': {response.text[:400]}")

        return message_data
