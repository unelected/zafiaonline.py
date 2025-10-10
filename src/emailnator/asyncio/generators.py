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
EmailNator API Client

This module provides a wrapper around the EmailNator API, facilitating the
generation of single or bulk email addresses. It includes utility functions
for handling HTTP requests and parsing JSON responses.


Typical Usage Example:
    from emailnator_client import Generators
    generator = Generators()
    await generator.generate_email()
    ['example@gmail.com']
    await generator.generate_bulk_emails(
        options=['dotGmail', 'plusGmail'], '5'
    )
    ['example1@gmail.com', 'example2@gmail.com', 'example3@gmail.com', 'example4@gmail.com', 'example5@gmail.com']
"""
import httpx

from typing import Literal

from emailnator.asyncio.helpers.metaclass import AsyncInitMeta
from emailnator.config.config import config
from emailnator.asyncio.helpers.parser import Parser
from emailnator.asyncio.builders.builders import AsyncEmailnatorClient


class Generators(metaclass=AsyncInitMeta):
    """
    Wrapper for interacting with the EmailNator API to generate emails.

    This class provides methods for generating single or multiple email
    addresses using the EmailNator API. It manages the HTTP client, default
    headers, and helper functions for parsing API responses.

    Attributes:
        parser (Parser): Parser for processing data.
        client (httpx.AsyncClient): Asynchronous HTTP client.
        headers (dict): HTTP headers for requests.
    """
    async def __ainit__(self) -> None:
        """
        Initializes the asynchronous instance.

        This method performs asynchronous setup of dependencies:
        creates a parser, initializes the asynchronous Emailnator client,
        and configures HTTP headers.

        Returns:
            None: This method does not return a value.
        """
        self.parser: Parser = Parser()
        emailnator_client: AsyncEmailnatorClient = (
            await AsyncEmailnatorClient()
        )
        self.client: httpx.AsyncClient = await emailnator_client.get_client()
        self.headers: dict = await emailnator_client.get_headers()

    async def generate_email(
        self,
        options: list[str] = config.GMAIL_CONFIG,
        base_url: str = config.BASE_URL,
    ) -> list[str]:
        """
        Generate a single email address via the API.

        Sends a POST request to the `/generate-email` endpoint with default
        Gmail options (from `config.GMAIL_CONFIG`). Uses `parse_json_response`
        to validate the response and return the parsed JSON.

        Args:
            options (list[str]): A list of options to customize email generation.
            base_url (str, optional): Base URL of the API. Defaults to `config.BASE_URL`.

        Returns:
            list[str]: A writed JSON response containing the generated email.

        Raises:
            RuntimeError: If the API response indicates an error (status != 200) 
                        or if the response is not valid JSON.
        """
        email_key: str = "email"
        generation_endpoint: str = "/generate-email"
        assert self.client is not None, "No client"
        response: httpx.Response = await self.client.post(
            base_url + generation_endpoint,
            headers=self.headers,
            json={email_key: options}
        )
        assert self.parser is not None, "No helpers"
        return await self.parser.parse_email_response(
            response,
            "generate-email"
        )

    async def generate_bulk_emails(
        self,
        emails_number: Literal["100", "200", "300"] = "100",
        options: list[str] = config.GMAIL_CONFIG,
        base_url: str = config.BASE_URL
    ) -> list[str]:
        """
        Generate multiple email addresses via the API.

        Sends a POST request to the `/generate-email` endpoint with the provided
        options and the number of emails to generate. Uses `parse_json_response`
        to validate the response and return the parsed JSON.

        Args:
            emails_number (Literal["100", "200", "300"], optional): Number of emails to generate. Defaults to "100".
            options (list[str]): A list of options to customize email generation.
            base_url (str, optional): Base URL of the API. Defaults to `config.BASE_URL`.

        Returns:
            list[str]: A writed JSON response containing generated emails.

        Raises:
            RuntimeError: If the API response indicates an error or is not valid JSON.
        """
        email_key: str = "email"
        email_number_key: str = "emailNo"
        generation_endpoint: str = "/generate-email"
        assert self.client is not None, "No client"
        response: httpx.Response = await self.client.post(
            base_url + generation_endpoint,
            headers=self.headers,
            json={
                email_key: options,
                email_number_key: emails_number
            }
        )
        assert self.parser is not None, "No helpers"
        return await self.parser.parse_email_response(
            response,
            "generate-email"
        )
