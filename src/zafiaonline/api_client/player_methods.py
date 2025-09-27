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
Client-side interface for sending and receiving data via server packets.

This module provides a high-level asynchronous interface for interacting
with a game or application server. It includes methods for sending
requests (e.g., friend management, messaging, complaints, room actions),
receiving responses, and parsing returned data into model objects.

Typical usage example:

    client = Client(...)
    await client.players.remove_friend("user_id")
    messages = await client.get_private_messages("friend_id")
"""
import asyncio
import json

from typing import Any, TYPE_CHECKING
from msgspec.json import decode

if TYPE_CHECKING:
    from zafiaonline.api_client.user_methods import AuthService
from zafiaonline.structures.packet_data_keys import PacketDataKeys
from zafiaonline.structures.models import ModelFriend, ModelMessage
from zafiaonline.structures.enums import RatingMode, RatingType
from zafiaonline.utils.utils import Helpers
from zafiaonline.utils.utils_for_send_messages import Utils, SentMessages
from zafiaonline.utils.logging_config import logger


class PlayersMethods:
    """
    Handles all player-related interactions in the system.

    This class provides a high-level interface to interact with the 
    player's data, including friends, messages, complaints, ratings, 
    and profile information. It communicates with the backend server 
    via the provided authenticated client.

    Attributes:
        auth_client (Auth): An authenticated client used to communicate 
            with the backend.
        sent_messages (SentMessages): A message tracker used for spam 
            prevention and content validation.
    """
    def __init__(self, auth_client: "AuthService") -> None:
        """
        Initializes the Players class with an authenticated client.

        If the auth_client is valid, it retrieves and sets user attributes.

        Args:
            auth_client (Auth): The authenticated client instance.
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
        Sends data to the server using the authenticated client.

        This method delegates the sending operation to the internal client.
        Optionally removes the token from the data object before sending.

        Args:
            data: The dict data object to be sent to the server.
            remove_token_from_object (bool): If True, removes the token field
                from the object before sending. Defaults to False.

        Returns:
            None
        """
        await self.auth_client.send_server(data, remove_token_from_object)

    async def get_data(self, data: str) -> dict:
        """
        Sends a request and waits for a specific response from the server.

        Delegates the operation to the internal client to retrieve data that matches
        the given identifier or request type.

        Args:
            data: The string key or identifier used to filter or retrieve the expected response.

        Returns:
            dict | None: The response data as a dictionary if available,
            otherwise None.
        """
        return await self.auth_client.get_data(data)

    async def friend_list(self) -> list[ModelFriend]:
        """
        Fetches the user's friend list from the server.

        Sends a request with packet type `ADD_CLIENT_TO_FRIENDSHIP_LIST`, then
        awaits and decodes the server response into a list of `ModelFriend` objects.

        Returns:
            A list of `ModelFriend` instances representing the user's friends.

        Raises:
            AttributeError: If the friendship list is missing in the server response.
        """
        friends_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_FRIENDSHIP_LIST
        }
        await self.send_server(friends_request)

        received_data: dict = await self.get_data(
            PacketDataKeys.FRIENDSHIP_LIST
        )

        friends: list[ModelFriend] = []

        for friend in received_data[PacketDataKeys.FRIENDSHIP_LIST]:
            friends.append(
                decode(
                    json.dumps(friend),
                    type=ModelFriend
                )
            )
        return friends

    async def get_friend_invite_list(self) -> dict:
        """
        Fetches the list of friends in the invite list from the server.

        Sends a request to retrieve users currently in the invite list and awaits
        the server's response.

        Returns:
            The parsed server response associated with `FRIENDS_IN_INVITE_LIST`,
            typically a `dict` or `None` if the data was not received.
        """
        get_invite_list_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_FRIENDS_IN_INVITE_LIST
        }
        await self.send_server(get_invite_list_request)
        return await self.get_data(PacketDataKeys.FRIENDS_IN_INVITE_LIST)

    async def invite_friend(self, player_id: str) -> dict:
        """
        Sends a friend invite to a player by their ID.

        Sends a request to invite the specified player to the current room
        and awaits a confirmation response from the server.

        Args:
            player_id: The unique identifier of the player to invite.

        Returns:
            The server's response associated with the `FRIEND_IS_INVITED` key,
            or `None` if no response was received.
        """
        invite_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.SEND_FRIEND_INVITE_TO_ROOM,
            PacketDataKeys.USER_OBJECT_ID: player_id
        }
        await self.send_server(invite_request)
        return await self.get_data(PacketDataKeys.FRIEND_IS_INVITED)

    async def search_player(self, nickname: str) -> dict:
        """
        Searches for a player by their nickname.

        Sends a search request to the server to look up a player using the
        provided nickname.

        Args:
            nickname: The nickname of the player to search for.

        Returns:
            A dictionary containing the search result data, or None if no
            data was received.
        """
        search_info_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.SEARCH_USER,
            PacketDataKeys.SEARCH_TEXT: nickname
        }
        await self.send_server(search_info_request)
        return await self.get_data(PacketDataKeys.SEARCH_USER)

    async def remove_friend(self, friend_id: str) -> dict:
        """
        Removes a friend from the user's friend list.

        Sends a request to the server to remove the specified friend.

        Args:
            friend_id: The unique identifier of the friend to remove.

        Returns:
            None.
        """
        remove_friend_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.REMOVE_FRIEND,
            PacketDataKeys.FRIEND_USER_OBJECT_ID: friend_id
        }
        await self.send_server(remove_friend_request)
        return await self.get_data(PacketDataKeys.REMOVE_FRIEND)

    async def get_friend_requests(self) -> dict:
        get_friend_requests: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_SENT_FRIEND_REQUESTS_LIST,
        }
        await self.send_server(get_friend_requests)
        return await self.get_data(PacketDataKeys.FRIENDSHIP_LIST)

    async def kick_user_vote(
        self,
        room_id: str,
        value: bool = True
    ) -> None:
        """
        Sends a vote request to kick a user from a room.

        Args:
            room_id: The unique identifier of the room.
            value: The vote decision. Defaults to True (vote to kick).
        """
        vote_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.KICK_USER_VOTE,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.VOTE: value
        }
        await self.send_server(vote_request)
        return None

    async def kick_user(
        self,
        user_id: str,
        room_id: str
    ) -> dict:
        """
        Sends a request to kick a user from the specified room.

        Args:
            user_id: The unique identifier of the user to be kicked.
            room_id: The unique identifier of the room.
        """
        kick_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.KICK_USER,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.USER_OBJECT_ID: user_id
        }
        await self.send_server(kick_request)
        return await self.get_data(PacketDataKeys.KICK_USER)

    async def message_complaint(
        self,
        reason: str,
        screenshot_id: int,
        user_id: str
    ) -> dict:
        """
        Submits a complaint about a user's message.

        Allows users to report inappropriate messages by specifying a reason
        and attaching a screenshot.

        Args:
            reason: The reason for the complaint.
            screenshot_id: The ID of the uploaded screenshot. Obtained from
                update_photo_server().
            user_id: The ID of the user being reported.

        Returns:
            The server response to the complaint request.
        """
        complaint_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MAKE_COMPLAINT,
            PacketDataKeys.USER_OBJECT_ID: user_id,
            PacketDataKeys.REASON: reason,
            PacketDataKeys.SCREENSHOT: screenshot_id
            # Retrieved from update_photo_server()
        }
        await self.send_server(complaint_request)
        return await self.get_data(PacketDataKeys.MAKE_COMPLAINT)

    async def get_private_messages(
        self,
        friend_id: str
    ) -> list[ModelMessage]:
        """
        Retrieves private messages exchanged with a specific friend.

        Args:
            friend_id: The unique identifier of the friend.

        Returns:
            A list of private messages as ModelMessage objects.

        Raises:
            AttributeError: If no data was received from the server.
        """
        private_messages_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_PRIVATE_CHAT,
            PacketDataKeys.FRIENDSHIP: friend_id
        }
        await self.send_server(private_messages_request)

        received_messages: dict = await self.get_data(
            PacketDataKeys.PRIVATE_CHAT_LIST_MESSAGES
        )

        messages: list[ModelMessage] = [
            decode(
                json.dumps(message),
                type=ModelMessage
            )
            for message in received_messages[PacketDataKeys.MESSAGES]
        ]

        return messages

    async def get_rating(
        self,
        rating_type: RatingType = RatingType.AUTHORITY,
        rating_mode: RatingMode = RatingMode.ALL_TIME
    ) -> dict:
        """
        Retrieves the player rating based on the specified type and mode.

        Args:
            rating_type: The type of rating to retrieve. Defaults to RatingType.AUTHORITY.
            rating_mode: The time period for the rating. Defaults to RatingMode.ALL_TIME.

        Returns:
            A dictionary containing the rating data if successful, otherwise None.
        """
        rating_query: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_RATING,
            PacketDataKeys.RATING_TYPE: rating_type,
            PacketDataKeys.RATING_MODE: rating_mode
        }
        await self.send_server(rating_query)
        rating: dict = await self.get_data(PacketDataKeys.RATING)
        rating_user_list: dict = rating.get(
            PacketDataKeys.RATING_USERS_LIST,
            {}
        )
        return rating_user_list

    async def send_message_friend(
        self,
        friend_id: str,
        content: str
    ) -> dict | None:
        """
        Sends a private message to a friend.

        Args:
            friend_id: The unique identifier of the friend.
            content: The message text to be sent.

        Returns:
            None. The message is sent if it passes validation checks.
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
            PacketDataKeys.TYPE: PacketDataKeys.PRIVATE_CHAT_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.FRIENDSHIP: friend_id,
                PacketDataKeys.TEXT: content
            }
        }
        await self.send_server(message_data)
        return await self.get_data(PacketDataKeys.PRIVATE_CHAT_LAST_MESSAGE)

    async def get_user(self, user_id: str) -> dict | None:
        """
        Retrieves the profile data of a specific user.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The user's profile data if successfully retrieved, otherwise None.

        Raises:
            Exception: If an unexpected error occurs while fetching the data.
        """
        user_payload: dict[str, Any] = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_USER_PROFILE,
            PacketDataKeys.USER_RECEIVER: user_id,
            PacketDataKeys.USER_OBJECT_ID: self.auth_client.user.user_id,
        }
        await self.send_server(user_payload)

        try:
            user_data: dict = await self.get_data(
                PacketDataKeys.USER_PROFILE
            )
            if not user_data:
                logger.error(f"Error: get_data returned {user_data}")
                return None
            return user_data
        except Exception as e:
            logger.error(
                f"Error retrieving user {user_id} data: {e}",
                exc_info=True
            )
            return None
        
    async def add_friend(self, user_id: str) -> int:
        friend_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_FRIEND,
            PacketDataKeys.FRIEND_USER_OBJECT_ID: user_id,
        }
        await self.send_server(friend_request)
        request_data: dict = await self.get_data(PacketDataKeys.ADD_FRIEND)
        request_status: int = request_data.get(
            PacketDataKeys.FRIENDSHIP_FLAG,
            1
        )
        return request_status
