import asyncio
import json

from typing import Optional, List, TYPE_CHECKING, Any
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
    def __init__(self, client: "Auth"):
        self.client = client
        if self.client:
            get_user_attributes(self.client)
        self.sent_messages = SentMessages()
        self.md5hash = Md5()

    async def send_server(self, data, remove_token_from_object = False):
        await self.client.send_server(data, remove_token_from_object)

    async def get_data(self, data):
        return await self.client.get_data(data)

    async def listen(self):
        return await self.client.listen()

    @property
    def device_id(self):
        return self.client.device_id

    async def vote_player_list(self, user_id: str, room_id: str) -> None:
        """
        Sends a request to vote for a player in the given room.

        Parameters:
            user_id (str): The unique identifier of the player being voted for.
            room_id (str): The unique identifier of the room.

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

        Parameters:
            selected_roles (Optional[List[Roles]]): List of selected roles
            for the room. Defaults to [0].
            title (str): The title of the room. Defaults to an empty string.
            max_players (int): Maximum number of players allowed in the
            room. Defaults to 8.
            min_players (int): Minimum number of players required to start
            the game. Defaults to 5.
            password (str): Optional password for the room.
            Defaults to an empty string.
            min_level (int): Minimum player level required to join.
            Defaults to 1.
            vip_enabled (bool): Whether VIP features are enabled.
            Defaults to False.

        Returns:
            ModelRoom: The created room object.
        """
        roles: list[int] = selected_roles or [0]
        room_request: dict = self._build_room_request(roles, title,
                                                max_players, min_players,
                                                password, min_level,
                                                vip_enabled)

        await self.send_server(room_request)
        received_data: dict | None = await self._get_validated_room_response(room_request)

        if received_data is None:
            raise AttributeError("No received_data")

        return self._decode_room(received_data)

    def _build_room_request(self, selected_roles: List[Roles | int],
            title: str, max_players: int, min_players: int, password:
            Optional[str],
            min_level: int, vip_enabled: bool) -> dict:
        """
        Constructs the request payload for creating a room.

        Args:
            selected_roles (Optional[List[Roles]]): List of selected roles
            for the room.
            title (str): The title of the room (max 15 characters).
            max_players (int): Maximum number of players allowed (8-21).
            min_players (int): Minimum number of players required (5-18).
            password (str): Room password (will be hashed).
            min_level (int): Minimum level required to join (must be ≥1).
            vip_enabled (bool): Whether VIP mode is enabled.

        Returns:
            dict: A dictionary representing the request payload.
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
        Sends the room creation request and ensures a valid response is
        received.

        If the first attempt fails, it retries once. If both attempts fail,
        logs an error and returns None.

        Args:
            room_request (dict): The room creation request payload.

        Returns:
            Optional[dict]: The validated response if successful, else None.
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
        Decodes the received room data into a ModelRoom object.

        Args:
            received_data (dict): The raw room data from the server.

        Returns:
            Optional[ModelRoom]: Decoded ModelRoom object if successful,
            otherwise None.
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
        Removes the player from the specified room.

        Parameters:
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
        Leaves the specified room by removing the player.

        Parameters:
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
        Creates a player in the specified room.

        This method should be called after `join_room()` if the user is not
        the host.

        Parameters:
            room_id (str): The unique identifier of the room.
            room_model_type (RoomModelType, optional): The type of the room.
            Defaults to `NOT_MATCHMAKING_MODE`.

        Returns:
            Optional[dict]: Room statistics if successful, otherwise None.
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
        Joins a specified room.

        Parameters:
            room_id (str): The unique identifier of the room to join.
            password (str, optional): The password for the room,
            if required. Defaults to an empty string.

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
        Performs an action associated with a player's role during a game.

        This method is used when executing a role-based action or voting
        after the game has started.

        Parameters:
            user_id (str): The unique identifier of the targeted user.
            room_id (str): The unique identifier of the room where the
            action occurs.
            room_model_type (RoomModelType, optional): The type of room model.
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

        This method allows a player to surrender during an ongoing game.

        Parameters:
            room_id (str): The unique identifier of the room where the
            surrender occurs.
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
        Sends a message to a room.

        Parameters:
            content (str): The message text to be sent.
            room_id (str): The unique identifier of the room.
            message_style (int, optional): The style of the message.
            Defaults to 0.

        Returns:
            None

        Notes:
            - If the content is empty, the function prevents sending to
            avoid spam or bans.
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

    async def add_client_to_room_list(self) -> Any:
        """
        Sends a request to add the client to the list of available rooms.

        This function allows the client to receive updates about available
        rooms
        in the game lobby.

        Returns:
            Any
        """
        rooms_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_ROOMS_LIST
        }
        await self.send_server(rooms_request)

        return await self.get_data(PacketDataKeys.ROOMS)


class MatchMaking:
    def __init__(self, client: "Auth"):
        self.client = client
        if self.client:
            get_user_attributes(self.client)

    async def send_server(self, data, remove_token_from_object = False):
        await self.client.send_server(data, remove_token_from_object)

    async def get_data(self, data):
        return await self.client.get_data(data)

    async def match_making_get_status(self) -> dict | None:
        """
        Retrieves the current status of matchmaking.

        Returns:
            dict: The matchmaking status data received from the server.

        Notes:
            - Sends a request to fetch the matchmaking status.
            - Waits for and returns the response from the server.
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

        Parameters:
            players_size (int, optional): The desired number of players in
            the game.
            Defaults to 8.

        Returns:
            dict: The response data containing the count of waiting users.

        Notes:
            - Sends a request to the server to get the count of players
            waiting in matchmaking.
            - Waits for and returns the response from the server.
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

        Parameters:
            players_size (int, optional): The desired number of players in
            the game.
            Defaults to 8.

        Returns:
            None

        Notes:
            - Sends a request to the server to add the user to matchmaking.
            - No response data is expected.
        """
        add_user_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MATCH_MAKING_ADD_USER,
            PacketDataKeys.MATCH_MAKING_BASE_PLAYERS_AMOUNT: players_size
        }
        await self.send_server(add_user_request)

    async def match_making_remove_user(self) -> None:
        """
        Removes the user from the matchmaking queue.

        Returns:
            None

        Notes:
            - Sends a request to the server to remove the user from
            matchmaking.
            - No response data is expected.
        """
        remove_user_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MATCH_MAKING_REMOVE_USER
        }
        await self.send_server(remove_user_request)
