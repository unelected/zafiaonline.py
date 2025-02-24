import asyncio
import json
import base64
import logging

from typing import List, Optional, Union
from secrets import token_hex

from msgspec.json import decode

from zafiaonline.utils.md5hash import Md5
from zafiaonline.structures.packet_data_keys import PacketDataKeys
from zafiaonline.structures.models import (ModelUser, ModelServerConfig,
                                           ModelRoom, ModelFriend,
                                           ModelMessage)
from zafiaonline.structures.enums import (Languages, Roles,
                                          Sex, RatingMode, RatingType,
                                          RoomModelType)
from zafiaonline.websocket_module import Websocket

logging.basicConfig(level=logging.INFO)

class Client(Websocket):
    def __init__(self, proxy: Optional[List[str]] = None, debug: bool =
    False) -> None:
        """
        Initializes the Client.

        Parameters:
            proxy (Optional[List[str]]): List of proxy addresses. Defaults
            to an empty list.
            debug (bool): Enables or disables debug mode. Defaults to False.
        """
        self.proxy = proxy or []
        self.debug = debug
        self.token: Optional[str] = None
        self.id: Optional[str] = None
        self.md5hash = Md5()
        self.user = ModelUser()
        self.server_config = ModelServerConfig()
        self.address = "37.143.8.68"
        self.port = 7090
        self.rest_address = f"http://{self.address}:{self.port}"
        super().__init__(client=self)


    async def sign_in(self, email: str = "", password: str = "",
                      token: str = "", user_id: str = "") -> Union[
        ModelUser, bool]:
        """
        Signs in a user.

        Parameters:
            email (str): The user's email. Defaults to an empty string.
            password (str): The user's password. Defaults to an empty string.
            token (str): The user's authentication token. Defaults to an
            empty string.
            user_id (str): The user's ID. Defaults to an empty string.

        Returns:
            ModelUser: The user object if authentication is successful.
            bool: False if authentication fails.
        """
        self._warn_if_default_email(email)
        await self._ensure_connection()

        auth_data = self._prepare_auth_data(email, password, token, user_id)
        await self.send_server(auth_data)

        return await self._process_auth_response()

    @staticmethod
    def _warn_if_default_email(email: str) -> None:
        """
        Logs a warning if the email is set to the default value.

        Parameters:
            email (str): The email address to check.

        Returns:
            None
        """
        default_email = "email"
        if email.strip().lower() == default_email:
            logging.warning(
                "Your email is literally 'email'. Please update your config "
                "if this is incorrect."
            )

    async def _ensure_connection(self) -> None:
        """
        Ensures the client is connected before performing an action.

        If the connection is not alive, it attempts to create a new one.
        """
        if not self.alive:
            logging.debug("Connection not active. Attempting to reconnect...")
            await self.create_connection()

    def _prepare_auth_data(self, email: str, password: str, token: str,
                           user_id: str) -> dict:
        """
        Prepares the authentication payload for the sign-in request.

        Parameters:
            email (str): The user's email address.
            password (str): The user's password.
            token (str): The authentication token.
            user_id (str): The unique identifier of the user.

        Returns:
            dict: The authentication payload.
        """
        return {
            PacketDataKeys.DEVICE_ID: token_hex(10),
            # Generates a random device ID
            PacketDataKeys.TYPE: PacketDataKeys.SIGN_IN,
            PacketDataKeys.EMAIL: email,
            PacketDataKeys.PASSWORD: self.md5hash.md5salt(password or ""),
            # Hashes password
            PacketDataKeys.OBJECT_ID: user_id,
            PacketDataKeys.TOKEN: token,
        }

    async def _process_auth_response(self) -> Union[ModelUser, bool]:
        """
        Processes the server response after attempting to sign in.

        Returns:
            ModelUser: The authenticated user object if sign-in is successful.
            bool: False if authentication fails.
        """
        received_data = await self.get_data(PacketDataKeys.USER_SIGN_IN)

        if not received_data or received_data.get(
                PacketDataKeys.TYPE) != PacketDataKeys.USER_SIGN_IN:
            logging.error("Sign-in data retrieval error")
            return False

        self._set_user_data(received_data)
        return self.user

    def _set_user_data(self, received_data: dict):
        """
        Parses and stores user data from the sign-in response.

        Args:
            received_data (dict): The response data containing user and
            server info.
        """
        try:
            user_data = received_data.get(PacketDataKeys.USER)
            server_config_data = received_data.get(
                PacketDataKeys.SERVER_CONFIG)

            if not user_data or not server_config_data:
                logging.error("Missing user or server config data in response")
                return

            self.user = decode(json.dumps(user_data).encode(), type=ModelUser)
            self.server_config = decode(json.dumps(server_config_data),
                                        type=ModelServerConfig)

            self.token = self.user.token
            self.id = self.user.user_id

        except Exception as e:
            logging.error(f"Error parsing user data: {e}", exc_info=True)

    async def kick_user_vote(self, room_id: str, value: bool = True) -> None:
        """
        Sends a vote request to kick a user from the room.

        Parameters:
            room_id (str): The unique identifier of the room.
            value (bool, optional): The vote decision.
            Defaults to True (vote to kick).

        Returns:
            None
        """
        vote_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.KICK_USER_VOTE,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.VOTE: value
        }
        await self.send_server(vote_request)
        
    async def kick_user(self, user_id: str, room_id: str) -> None:
        """
        Sends a request to kick a user from the specified room.

        Parameters:
            user_id (str): The unique identifier of the user to be kicked.
            room_id (str): The unique identifier of the room.

        Returns:
            None
        """
        kick_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.KICK_USER,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.USER_OBJECT_ID: user_id
        }
        await self.send_server(kick_request)

    async def username_set(self, nickname: str) -> None:
        """
        Sends a request to update the user's nickname.

        Parameters:
            nickname (str): The new nickname to be set.

        Returns:
            None
        """
        username_update_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USERNAME_SET,
            PacketDataKeys.USERNAME: nickname
        }
        await self.send_server(username_update_request)

    async def select_language(self, language: Languages = Languages.RUSSIAN)\
            -> None:
        """
        Sends a request to update the user's preferred language.

        Parameters:
            language (Languages): The language to be set. Defaults to Russian.

        Returns:
            None
        """
        language_update_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USER_SET_SERVER_LANGUAGE,
            PacketDataKeys.SERVER_LANGUAGE: language
        }
        await self.send_server(language_update_request)

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
            selected_roles: Optional[List[Roles]] = None,
            title: str = "",
            max_players: int = 8,
            min_players: int = 5,
            password: str = "",
            min_level: int = 1,
            vip_enabled: bool = False
    ) -> ModelRoom:
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
        selected_roles = selected_roles or [0]
        room_request = self._build_room_request(selected_roles, title,
                                                max_players, min_players,
                                                password, min_level,
                                                vip_enabled)

        await self.send_server(room_request)
        received_data = await self._get_validated_room_response(room_request)

        return self._decode_room(received_data)

    def _build_room_request(
            self,
            selected_roles: Optional[List[Roles]],
            title: str,
            max_players: int,
            min_players: int,
            password: str,
            min_level: int,
            vip_enabled: bool,
    ) -> dict:
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
                PacketDataKeys.MIN_PLAYERS: min(18, max(5, min_players)),
                PacketDataKeys.MAX_PLAYERS: min(21, max(8, max_players)),
                PacketDataKeys.PASSWORD: self.md5hash.md5salt(password or ""),
                PacketDataKeys.DEVICE_ID: 0,
                PacketDataKeys.SELECTED_ROLES: selected_roles,
                PacketDataKeys.MIN_LEVEL: max(1, min_level),
                PacketDataKeys.TITLE: title.strip()[:15],
                PacketDataKeys.VIP_ENABLED: vip_enabled,
            },
        }

    async def _get_validated_room_response(self, room_request: dict) -> \
    Optional[dict]:
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
        received_data = await self.get_data(PacketDataKeys.ROOM_CREATED)

        if received_data.get(
                PacketDataKeys.TYPE) != PacketDataKeys.ROOM_CREATED:
            logging.warning("Invalid room creation response, retrying...")
            await self.send_server(room_request)
            received_data = await self.get_data(PacketDataKeys.ROOM_CREATED)
            await asyncio.sleep(1)

        if received_data.get(
                PacketDataKeys.TYPE) != PacketDataKeys.ROOM_CREATED:
            logging.error("Room creation failed after retry.")
            return None

        return received_data

    @staticmethod
    def _decode_room(received_data: dict) -> Optional[ModelRoom]:
        """
        Decodes the received room data into a ModelRoom object.

        Args:
            received_data (dict): The raw room data from the server.

        Returns:
            Optional[ModelRoom]: Decoded ModelRoom object if successful,
            otherwise None.
        """
        try:
            if PacketDataKeys.ROOM not in received_data:
                logging.error("Missing room data in response")
                return None

            return decode(json.dumps(received_data[PacketDataKeys.ROOM]),
                          type=ModelRoom)

        except Exception as e:
            logging.error(f"Failed to decode room data: {e}", exc_info=True)
            return None

    async def friend_list(self) -> List[ModelFriend]:
        """
        Retrieves the user's friend list.

        Returns:
            List[ModelFriend]: A list of friends as ModelFriend objects.
        """
        friends_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_FRIENDSHIP_LIST
        }
        await self.send_server(friends_request)

        received_data = await self.get_data(PacketDataKeys.FRIENDSHIP_LIST)

        friends: List[ModelFriend] = []

        for friend in received_data[PacketDataKeys.FRIENDSHIP_LIST]:
            friends.append(decode(json.dumps(friend), type=ModelFriend))
        return friends

    async def search_player(self, nickname: str) -> dict:
        """
        Searches for a player by their nickname.

        Parameters:
            nickname (str): The nickname of the player to search for.

        Returns:
            dict: The search result data.
        """
        search_info_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.SEARCH_USER,
            PacketDataKeys.SEARCH_TEXT: nickname
        }
        await self.send_server(search_info_request)
        return await self.get_data(PacketDataKeys.SEARCH_USER)

    async def remove_friend(self, friend_id: str) -> None:
        """
        Removes a friend from the user's friend list.

        Parameters:
            friend_id (str): The unique identifier of the friend to remove.

        Returns:
            None
        """
        remove_friend_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.REMOVE_FRIEND,
            PacketDataKeys.FRIEND_USER_OBJECT_ID: friend_id
        }
        await self.send_server(remove_friend_request)

    async def update_photo(self, file: bytes) -> None:
        """
        Uploads and updates the user's profile photo.

        Parameters:
            file (bytes): The image file in bytes to be uploaded.

        Returns:
            None
        """
        update_photo_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.UPLOAD_PHOTO,
            PacketDataKeys.FILE: base64.encodebytes(file).decode()
        }
        await self.send_server(update_photo_request)

    async def update_photo_server(self, file: bytes) -> None:
        """
        Uploads and updates a screenshot on the server.

        Parameters:
            file (bytes): The screenshot file in bytes to be uploaded.

        Returns:
            None
        """
        upload_photo_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.UPLOAD_SCREENSHOT,
            PacketDataKeys.FILE: base64.encodebytes(file).decode()
        }
        await self.send_server(upload_photo_request)

    async def update_sex(self, sex: Sex) -> dict:
        """
        Updates the user's gender.

        Parameters:
            sex (Sex): The new gender to be set for the user.

        Returns:
            dict: The server response after updating the gender.
        """
        update_sex_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USER_CHANGE_SEX,
            PacketDataKeys.SEX: sex
        }
        await self.send_server(update_sex_request)
        return await self.listen()

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
    room_model_type: RoomModelType = RoomModelType.NOT_MATCHMAKING_MODE) -> \
    Optional[dict]:
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
        return await self.get_data(PacketDataKeys.ROOM_STATISTICS)

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

    async def message_complaint(self, reason: str, screenshot_id: int,
                                user_id: str) -> dict:
        """
        Submits a complaint about a user's message.

        This method allows users to report inappropriate messages by
        specifying a reason
        and attaching a screenshot.

        Parameters:
            reason (str): The reason for the complaint.
            screenshot_id (int): The ID of the uploaded screenshot.
                Obtained from update_photo_server().
            user_id (str): The ID of the user being reported.

        Returns:
            dict: The server response to the complaint request.
        """
        complaint_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MAKE_COMPLAINT,
            PacketDataKeys.USER_OBJECT_ID: user_id,
            PacketDataKeys.REASON: reason,
            PacketDataKeys.SCREENSHOT: screenshot_id
            # Retrieved from update_photo_server()
        }
        await self.send_server(complaint_request)
        return await self.listen()

    async def get_private_messages(self, friend_id: str) -> List[ModelMessage]:
        """
        Retrieves the list of private messages exchanged with a specific
        friend.

        Parameters:
            friend_id (str): The unique identifier of the friend.

        Returns:
            List[ModelMessage]: A list of private messages.
        """
        private_messages_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_PRIVATE_CHAT,
            PacketDataKeys.FRIENDSHIP: friend_id
        }
        await self.send_server(private_messages_request)

        received_messages = await self.get_data(
            PacketDataKeys.PRIVATE_CHAT_LIST_MESSAGES
        )

        messages: List[ModelMessage] = [
            decode(json.dumps(message), type=ModelMessage)
            for message in received_messages[PacketDataKeys.MESSAGES]
        ]

        return messages

    async def get_rating(self, rating_type: RatingType = RatingType.AUTHORITY,
                     rating_mode: RatingMode = RatingMode.ALL_TIME) -> dict:
        """
        Retrieves the player rating based on the specified type and mode.

        Parameters:
            rating_type (RatingType): The type of rating to retrieve.
                Defaults to RatingType.AUTHORITY.
            rating_mode (RatingMode): The time period for the rating.
                Defaults to RatingMode.ALL_TIME.

        Returns:
            dict: A dictionary containing the rating data.
        """
        rating_query: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_RATING,
            PacketDataKeys.RATING_TYPE: rating_type,
            PacketDataKeys.RATING_MODE: rating_mode
        }
        await self.send_server(rating_query)
        return await self.get_data(PacketDataKeys.RATING)

    async def add_client_to_room_list(self) -> None:
        """
        Sends a request to add the client to the list of available rooms.

        This function allows the client to receive updates about available
        rooms
        in the game lobby.

        Returns:
            None
        """
        rooms_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_ROOMS_LIST
        }
        await self.send_server(rooms_request)

    async def join_global_chat(self) -> None:
        """
        Sends a request to join the global chat.

        This function allows the client to enter the global chat and receive
        messages from other users.

        Returns:
            None
        """
        chat_join_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_CHAT
        }
        await self.send_server(chat_join_request)

    async def leave_from_global_chat(self) -> None:
        """
        Leaves the global chat.

        This function removes the client from the global chat by calling the
        dashboard function.

        Returns:
            None
        """
        await self.dashboard()

    async def dashboard(self) -> None:
        """
        Sends a request to add the client to the dashboard.

        This function requests the server to place the client on the
        dashboard, typically used for accessing account-related information
        or lobby interactions.

        Returns:
            None
        """
        account_payload: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_DASHBOARD
        }
        await self.send_server(account_payload)

    @staticmethod
    def validate_message_content(content: str) -> bool:
        """
        Validates the message content to prevent sending empty messages.

        Parameters:
            content (str): The message content.

        Returns:
            bool: True if the message is valid, False otherwise.
        """
        if not content.strip():
            logging.warning(
                "Anti-ban protection: message not sent because it's empty.")
            return False
        return True

    async def send_message_friend(self, friend_id: str, content: str) -> None:
        """
        Sends a private message to a friend.

        Parameters:
            friend_id (str): The unique identifier of the friend.
            content (str): The message text to be sent.

        Returns:
            None

        Notes:
            - If the content is empty, the function prevents sending to
            avoid spam or bans.
        """
        if not self.validate_message_content(content):
            return

        message_data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.PRIVATE_CHAT_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.FRIENDSHIP: friend_id,
                PacketDataKeys.TEXT: content
            }
        }
        await self.send_server(message_data)

    async def send_message_room(self, content: str, room_id: str,
                                message_style: int = 0) -> None:
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
        if not self.validate_message_content(content):
            return

        message_data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ROOM_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.TEXT: content,
                PacketDataKeys.MESSAGE_STYLE: message_style
            },
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(message_data)

    async def send_message_global(self, content: str,
                                  message_style: int = 0) -> None:
        """
        Sends a message to the global chat.

        Parameters:
            content (str): The text of the message to be sent.
            message_style (int, optional): The style of the message.
            Defaults to 0.

        Returns:
            None

        Notes:
            - If the content is empty, the function prevents sending to
            avoid spam or bans.
        """
        if not self.validate_message_content(content):
            return

        message_data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.CHAT_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.TEXT: content,
                PacketDataKeys.MESSAGE_STYLE: message_style,
            }
        }
        await self.send_server(message_data)

    async def get_user(self, user_id: str) -> Optional[dict]:
        """
        Retrieves the profile data of a specific user.

        Parameters:
            user_id (str): The unique identifier of the user.

        Returns:
            Optional[dict]: The user's profile data if successfully
            retrieved, otherwise None.

        Raises:
            Exception: If an unexpected error occurs while fetching the data.

        Notes:
            - Logs an error if no data is returned.
            - Uses exception handling to catch and log potential failures.
        """
        user_payload: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_USER_PROFILE,
            PacketDataKeys.USER_OBJECT_ID: user_id
        }
        await self.send_server(user_payload)

        try:
            user_data = await self.get_data(PacketDataKeys.USER_PROFILE)
            if not user_data or user_data.get(
                    PacketDataKeys.TYPE) != PacketDataKeys.USER_SIGN_IN:
                logging.error("Get user data retrieval error")
                return None
            return user_data
        except Exception as e:
            logging.error(f"Error retrieving user {user_id} data: {e}",
                          exc_info=True)
            raise

    async def match_making_get_status(self) -> dict:
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
        return await self.get_data("mmms")

    async def users_waiting_count(self, players_size: int = 8) -> dict:
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
            PacketDataKeys.TYPE: "mmguiabk",
            "mmbpa": players_size
        }
        await self.send_server(users_in_wait_request)
        return await self.get_data("mmuiabk")

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
            "mmbpa": players_size
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
