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
Module for interacting with the EmailNator API to retrieve email messages.

This module provides the `MessageGetter` class, which is a wrapper around the
EmailNator API for fetching email messages. It uses an HTTP client from `httpx`
and helper utilities from `Helpers` to parse API responses.
"""
import httpx

from emailnator.config.config import config
from emailnator.asyncio.helpers.parser import Parser
from emailnator.asyncio.builders.builders import AsyncEmailnatorClient
from emailnator.asyncio.helpers.metaclass import AsyncInitMeta


class MessageGetter(metaclass=AsyncInitMeta):
    """
    Asynchronous client wrapper for retrieving messages from the EmailNator API.

    This class provides functionality to fetch the list of messages associated
    with a given email address and parse the results using the `Parser` utility.

    Attributes:
        parser (Parser): Parser instance used to process API responses.
        client (httpx.AsyncClient): Asynchronous HTTP client for making requests
            to the EmailNator API.
        headers (dict[str, str]): Default HTTP headers applied to all requests.
    """
    async def __ainit__(self) -> None:
        """
        Asynchronous initializer for the MessageGetter.

        This method initializes the HTTP client, request headers, and parser
        required for interacting with the EmailNator API.
        """
        emailnator_client: AsyncEmailnatorClient = (
            await AsyncEmailnatorClient()
        )
        self.parser: Parser = Parser()
        self.client: httpx.AsyncClient = await emailnator_client.get_client()
        self.headers: dict = await emailnator_client.get_headers()

    async def get_message_list(
        self,
        email: str,
        base_url: str = config.BASE_URL,
    ) -> list[dict[str, str]]:
        """
        Asynchronously retrieve a list of messages associated with the given email address.

        This coroutine sends a POST request to the `/message-list` endpoint to fetch
        metadata about messages linked to the specified email. The result is parsed
        and returned as a list of message dictionaries.

        Args:
            email (str): The email address for which to fetch the message list.
            base_url (str, optional): The base URL of the API. Defaults to `config.BASE_URL`.

        Returns:
            list[dict[str, str]]: A list of message metadata dictionaries. Each dictionary
            typically contains keys such as 'messageID', 'from', 'subject', and 'time'.

        Raises:
            AssertionError: If the HTTP client (`self.client`) is not initialized.
            httpx.RequestError: If a network-related error occurs.
            httpx.HTTPStatusError: If the HTTP response indicates a failed request.
            RuntimeError: If the response cannot be parsed or is missing expected data.
        """
        get_messages_endpoint: str = "/message-list"
        final_url: str = base_url + get_messages_endpoint

        assert self.client is not None, "No client"
        response: httpx.Response = await self.client.post(
            final_url,
            headers=self.headers,
            json={"email": email}
        )
        return await self.parser.parse_message_response(response, "message-list")

    async def get_message(
        self,
        email: str,
        message_id: str,
        base_url: str = config.BASE_URL,
    ) -> str:
        """
        Asynchronously retrieve the full content of a specific email message from the API.

        This coroutine sends a POST request to the `/message-list` endpoint with the
        given email and message ID, and returns the raw response text (typically the
        HTML content of the message).

        Args:
            email (str): The email address from which to retrieve the message.
            message_id (str): The unique identifier of the message to fetch.
            base_url (str, optional): The base URL of the API. Defaults to `config.BASE_URL`.

        Returns:
            str: The raw message content as returned by the server (usually HTML).

        Raises:
            AssertionError: If the HTTP client (`self.client`) is not initialized.
            httpx.RequestError: If there is a network or connection issue.
            httpx.HTTPStatusError: If the response status code indicates an error.
        """
        get_messages_endpoint: str = "/message-list"
        final_url: str = base_url + get_messages_endpoint

        assert self.client is not None, "No client"
        response: httpx.Response = await self.client.post(
            final_url,
            headers=self.headers,
            json={
                "email": email,
                "messageID": message_id
            }
        )
        return response.text
