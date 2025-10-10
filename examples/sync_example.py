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
Example usage of the synchronous EmailGenerator.

This script demonstrates how to:
    1. Initialize the synchronous `EmailGenerator`.
    2. Generate a new temporary email address.
    3. Retrieve messages associated with the generated email.
    4. Print the generated email and its messages.

Typical output:
    Generated: example.email@domain.com
    Messages: ['Welcome to service!', 'Your verification code is 123456']
"""

from emailnator.sync.email_generator import EmailGenerator

generator: EmailGenerator = EmailGenerator()
email: str = generator.generate_email()
messages: list[dict[str, str]] = generator.get_messages(email)
print("Generated:", email)
print("Messages:", messages)
needed_message = messages[0]
message_id = needed_message["messageID"]
print(message_id)
message = generator.get_message(email, message_id)
print(message)
print("Don't worry, if message is 'Server Error' that's normal")
