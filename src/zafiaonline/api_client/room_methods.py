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
This module provides matchmaking and room-related functionalities for a multiplayer game client.

It defines asynchronous methods for joining and leaving rooms, creating players, performing
role-based actions, sending messages, and interacting with the matchmaking queue. The module
relies on communication with a game server using structured packet data.

Typical usage example:

    auth = Auth(...)
    matchmaking = MatchMaking(auth)
    await matchmaking.match_making_add_user(players_size = 12)
"""
import asyncio
import json

from typing import Optional, List, TYPE_CHECKING
from msgspec.json import decode

from zafiaonline.utils import Md5

if TYPE_CHECKING:
    from zafiaonline.api_client.user_methods import Auth
from zafiaonline.utils.utils_for_send_messages import Utils, SentMessages
from zafiaonline.structures import PacketDataKeys, ModelRoom
from zafiaonline.structures.enums import MessageStyles, RoomModelType, Roles
from zafiaonline.utils.logging_config import logger
from zafiaonline.utils.utils import get_user_attributes


class Room:
    """
    Handles multiplayer room logic over WebSocket for an authenticated client.

    The Room class provides high-level operations for creating, joining,
    managing, and interacting within game rooms via WebSocket. It builds
    structured payloads, handles message dispatch, and manages room-level
    interactions like chat, voting, and forfeiting.

    Attributes:
        client (Auth): Authenticated WebSocket client used for communication.
        sent_messages (SentMessages): Tracker for detecting repeated messages or spam.
        md5hash (Md5): Utility for hashing passwords with salt before transmission.
    """
    def __init__(self, client: "Auth"):
        """
        Initializes a Room instance with an authenticated WebSocket client.

        This constructor sets up the authenticated client connection, initializes
        message tracking to prevent spam, and prepares utilities like MD5 hashing
        for password security.

        Args:
            client (Auth): An authenticated WebSocket client used to send and receive
                messages related to room interactions.
        """
        self.client = client
        if self.client:
            get_user_attributes(self.client)
        self.sent_messages = SentMessages()
        self.md5hash = Md5()

    async def send_server(self, data: dict, 
                          remove_token_from_object: bool = False) -> None:
        """
        Sends a structured payload to the game server via WebSocket.

        Delegates the actual sending logic to the authenticated client.

        Args:
            data (dict): The payload to be sent to the server.
            remove_token_from_object (bool, optional): Whether to remove the
                authentication token from the payload object before sending.
                Defaults to False.

        Returns:
            None
        """
        await self.client.send_server(data, remove_token_from_object)

    async def get_data(self, data: str) -> dict | None:
        """
        Fetches structured data from the server based on the given key.

        Delegates the retrieval logic to the authenticated client.

        Args:
            data (str): The key or identifier for the data to fetch.

        Returns:
            dict | None: The retrieved data as a dictionary if available;
            otherwise, None.
        """
        return await self.client.get_data(data)

    async def listen(self) -> dict | None:
        """
        Waits for and returns the next incoming message from the server.

        This method listens for a single message from the WebSocket connection
        and returns it as a dictionary.

        Returns:
            dict | None: The parsed message if received successfully;
            otherwise, None.
        """
        return await self.client.listen()

    @property
    def device_id(self):
        """
        Device ID associated with the client.

        Returns:
            str: The unique device identifier used for authentication.
        """
        return self.client.device_id

    async def vote_player_list(self, user_id: str, room_id: str) -> None:
        """
        Sends a vote request for a specific player in a room.

        Constructs and sends a vote payload to the server, indicating that the user
        with the given `user_id` is being voted for within the specified room.

        Args:
            user_id (str): The ID of the player being voted for.
            room_id (str): The ID of the room where the vote is cast.

        Returns:
            None
        """
        vote_info_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.VOTE_PLAYER_LIST,
            PacketDataKeys.USER_OBJECT_ID: user_id,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(vote_info_request)

    async def create_room(
            self,
            selected_roles: List[Roles | int] = [0],
            title: str = "",
            max_players: int = 8,
            min_players: int = 5,
            password: str | None = None,
            min_level: int = 1,
            vip_enabled: bool = False
    ) -> ModelRoom | None:
        """
        Creates a new game room with the specified parameters.

        Sends a room creation request to the server with the configured
        settings such as player limits, role selection, room title,
        and access restrictions.

        Args:
            selected_roles (List[Roles | int], optional): List of roles or role IDs
                selected for the room. Defaults to [0].
            title (str, optional): Title of the room. Defaults to "".
            max_players (int, optional): Maximum number of players allowed. Defaults to 8.
            min_players (int, optional): Minimum number of players to start the game. Defaults to 5.
            password (str | None, optional): Optional password for the room. Defaults to None.
            min_level (int, optional): Minimum player level required to join. Defaults to 1.
            vip_enabled (bool, optional): Whether VIP features are enabled. Defaults to False.

        Returns:
            ModelRoom | None: A `ModelRoom` instance if room creation succeeds, otherwise None.

        Raises:
            AttributeError: If no response data is received after sending the request.
        """
        roles: list[int] = selected_roles or [0]
        room_request: dict = self._build_room_request(roles, title,
                                                max_players, min_players,
                                                password, min_level,
                                                vip_enabled)

        await self.send_server(room_request)
        received_data: dict | None = await self._get_validated_room_response(room_request)

        if received_data is None:
            raise AttributeError("No received data")

        return self._decode_room(received_data)

    def _build_room_request(self, selected_roles: List[Roles | int],
            title: str, max_players: int, min_players: int, password:
            Optional[str],
            min_level: int, vip_enabled: bool) -> dict:
        """
        Constructs the request payload for creating a room.

        Builds a structured dictionary payload for room creation, applying
        constraints to player counts, trimming titles, and hashing passwords.

        Args:
            selected_roles (List[Roles | int]): List of selected roles or role IDs for the room.
            title (str): Title of the room. Will be trimmed to 15 characters.
            max_players (int): Maximum number of players allowed (clamped between 8 and 21).
            min_players (int): Minimum number of players required (clamped between 5 and 18).
            password (Optional[str]): Optional room password; will be hashed with salt if provided.
            min_level (int): Minimum player level required to join (minimum 1).
            vip_enabled (bool): Whether VIP features are enabled.

        Returns:
            dict: Dictionary payload ready to be sent to the server.
        """
        return {
            PacketDataKeys.TYPE: PacketDataKeys.ROOM_CREATE,
            PacketDataKeys.ROOM: {
                PacketDataKeys.MAX_PLAYERS: min(21, max(8, max_players)),
                PacketDataKeys.MIN_PLAYERS: min(18, max(5, min_players)),
                PacketDataKeys.MIN_LEVEL: max(1, min_level),
                PacketDataKeys.DEVICE_ID: self.device_id,
                PacketDataKeys.PASSWORD: self.md5hash.md5salt(password)
                if password is not None else "",
                PacketDataKeys.SELECTED_ROLES: selected_roles,
                PacketDataKeys.TITLE: title.strip()[:15] if title else "",
                PacketDataKeys.VIP_ENABLED: vip_enabled,
            },
        }

    async def _get_validated_room_response(self, room_request: dict) -> \
    dict | None:
        """
        Sends the room creation request and ensures a valid response is received.

        Attempts to retrieve and validate the server response to a room creation
        request. If the response is invalid or missing, retries up to three times
        before giving up and logging an error.

        Args:
            room_request (dict): The dictionary payload representing the room creation request.

        Returns:
            dict | None: The validated room creation response, or None if all attempts fail.
        """
        max_attempts: int = 3
        attempt: int = 0

        while attempt <= max_attempts:
            try:
                received_data: dict | None = await self.get_data(
                    PacketDataKeys.ROOM_CREATED)
                if isinstance(received_data, dict) and received_data.get(
                        PacketDataKeys.TYPE) == PacketDataKeys.ROOM_CREATED:
                    return received_data
                logger.warning(f"Invalid room creation response"
                               f" {received_data}, retrying...")
                await asyncio.sleep(12)
                await self.send_server(room_request)
            except Exception as e:
                logger.error(f"Get server data error: "
                              f"{e}", exc_info=True)
            attempt += 1

        logger.error("Room creation failed after retry.")
        return None

    @staticmethod
    def _decode_room(received_data: dict) -> ModelRoom | None:
        """
        Decodes raw server data into a ModelRoom instance.

        Attempts to extract and decode the room data from the given dictionary.
        Logs an error and returns None if the expected data is missing or
        decoding fails.

        Args:
            received_data (dict): The raw dictionary received from the server containing room data.

        Returns:
            ModelRoom | None: A ModelRoom instance if decoding is successful; otherwise, None.
        """
        try:
            if received_data:
                if PacketDataKeys.ROOM not in received_data:
                    logger.error("Missing room data in response")
                    return None

                return decode(json.dumps(received_data[PacketDataKeys.ROOM]),
                          type = ModelRoom)
            return None

        except TypeError:
            logger.error(f"Failed to decode room data: data is None",
                          exc_info = True)
            return None

        except Exception as e:
            logger.error(f"Failed to decode room data: {e}", exc_info = True)
            return None

    async def remove_player(self, room_id: str) -> None:
        """
        Sends a request to remove the player from a specific room.

        Constructs and sends a request to leave or be removed from the room
        with the given identifier.

        Args:
            room_id (str): The unique identifier of the room.

        Returns:
            None
        """
        leave_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.REMOVE_PLAYER,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(leave_request)

    async def leave_room(self, room_id: str) -> None:
        """
        Leaves the specified room by sending a removal request.

        Delegates to `remove_player` to handle the actual request to
        leave the room.

        Args:
            room_id (str): The unique identifier of the room.

        Returns:
            None
        """
        await self.remove_player(room_id)

    async def create_player(self, room_id: str,
                            room_model_type: RoomModelType =
                            RoomModelType.NOT_MATCHMAKING_MODE)\
                            -> dict | None:
        """
        Creates a player in the specified room and retrieves room statistics.

        Should be called after `join_room()` if the user is not the host.

        Sends a request to create a player in the given room, waits for room
        statistics to be received, and retries up to 3 times if necessary.

        Args:
            room_id (str): The unique identifier of the room.
            room_model_type (RoomModelType, optional): The type of room model.
                Defaults to `RoomModelType.NOT_MATCHMAKING_MODE`.

        Returns:
            dict | None: A dictionary containing "player_list" and "room_messages"
            if successful, otherwise None.

        Raises:
            AttributeError: If the room statistics cannot be retrieved.
        """
        create_player_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.CREATE_PLAYER,
            PacketDataKeys.ROOM_MODEL_TYPE: room_model_type,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(create_player_request)
        await asyncio.sleep(.01)
        data: dict | None = await self.get_data(PacketDataKeys.ROOM_STATISTICS)
        attempts: int = 0
        while data is None and attempts < 3:
            await self.send_server(create_player_request)
            try:
                await asyncio.sleep(.01)
                data = await self.get_data(PacketDataKeys.ROOM_STATISTICS)
            except TimeoutError:
                logger.error("NOT CRITICAL error get room players and "
                              "messages")
            attempts += 1
            if data is not None and attempts < 3:
                break
        if data is None:
            raise AttributeError
        player_list: list = data.get(PacketDataKeys.PLAYERS, [])
        room_messages: list = data.get(PacketDataKeys.MESSAGES, [])

        return {"player_list": player_list, "room_messages": room_messages}

    async def join_room(self, room_id: str, password: str = "") -> None:
        """
        Joins a specified room using the given room ID and optional password.

        Sends a request to the server to join the specified room. If a password
        is provided, it is hashed before being included in the request.

        Args:
            room_id (str): The unique identifier of the room to join.
            password (str, optional): The password for the room, if required.
                Defaults to an empty string.

        Returns:
            None
        """
        join_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ROOM_ENTER,
            PacketDataKeys.ROOM_PASS: self.md5hash.md5salt(
                password) if password else "",
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(join_request)

    async def role_action(self, user_id: str, room_id: str,
                          room_model_type: RoomModelType =
                          RoomModelType.NOT_MATCHMAKING_MODE) -> None:
        """
        Performs a role-specific action on a user within a room.

        Used to execute a role-based action (e.g., vote, attack, investigate)
        during an ongoing game.

        Args:
            user_id (str): The unique identifier of the targeted user.
            room_id (str): The unique identifier of the room where the action occurs.
            room_model_type (RoomModelType, optional): The type of room model to use.
                Defaults to RoomModelType.NOT_MATCHMAKING_MODE.

        Returns:
            None
        """
        action_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ROLE_ACTION,
            PacketDataKeys.USER_OBJECT_ID: user_id,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.ROOM_MODEL_TYPE: room_model_type
        }
        await self.send_server(action_request, True)

    async def give_up(self, room_id: str, room_model_type: RoomModelType =
    RoomModelType.NOT_MATCHMAKING_MODE) -> None:
        """
        Sends a request to forfeit the game.

        Allows a player to surrender during an ongoing game.

        Args:
            room_id (str): The unique identifier of the room where the surrender occurs.
            room_model_type (RoomModelType, optional): The type of room model.
                Defaults to RoomModelType.NOT_MATCHMAKING_MODE.

        Returns:
            None
        """
        give_up_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GIVE_UP,
            PacketDataKeys.ROOM_MODEL_TYPE: room_model_type,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(give_up_request)

    async def send_message_room(self, content: str, room_id: str,
                                message_style: int = MessageStyles.NO_COLOR)\
                                -> None:
        """
        Sends a message to the specified room.

        Prevents sending if the message content is empty or potentially
        risky to avoid spam or bans.

        Args:
            content (str): The message text to be sent.
            room_id (str): The unique identifier of the room.
            message_style (int, optional): The style of the message.
                Defaults to MessageStyles.NO_COLOR.

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
            PacketDataKeys.TYPE: PacketDataKeys.ROOM_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.TEXT: content,
                PacketDataKeys.MESSAGE_STYLE: message_style
            },
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(message_data)
        return None

    async def add_client_to_room_list(self) -> dict | None:
        """
        Adds the client to the list of available rooms.

        Sends a request so the client can receive updates about available
        rooms in the game lobby.

        Returns:
            Optional[dict]: Room list data if available, otherwise None.
        """
        rooms_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_ROOMS_LIST
        }
        await self.send_server(rooms_request)

        return await self.get_data(PacketDataKeys.ROOMS)


