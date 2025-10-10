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
Synchronous interface for the Emailnator API wrapper.

This module defines the `EmailGenerator` class, which provides a blocking
(synchronous) wrapper around the asynchronous `AsyncEmailGenerator`.  
It allows generating temporary email addresses and retrieving their messages
without requiring an asynchronous runtime.

Typical Usage example:
    from emailnator.sync.email_generator import EmailGenerator
    gen = EmailGenerator()
    email = gen.generate_email()
    print(email)
    messages = gen.get_messages(email)
    print(messages)
    bulk = gen.generate_bulk_emails("200")
    print(bulk)
"""
import asyncio
import re

from typing import Literal

from emailnator.asyncio.email_generator import AsyncEmailGenerator


class EmailGenerator:
    """
    Synchronous wrapper for generating temporary email addresses
    and retrieving their associated messages.

    This class provides a blocking interface to the asynchronous
    `AsyncEmailGenerator`, making it convenient to use in codebases
    that are not async-aware.

    Attributes:
        _loop (asyncio.AbstractEventLoop):
            Event loop used to execute asynchronous operations
            in a synchronous context.
        _async (AsyncEmailGenerator):
            Internal asynchronous generator instance responsible for
            performing the actual operations.
    """
    def __init__(self) -> None:
        """
        Initialize the synchronous email generator.

        This sets up an internal instance of `AsyncEmailGenerator`
        to handle the underlying asynchronous operations, which are
        then exposed through synchronous wrappers.
        """
        try:
            self._loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop: asyncio.AbstractEventLoop= asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        self._async: AsyncEmailGenerator = self._loop.run_until_complete(
            AsyncEmailGenerator()
        )

    def generate_email(self) -> str:
        """
        Generate a new email address synchronously.

        This method runs the asynchronous `generate_email` coroutine from
        `AsyncEmailGenerator` in a blocking manner using the event loop.

        Returns:
            str: A newly generated email address.

        Raises:
            RuntimeError: If the underlying async generator fails to return
            a valid email address.
        """
        email = self._loop.run_until_complete(self._async.generate_email())

        if not isinstance(email, str) or not email.strip():
            raise RuntimeError(
                "Email generator returned invalid or empty data."
            )

        if "@" not in email or "." not in email.split("@")[-1]:
            raise RuntimeError(f"Invalid email format returned: {email!r}")

        return email

    def get_messages(self, email: str) -> list[dict[str, str]]:
        """
        Retrieve messages for a given email address synchronously.

        This method executes the asynchronous `get_messages` coroutine from
        `AsyncEmailGenerator` in a blocking manner using the event loop.

        Args:
            email (str): The email address to fetch messages for.

        Returns:
            list[dict[str, str]]: A list of message objects, where each message is
                represented as a dictionary containing fields such as 'messageID',
                'from', 'subject', and 'time'.

        Raises:
            ValueError: If the provided email is invalid.
            RuntimeError: If message retrieval fails or the response is invalid.
        """
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email must be a non-empty string.")

        if not re.match(r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email):
            raise ValueError(f"Invalid email format: {email}")

        messages: list[dict[str, str]] = self._loop.run_until_complete(
            self._async.get_messages(
                email
            )
        )

        if not isinstance(messages, list):
            raise RuntimeError(
                "Message getter returned invalid data type (expected list)."
            )

        if not all(isinstance(m, dict) for m in messages):
            raise RuntimeError(
                "Message getter returned a list with non-dict elements."
            )

        expected_keys: set = {"messageID", "from", "subject", "time"}
        for msg in messages:
            if not expected_keys.issubset(msg.keys()):
                raise RuntimeError(
                    f"Message object missing required fields: {msg}"
                )

        return messages

    def get_message_from_sender(
            self,
            sender: str,
            email: str
    ) -> str | None:
        """
        Retrieves the message content from a specific sender for the given email address.

        Args:
            sender (str): The email address or name of the sender. Must be a non-empty string.
            email (str): The target email address to fetch the message for. Must be a valid email format.

        Returns:
            str | None: The message content if found, otherwise None.

        Raises:
            ValueError: If `sender` or `email` are invalid.
            RuntimeError: If the asynchronous client is not initialized or an error occurs while fetching the message.
        """
        if not sender or not isinstance(sender, str):
            raise ValueError("Sender must be a non-empty string.")

        email_regex = r"^[^@]+@[^@]+\.[^@]+$"
        if not email or not isinstance(
            email,
            str
        ) or not re.match(email_regex, email):
            raise ValueError("Email must be a valid email address.")

        message = self._loop.run_until_complete(
            self._async.get_message_from_sender(
                sender,
                email
            )
        )
        return message

    def parse_message_from_sender(
            self,
            messages: list[dict[str, str]],
            sender: str
    ) -> str | None:
        """
        Parses a list of messages and retrieves the content of the message sent by a specific sender.

        Args:
            messages (list[dict[str, str]]): A list of messages, where each message is a dictionary
                                            containing keys like 'from', 'subject', 'time', etc.
            sender (str): The email address or name of the sender to search for. Must be a non-empty string.

        Returns:
            str | None: The message content if a message from the specified sender is found, otherwise None.

        Raises:
            ValueError: If `messages` is empty or not a list of dictionaries, or if `sender` is invalid.
            RuntimeError: If the asynchronous client is not initialized or an error occurs during parsing.
        """
        # Validation
        if not isinstance(
            messages,
            list
        ) or not all(isinstance(m, dict) for m in messages):
            raise ValueError("Messages must be a list of dictionaries.")

        if not sender or not isinstance(sender, str):
            raise ValueError("Sender must be a non-empty string.")

        message = self._loop.run_until_complete(
            self._async.parse_message_from_sender(
                messages,
                sender,
            )
        )
        return message

    def get_message(self, email: str, message_id: str) -> str:
        """
        Retrieve a specific message for the given email synchronously.

        This method runs the asynchronous `get_message` coroutine in the current
        event loop and returns its result as a string (typically the message HTML
        or raw text).

        Args:
            email (str): The email address from which to retrieve the message.
            message_id (str): The unique identifier of the message to fetch.

        Returns:
            str: The message content, usually in HTML or plain text format.

        Raises:
            ValueError: If `email` or `message_id` are invalid or empty.
            RuntimeError: If the retrieved message is invalid or empty.
        """
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email must be a non-empty string.")

        if not re.match(r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email):
            raise ValueError(f"Invalid email format: {email}")

        if not isinstance(message_id, str) or not message_id.strip():
            raise ValueError("Message ID must be a non-empty string.")

        message_content: str = self._loop.run_until_complete(
            self._async.get_message(email, message_id)
        )

        if not isinstance(message_content, str):
            raise RuntimeError(
                "Message getter returned invalid data type (expected str)."
            )

        if not message_content.strip():
            raise RuntimeError("Message getter returned an empty message.")

        return message_content

    def generate_bulk_emails(
        self,
        emails_number: Literal["100", "200", "300"] = "100"
    ) -> list[str]:
        """
        Generate multiple email addresses synchronously.

        This method runs the asynchronous `generate_bulk_emails` coroutine from
        `AsyncEmailGenerator` in a blocking manner using the event loop.

        Args:
            emails_number (Literal["100", "200", "300"], optional):  
                The number of email addresses to generate.  
                Must be one of: `"100"`, `"200"`, or `"300"`.  
                Defaults to `"100"`.

        Returns:
            list[str]: A list of newly generated email addresses.

        Raises:
            ValueError: If `emails_number` is invalid.
            RuntimeError: If the async generator returns invalid or empty data.
        """
        if emails_number not in {"100", "200", "300"}:
            raise ValueError(
                f"Invalid emails_number '{emails_number}'. Must be one of '100', '200', or '300'."
            )

        emails: list = self._loop.run_until_complete(
            self._async.generate_bulk_emails(emails_number)
        )

        if not isinstance(emails, list):
            raise RuntimeError(
                "Email generator returned invalid data type (expected list)."
            )

        if not emails:
            raise RuntimeError("Email generator returned an empty list.")

        if not all(isinstance(e, str) and e.strip() for e in emails):
            raise RuntimeError(
                "Email generator returned a list with invalid email strings."
            )

        return emails
