# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 unelected
#
# This file is part of the zafiaonline project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Copies non-callable attributes of a client object onto itself.

This module provides a utility function for copying all non-callable
attributes from a client's `__dict__` back to the client instance.

Intended for use in dynamic or reflective systems where attribute resetting
or propagation is necessary.
"""
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zafiaonline.api_client.user_methods import AuthService


class Helpers:
    def get_user_attributes(self, auth: "AuthService") -> None:
        """
        Reassigns all non-callable attributes from a client's __dict__ to itself.

        Args:
            auth: The client object whose attributes will be reassigned.

        Returns:
            None
        """
        for key, value in auth.__dict__.items():
            if not callable(value):
                setattr(auth, key, value)

    async def send_and_get(
        self,
        send_func,
        get_func,
        request: dict,
        response_key: str,
        extract_key: str | None = None,
        default: Any = None
    ) -> dict:
        """Send a request to the server and retrieve structured data.

        Args:
            send_func (Callable): Async function to send data to the server.
            get_func (Callable): Async function to retrieve data from the server.
            request (dict): The request payload to send.
            response_key (str): The key used to extract the response block.
            extract_key (str | None, optional): Specific key inside the response dict to return.
                If None, the whole dict is returned. Defaults to None.
            default (Any, optional): Default value if no valid response is found. Defaults to None.

        Returns:
            Any: The extracted value, the full dict, or the default if nothing is found.
        """
        await send_func(request)
        data: dict = await get_func(response_key)
        if isinstance(data, dict):
            return data.get(extract_key, data) if extract_key else data
        return default
