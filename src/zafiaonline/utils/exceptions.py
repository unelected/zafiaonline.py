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
Custom exception classes for Mafia Online client.

This module defines application-specific exceptions used throughout the
Mafia Online WebSocket client codebase. These exceptions allow for precise
handling of login failures, bans, and other client-side error conditions.

Typical usage example:

    from zafiaonline.exceptions import LoginError, BanError

    if not user_logged_in:
        raise LoginError("Invalid credentials")

    if server_response["type"] == "USER_BLOCKED":
        raise BanError(client, server_response, auth)
"""
from typing import Type

from zafiaonline.main import Client


class ListenDataException(Exception):
    """
    Raised when an error occurs while receiving data from the WebSocket
    listener.

    This exception is typically used to indicate unexpected issues during the
    WebSocket message listening process, such as malformed data, timeouts, or
    disconnections that were not handled properly.
    """

    def __init__(self, message: str = "An error occurred while receiving data from "
                               "the listener."):
        super().__init__(message)


class ListenExampleErrorException(Exception):
    """
    Raised for specific test cases or example scenarios involving WebSocket
    listening errors.

    This exception is useful for handling controlled test failures, debugging,
    or identifying particular patterns in received messages that need special
    handling.
    """

    def __init__(self, message: str = "An example listening error occurred."):
        super().__init__(message)

class BanError(Exception):
    """
    Exception raised when a user is banned by the server.

    This error is triggered upon receiving a USER_BLOCKED event from the server,
    indicating the client is no longer allowed to interact due to a violation
    or other reason.

    Attributes:
        client (Client): The client instance associated with the banned user.
        auth (Type | None): Optional authentication object for fallback user data.
        message (str): Explanation of the ban including reason and remaining time.
    """
    def __init__(self, client: "Client", data: dict = {}, auth: Type | None = None):
        """
        Initializes a BanError indicating the client has been banned.

        Constructs a detailed error message based on the ban reason and remaining
        ban duration. Uses client and optional auth information to determine the
        banned username.

        Args:
            client (Client): The client instance representing the banned user.
            data (dict, optional): The server packet containing ban information.
                Must include 'REASON' and 'TIME_SEC_REMAINING' fields.
            auth (Type | None, optional): An optional auth object used to
                supplement or replace client info if needed.

        Raises:
            AttributeError: If required client or auth user attributes are missing.
        """
        from zafiaonline.structures.packet_data_keys import PacketDataKeys


        self.client = client
        self.auth = auth

        # Ensure data is not None before accessing it
        reason: str = data[PacketDataKeys.REASON.value]

        if self.auth is None or self.client is None:
            raise AttributeError
        if not self.auth.user or not self.client.user:
            raise AttributeError
        username = (self.client.user.username or self.auth.user.username or
                    "UnknownUser")
        time: str | int = data[PacketDataKeys.TIME_SEC_REMAINING.value]
        ban_time_seconds: int = int(time)

        ban_time = round(ban_time_seconds / 3600, 1)

        message = (f"{username} have been banned due to {reason}, "
                   f"remaining lockout {ban_time} hours")
        super().__init__(message)

class LoginError(Exception):
    """
    Exception raised when authentication with the server fails.

    This can occur due to invalid credentials, network errors,
    or server-side issues during the login process.
    """
    pass