class MatchMaking:
    """
    Handles matchmaking operations for the client.

    This class provides methods for interacting with the matchmaking system,
    including adding and removing the user from the matchmaking queue,
    checking queue status, and retrieving user count.

    Attributes:
        client (Auth): The authenticated client instance used to send and
            receive data from the server.
    """
    def __init__(self, client: "Auth"):
        """
        Initializes the MatchMaking instance.

        This constructor sets up the matchmaking client and initializes
        user attributes if a valid client is provided.

        Args:
            client (Auth): The authenticated client instance used for communication
                with the game server.
        """
        self.client = client
        if self.client:
            get_user_attributes(self.client)

    async def send_server(self, data: dict,
                          remove_token_from_object: bool = False) -> None:
        """
        Sends a packet to the server through the authenticated client.

        Args:
            data (dict): The data to be sent to the server.
            remove_token_from_object (bool, optional): Whether to remove the token
                from the object before sending. Defaults to False.

        Returns:
            None
        """
        await self.client.send_server(data, remove_token_from_object)

    async def get_data(self, data: str) -> dict | None:
        """
        Retrieves data from the server through the authenticated client.

        Args:
            data (str): The key or identifier for the data to retrieve.

        Returns:
            dict | None: The data received from the server, or None if no data is available.
        """
        return await self.client.get_data(data)

    async def match_making_get_status(self) -> dict | None:
        """
        Retrieves the current status of matchmaking.

        Sends a request to the server to get the current matchmaking status and 
        waits briefly for a response.

        Returns:
            dict | None: The matchmaking status data received from the server,
            or None if no data is returned.
        """
        status_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MATCH_MAKING_GET_STATUS
        }
        await self.send_server(status_request)
        await asyncio.sleep(.01)
        return await self.get_data(PacketDataKeys.MATCH_MAKING_MATCH_STATUS)

    async def users_waiting_count(self, players_size: int = 8) -> dict | None:
        """
        Retrieves the number of users currently waiting for a matchmaking game.

        Sends a request to the server to get the number of players currently
        waiting in the matchmaking queue.

        Args:
            players_size (int, optional): The desired number of players in the game.
                Defaults to 8.

        Returns:
            dict | None: The response data containing the count of waiting users,
            or None if no data is returned.
        """
        users_in_wait_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.
            GET_MATCH_MAKING_USERS_IN_QUEUE_INTERVAL,
            PacketDataKeys.MATCH_MAKING_BASE_PLAYERS_AMOUNT: players_size
        }
        await self.send_server(users_in_wait_request)
        await asyncio.sleep(.01)
        return await self.get_data(PacketDataKeys.
                                   GET_MATCH_MAKING_USERS_IN_QUEUE_INTERVAL)

    async def match_making_add_user(self, players_size: int = 8) -> None:
        """
        Adds the user to the matchmaking queue.

        Sends a request to the server to add the user to matchmaking. No response
        is expected.

        Args:
            players_size (int, optional): The desired number of players in the game.
                Defaults to 8.

        Returns:
            None
        """
        add_user_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MATCH_MAKING_ADD_USER,
            PacketDataKeys.MATCH_MAKING_BASE_PLAYERS_AMOUNT: players_size
        }
        await self.send_server(add_user_request)

    async def match_making_remove_user(self) -> None:
        """
        Removes the user from the matchmaking queue.

        Sends a request to the server to remove the user from matchmaking. No
        response is expected.

        Returns:
            None
        """
        remove_user_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MATCH_MAKING_REMOVE_USER
        }
        await self.send_server(remove_user_request)
