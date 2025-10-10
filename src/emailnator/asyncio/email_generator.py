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
Asynchronous email generator module.

This module provides the `AsyncEmailGenerator` class, an asynchronous
wrapper around the Emailnator API for working with temporary email
addresses. It offers methods to:

    - Generate a single temporary email address.
    - Generate multiple temporary email addresses (limited to `"100"`, `"200"`, or `"300"`).
    - Retrieve messages associated with a given email address.

Typical usage example:
    from emailnator.asyncio.email_generator import AsyncEmailGenerator

    async def main():
        generator = AsyncEmailGenerator()
        email = await generator.generate_email()
        messages = await generator.get_messages(email)
        print(email, messages)
"""
import re

from typing import Literal

from emailnator.asyncio.generators import Generators
from emailnator.asyncio.helpers.metaclass import AsyncInitMeta
from emailnator.asyncio.message_getter import MessageGetter


class AsyncEmailGenerator(metaclass=AsyncInitMeta):
    """
    Asynchronous wrapper for generating temporary email addresses
    and retrieving their associated messages.

    This class provides a high-level interface to the Emailnator API
    through asynchronous methods.

    Attributes:
        generators (Generators): 
        - The underlying generator instance used to create email addresses.
        message_getter (MessageGetter): 
        - The instance responsible for retrieving messages linked to emails.
    """
    async def __ainit__(self) -> None:
        """
        Initialize the asynchronous email generator.

        Sets up the required components for generating temporary email
        addresses and retrieving their associated messages.
        """
        self._generators: Generators = await Generators()
        self._message_getter: MessageGetter = await MessageGetter()

    async def generate_email(self) -> str:
        """
        Generate a new email address asynchronously.

        This method requests a new email address from the underlying
        `Generators` instance and returns the first generated address.

        Returns:
            str: A newly generated email address.

        Raises:
            RuntimeError: If the generator fails to return at least one email.
        """
        emails = await self._generators.generate_email()

        if not emails or not isinstance(emails, list):
            raise RuntimeError("Email generator returned no valid addresses.")

        return emails[0]

    async def get_messages(self, email: str) -> list[dict[str, str]]:
        """
        Asynchronously retrieve all messages associated with the given email address.

        This coroutine validates the email address, delegates the retrieval to the
        underlying `MessageGetter` instance, and returns a list of message metadata
        dictionaries.

        Args:
            email (str): The email address for which to fetch messages.

        Returns:
            list[dict[str, str]]: A list of message dictionaries, each typically
            containing keys such as 'messageID', 'from', 'subject', and 'time'.

        Raises:
            ValueError: If the provided email address is invalid or empty.
            RuntimeError: If message retrieval fails or the response is invalid.
        """
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email must be a non-empty string.")

        if not re.match(r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email):
            raise ValueError(f"Invalid email format: {email}")

        return await self._message_getter.get_message_list(email)

    async def get_message(self, email: str, message_id: str) -> str:
        """
        Asynchronously retrieve the full content of a specific email message.

        This coroutine validates its inputs, delegates the retrieval to the
        underlying message getter, and returns the message body as a string
        (typically HTML or plain text).

        Args:
            email (str): The email address associated with the message.
            message_id (str): The unique identifier of the message to fetch.

        Returns:
            str: The content of the message, usually in HTML or plain text format.

        Raises:
            ValueError: If the email or message_id is invalid or empty.
            RuntimeError: If message retrieval fails.
        """
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email must be a non-empty string.")

        if not re.match(r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email):
            raise ValueError(f"Invalid email format: {email}")

        if not isinstance(message_id, str) or not message_id.strip():
            raise ValueError("Message ID must be a non-empty string.")

        return await self._message_getter.get_message(email, message_id)

    async def generate_bulk_emails(
        self,
        emails_number: Literal["100", "200", "300"] = "100"
    ) -> list[str]:
        """
        Generate multiple email addresses asynchronously.

        This method requests a batch of email addresses from the underlying
        `Generators` instance. The number of generated emails is restricted
        to specific supported values.

        Args:
            emails_number (Literal["100", "200", "300"], optional):  
                The number of email addresses to generate.  
                Must be one of: `"100"`, `"200"`, or `"300"`.  
                Defaults to `"100"`.

        Returns:
            list[str]: A list of newly generated email addresses.

        Raises:
            ValueError: If `emails_number` is not one of the supported values.
            RuntimeError: If the generator fails to return a valid list of emails.
        """
        if emails_number not in {"100", "200", "300"}:
            raise ValueError(
                f"Invalid emails_number '{emails_number}'. Must be one of '100', '200', or '300'."
            )

        emails: list[str] = await self._generators.generate_bulk_emails(
            emails_number
        )

        if not isinstance(emails, list) or not all(
            isinstance(e, str) for e in emails
        ):
            raise RuntimeError("Email generator returned invalid data type.")

        if not emails:
            raise RuntimeError("Email generator returned an empty list.")

        return emails

    async def parse_message_from_sender(
        self,
        messages: list[dict[str, str]],
        sender: str,
    ) -> str | None:
        """
        Parses a list of messages and retrieves the messageID of a message sent by a specific sender.

        Args:
            messages (list[dict[str, str]]): List of messages, each being a dictionary with at least 'from' and 'messageID' keys.
            sender (str): Email address or name of the sender to search for. Must be a non-empty string.

        Returns:
            str | None: The messageID if a message from the specified sender is found, otherwise None.

        Raises:
            ValueError: If `messages` is not a list of dicts or if `sender` is invalid.
        """
        if not isinstance(messages, list) or not all(isinstance(m, dict) for m in messages):
            raise ValueError("Messages must be a list of dictionaries.")

        if not sender or not isinstance(sender, str):
            raise ValueError("Sender must be a non-empty string.")

        message = next(
            (msg for msg in messages if msg.get('from') == sender),
            None
        )
        if message:
            message_id = message.get("messageID")
            return message_id
        return None

    async def get_message_from_sender(
            self,
            sender: str,
            email: str
        ) -> str | None:
        """
        Retrieves the full text of the first message sent by a specific sender to a given email.

        Args:
            sender (str): Email address or name of the sender to search for. Must be a non-empty string.
            email (str): The target email address. Must be a non-empty string.

        Returns:
            str | None: The full message text if a message from the specified sender is found, otherwise None.

        Raises:
            ValueError: If `sender` or `email` is invalid.
            RuntimeError: If fetching messages or message text fails.
        """
        if not sender or not isinstance(sender, str):
            raise ValueError("Sender must be a non-empty string.")

        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string.")

        messages = await self.get_messages(email)
        if not isinstance(messages, list) or not all(isinstance(m, dict) for m in messages):
            raise ValueError("get_messages() must return a list of dictionaries.")

        message = next(
            (msg for msg in messages if msg.get('from') == sender),
            None
        )
        if message:
            message_id = message.get("messageID")
            if not message_id:
                return None
            text = await self.get_message(email, message_id)
            return text

        return None
