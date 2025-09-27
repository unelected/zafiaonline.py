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
Handles interaction with the global chat system for authenticated clients.

This module defines the GlobalChatMethods class, which allows clients to join
and leave the global chat, send messages, and perform basic anti-spam
handling. It is designed to be used as part of a WebSocket-based client
for MafiaOnline or similar real-time systems.

Typical usage example:

    auth = Auth(...)
    chat = GlobalChatMethods(auth)
    await chat.join_global_chat()
    await chat.send_message_global("Hello everyone!")
    await chat.leave_from_global_chat()
"""
import asyncio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zafiaonline.api_client.user_methods import AuthService
from zafiaonline.structures import PacketDataKeys
from zafiaonline.utils.utils import Helpers
from zafiaonline.structures.enums import MessageStyles
from zafiaonline.utils.utils_for_send_messages import Utils, SentMessages


class GlobalChatMethods:
    """
    Handles global chat interactions for an authenticated user.

    This class manages the global chat functionality using an authenticated
    client session. It initializes user-related state and tracks messages
    sent during the session.

    Attributes:
        auth_client: An authenticated API client instance used for user operations.
        sent_messages: A SentMessages instance used to track sent messages.
    """
    def __init__(self, auth_client: "AuthService") -> None:
        """
        Initializes GlobalChat with the provided authenticated client.

        Args:
            auth_client: An authenticated API client used to perform user-related actions.
        """
        self.auth_client: "AuthService" = auth_client
        if self.auth_client:
            helpers: "Helpers" = Helpers()
            helpers.get_user_attributes(self.auth_client)
        self.sent_messages: "SentMessages" = SentMessages()

    async def send_server(
        self,
        data: dict,
        remove_token_from_object: bool = False
    ) -> None:
        """
        Sends data to the server through the authenticated client.

        This method forwards the given data to the server using the client's
        `send_server` method. Optionally removes token-related information
        from the data before sending.

        Args:
            data: The dict data object to be sent to the server. Can be of any type
                supported by the underlying client method.
            remove_token_from_object: If True, removes authentication token
                fields from the data before sending. Defaults to False.

        Returns:
            None

        Raises:
            Any exception raised by `self.client.send_server`.
        """
        await self.auth_client.send_server(data, remove_token_from_object)

    async def get_data(self, data: str) -> dict:
        """
        Fetches structured data from the server based on the given key.

        Delegates the retrieval logic to the authenticated client.

        Args:
            data (str): The key or identifier for the data to fetch.

        Returns:
            dict | None: The retrieved data as a dictionary if available;
            otherwise, None.
        """
        return await self.auth_client.get_data(data)

    async def join_global_chat(self) -> dict:
        """
        Joins the global chat by sending a join request to the server.

        This method constructs a packet with the appropriate type identifier
        and sends it to the server to add the client to the global chat session.

        Once joined, the client can receive and send messages within the
        global chat room.

        Returns:
            None

        Raises:
            Any exception raised by `send_server`.
        """
        chat_join_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_CHAT
        }
        await self.send_server(chat_join_request)
        return await self.get_data(PacketDataKeys.MESSAGES)


    async def leave_from_global_chat(self) -> dict:
        """
        Leaves the global chat and returns the client to the dashboard.

        Sends a request to the server to remove the client from the global chat
        and add them to the dashboard, typically representing a lobby or
        non-chat state.

        Returns:
            None

        Raises:
            Any exception raised by `send_server`.
        """
        leave_from_chat_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_DASHBOARD
        }
        await self.send_server(leave_from_chat_request)
        return await self.get_data(PacketDataKeys.DASHBOARD)

    async def send_message_global(
        self,
        content: str,
        message_style: int = MessageStyles.NO_COLOR
    ) -> None:
        """
        Sends a message to the global chat with optional styling.

        Validates and cleans the message before sending. Implements basic spam
        prevention and risk mitigation by skipping unsafe or repeated messages.

        Args:
            content (str): The text content of the message to send.
            message_style (int, optional): The display style of the message.
                Defaults to `MessageStyles.NO_COLOR`.

        Returns:
            None
        """
        utils: "Utils" = Utils()
        if not utils.validate_message_content(content):
            return None
        content = utils.clean_content(content)
        self.sent_messages.add_message(content)
        utils.auto_delete_first_message(self.sent_messages)
        if utils.is_ban_risk_message(self.sent_messages) is True:
            await asyncio.sleep(5)
            return None

        message_data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.CHAT_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.TEXT: content,
                PacketDataKeys.MESSAGE_STYLE: message_style,
            }
        }
        await self.send_server(message_data)
        return None
