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
from zafiaonline.web import WebClient
from zafiaonline.websocket_module import Websocket

logging.basicConfig(level=logging.INFO)

class Client(Websocket, WebClient):
    def __init__(self, proxy: Optional[list] = None, debug:
    Optional[bool] = False) -> None:
        self.proxy = proxy if proxy is not None else []
        self.debug = debug
        self.token: Optional[str] = None
        self.id: Optional[str] = None
        self.md5hash = Md5()
        self.user: ModelUser = ModelUser()
        self.server_config: ModelServerConfig = ModelServerConfig()
        self.address:str = "37.143.8.68"
        self.port:str = "7090"
        self.web_port:str = "8008"
        self.rest_address \
            = f"http://{self.address}:{self.web_port}"
        super().__init__(self)

    async def sign_in(self, email: str = "", password: str = "",
                token: str = "", user_id: str = "") -> Union[ModelUser, bool]:
        if email == "email":
            logging.warning(f"your email is literally {email} "
                         f"please change your config if your nickname"
                         f" isn't email")
        """
        Sign in into user

        **Parameters**
            - **email** : Email of the user
            - **password** : Password of the user
            - **token** : Token of the user
        **Returns**
            - **Success** : list
        """
        if not self.ws:
            await self.create_connection()
        data: dict = {
            PacketDataKeys.DEVICE_ID: token_hex(10),
            PacketDataKeys.TYPE: PacketDataKeys.SIGN_IN,
            PacketDataKeys.EMAIL: email,
            PacketDataKeys.PASSWORD: self.md5hash.md5salt(password or
                                                                ""),
            PacketDataKeys.OBJECT_ID: user_id,
            PacketDataKeys.TOKEN: token,
        }
        await self.send_server(data)
        data = await self.get_data(PacketDataKeys.USER_SIGN_IN)
        if data[PacketDataKeys.TYPE] != PacketDataKeys.USER_SIGN_IN:
            logging.debug("sign in data get error")
            return False
        self.user = decode(json.dumps(data[PacketDataKeys.USER]),
                           type=ModelUser)
        self.server_config = decode(json.dumps(data
                                               [PacketDataKeys.SERVER_CONFIG])
                                    , type=ModelServerConfig)
        self.token = self.user.token
        self.id = self.user.user_id
        return self.user
        
    async def get_rating(self, rating_type: RatingType = RatingType.AUTHORITY,
                   rating_mode: RatingMode = RatingMode.ALL_TIME) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_RATING,
            PacketDataKeys.RATING_TYPE: rating_type,
            PacketDataKeys.RATING_MODE: rating_mode
        }
        await self.send_server(data)
        return await self.get_data(PacketDataKeys.RATING)

    async def kick_user_vote(self, room_id: str, value: bool = True) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.KICK_USER_VOTE,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.VOTE: value
        }
        await self.send_server(data)
        
    async def kick_user(self, user_id: str, room_id: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.KICK_USER,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.USER_OBJECT_ID: user_id
        }
        await self.send_server(data)

    async def username_set(self, nickname: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USERNAME_SET,
            PacketDataKeys.USERNAME: nickname
        }
        await self.send_server(data)

    async def select_language(self, language: Languages = Languages.RUSSIAN)\
            -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USER_SET_SERVER_LANGUAGE,
            PacketDataKeys.SERVER_LANGUAGE: language
        }
        await self.send_server(data)

    async def vote_player_list(self, user_id: str, room_id: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.VOTE_PLAYER_LIST,
            PacketDataKeys.USER_OBJECT_ID: user_id,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(data)

    async def create_room(self, selected_roles: Optional[List[Roles]] = None,
                    title: str = "", max_players: int = 8,
                    min_players: int = 5, password: str = "",
                    min_level: int = 1,
                    vip_enabled: bool = False) -> ModelRoom:
        selected_roles = selected_roles or [0]
        request_data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ROOM_CREATE,
            PacketDataKeys.ROOM: {
                PacketDataKeys.MIN_PLAYERS: min_players,
                PacketDataKeys.MAX_PLAYERS: max_players,
                PacketDataKeys.PASSWORD: self.md5hash.md5salt(password
                                                                    or ""),
                PacketDataKeys.DEVICE_ID: 0,
                PacketDataKeys.SELECTED_ROLES: selected_roles,
                PacketDataKeys.MIN_LEVEL: min_level,
                PacketDataKeys.TITLE: title,
                PacketDataKeys.VIP_ENABLED: vip_enabled
            }
        }
        await self.send_server(request_data)
        data = await self.get_data(PacketDataKeys.ROOM_CREATED)
        if data[PacketDataKeys.TYPE] != PacketDataKeys.ROOM_CREATED:
            await self.send_server(request_data)
            data = await self.get_data(PacketDataKeys.ROOM_CREATED)
            logging.debug("receiver")
        return decode(json.dumps(data[PacketDataKeys.ROOM]), type=ModelRoom)

    async def friend_list(self) -> List[ModelFriend]:
        data: dict = {
            PacketDataKeys.TYPE:  PacketDataKeys.ADD_CLIENT_TO_FRIENDSHIP_LIST
        }
        await self.send_server(data)
        data = await self.get_data(PacketDataKeys.FRIENDSHIP_LIST)
        friends: List[ModelFriend] = []
        for friend in data[PacketDataKeys.FRIENDSHIP_LIST]:
            friends.append(decode(json.dumps(friend), type=ModelFriend))
        return friends
    
    async def search_player(self, nickname:str) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.SEARCH_USER,
            PacketDataKeys.SEARCH_TEXT: nickname
        }
        await self.send_server(data)
        return await self.get_data(PacketDataKeys.SEARCH_USER)

    async def remove_friend(self, friend_id: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.REMOVE_FRIEND,
            PacketDataKeys.FRIEND_USER_OBJECT_ID: friend_id
        }
        await self.send_server(data)

    async def update_photo(self, file: bytes) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.UPLOAD_PHOTO,
            PacketDataKeys.FILE: base64.encodebytes(file).decode()
        }
        await self.send_server(data)

    async def update_photo_server(self, file: bytes) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.UPLOAD_SCREENSHOT,
            PacketDataKeys.FILE: base64.encodebytes(file).decode()
        }
        await self.send_server(data)

    async def update_sex(self, sex: Sex) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USER_CHANGE_SEX,
            PacketDataKeys.SEX: sex
        }
        await self.send_server(data)
        return await self.listen()

    async def message_complaint(self, reason: str,
                                screenshot_id: int, user_id: str) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MAKE_COMPLAINT,
            PacketDataKeys.USER_OBJECT_ID: user_id,
            PacketDataKeys.REASON: reason,
            PacketDataKeys.SCREENSHOT: screenshot_id  # get from
                                                      # update_photo_server()
        }
        await self.send_server(data)
        return await self.listen()

    async def get_private_messages(self, friend_id: str) -> List[ModelMessage]:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_PRIVATE_CHAT,
            PacketDataKeys.FRIENDSHIP: friend_id
        }
        await self.send_server(data)
        data = await self.get_data(PacketDataKeys.PRIVATE_CHAT_LIST_MESSAGES)
        messages: List[ModelMessage] = []
        for message in data[PacketDataKeys.MESSAGES]:
            messages.append(decode(json.dumps(message), type=ModelMessage))
        return messages

    async def remove_player(self, room_id: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.REMOVE_PLAYER,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(data)
    

    async def create_player(self, room_id: str, room_model_type:
    RoomModelType = RoomModelType.NOT_MATCHMAKING_MODE) -> Optional[dict]:
        """
        need run after join_room()
        :param room_model_type: room type
        :param room_id: id into room
        :return: None or Players in room
        """
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.CREATE_PLAYER,
            PacketDataKeys.ROOM_MODEL_TYPE: room_model_type,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(data)
        return await self.get_data(PacketDataKeys.ROOM_STATISTICS)

    async def join_room(self, room_id: str, password: str = "") -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ROOM_ENTER,
            PacketDataKeys.ROOM_PASS: self.md5hash.md5salt(password)
            if password else "",
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(data)
        

    async def leave_room(self, room_id: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.REMOVE_PLAYER,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(data)

    async def role_action(self, user_id: str, room_id: str,
                    room_model_type: RoomModelType =
                    RoomModelType.NOT_MATCHMAKING_MODE) -> None:
        """
        is used when using a role and voting when a game is started
        """
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ROLE_ACTION,
            PacketDataKeys.USER_OBJECT_ID: user_id,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.ROOM_MODEL_TYPE: room_model_type
        }
        await self.send_server(data, True)

    async def add_client_to_rooms_list(self) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_ROOMS_LIST
        }
        await self.send_server(data)

    async def join_global_chat(self) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_CHAT
        }
        await self.send_server(data)

    async def leave_from_global_chat(self) -> None:
        await self.dashboard()

    async def dashboard(self) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_DASHBOARD
        }
        await self.send_server(data)

    async def send_message_friend(self, friend_id: str, content: str) -> None:
        if content == "":
            logging.warning("anti-ban protection, dont send message")
            return
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.PRIVATE_CHAT_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.FRIENDSHIP: friend_id,
                PacketDataKeys.TEXT: content
            }
        }
        await self.send_server(data)

    async def send_message_room(self, content: str, room_id: str,
                          message_style: int = 0) -> None:
        if content == "":
            logging.warning("anti-ban protection, dont send message")
            return
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ROOM_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.TEXT: content,
                PacketDataKeys.MESSAGE_STYLE: message_style
            },
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        await self.send_server(data)

    async def send_message_global(self, content: str, message_style: int = 0)\
            -> None:
        """
        Send message to global chat

        **Parameters**
            - **content** - Content of message
            - **message_style** - Style of message
        """
        if content == "":
            logging.warning("ant-ban protection, dont send message")
            return
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.CHAT_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.TEXT: content,
                PacketDataKeys.MESSAGE_STYLE: message_style,
            }
        }
        await self.send_server(data)

    async def get_user(self, user_id: str) -> Optional[dict]:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_USER_PROFILE,
            PacketDataKeys.USER_OBJECT_ID: user_id
        }
        await self.send_server(data)
        try:
            return await self.get_data(PacketDataKeys.USER_PROFILE)
        except Exception as e:
            logging.error(f"get user {user_id} data error {e}")
            return None

    async def match_making_get_status(self) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MATCH_MAKING_GET_STATUS
        }
        await self.send_server(data)
        return await self.get_data("mmms")

    async def match_making_get_users_waits_count(self, players_size: int = 8)\
            -> dict:
        data: dict = {
            PacketDataKeys.TYPE: "mmguiabk",
            "mmbpa": players_size
        }
        await self.send_server(data)
        return await self.get_data("mmuiabk")

    async def match_making_add_user(self, players_size: int = 8) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MATCH_MAKING_ADD_USER,
            "mmbpa": players_size
        }
        await self.send_server(data)

    async def match_making_remove_user(self) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MATCH_MAKING_REMOVE_USER
        }
        await self.send_server(data)

    async def remove_type(self, room_model_type: RoomModelType =
    RoomModelType.NOT_MATCHMAKING_MODE) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GIVE_UP,
            PacketDataKeys.ROOM_MODEL_TYPE: room_model_type
        }
        await self.send_server(data)

    async def give_up(self, room_id: str, room_model_type: RoomModelType =
    RoomModelType.NOT_MATCHMAKING_MODE) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GIVE_UP,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.ROOM_MODEL_TYPE: room_model_type
        }
        await self.send_server(data)
