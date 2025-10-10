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
Utility functions for Gmail configuration formatting.

This module provides helper functions for normalizing and formatting
configuration values related to Gmail integration. It ensures that
values are consistently represented as lists of strings, which is
useful for downstream processing in account generation.

Typical usage example:
    from emailnator.config.helpers import format_gmail_config

    config = format_gmail_config("test@example.com")
    print(config)  # ["test@example.com"]

    config = format_gmail_config(["a@gmail.com", "b@gmail.com"])
    print(config)  # ["a@gmail.com", "b@gmail.com"]
"""
from typing import Any


def format_gmail_config(value: Any) -> list:
    """
    Format a value into a list of Gmail configuration strings.

    Args:
        value (Any): Input value that can either be a list of strings
            or a single value convertible to a string.

    Returns:
        List[str]: A list containing the Gmail configuration strings.
    """
    if isinstance(value, list):
        gmail_config: list = value
    else:
        gmail_config: list = [str(value)]

    return gmail_config

