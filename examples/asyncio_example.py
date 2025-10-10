# Copyright (C) 2025 unelected
#
# This file is part of account_generator.
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
Example usage of the asynchronous AsyncEmailGenerator.

This script demonstrates how to:
    1. Initialize the asynchronous `AsyncEmailGenerator`.
    2. Generate a new temporary email address asynchronously.
    3. Retrieve messages associated with the generated email.
    4. Print the generated email and its messages.

Typical usage:
    $ python async_example.py

Typical output:
    Email: example.email@domain.com
    Messages: ['Welcome!', 'Your verification code is 123456']
"""
import asyncio

from emailnator.asyncio.email_generator import AsyncEmailGenerator


async def generate_email_and_get_messages():
    """
    Generate a new email and retrieve its messages asynchronously.

    This coroutine demonstrates the usage of `AsyncEmailGenerator` by:
    1. Creating a temporary email address.
    2. Fetching messages associated with that address.
    3. Retrieving the full content of the first message.

    Returns:
        dict: A dictionary containing the generated email, the message list,
              and the full text of the first message (if available).
    """
    generator: AsyncEmailGenerator = await AsyncEmailGenerator()
    email: str = await generator.generate_email()
    messages: list[dict] = await generator.get_messages(email)
    print(f"Email: {email}\n Messages: {messages}")
    needed_message_id = await generator.parse_message_from_sender(messages, "AI TOOLS")
    print(needed_message_id)
    if needed_message_id:
        message = await generator.get_message(email, needed_message_id)
        print(message)
        print("Don't worry, if message is 'Server Error' that's normal")

if __name__ == "__main__":
    asyncio.run(generate_email_and_get_messages())
