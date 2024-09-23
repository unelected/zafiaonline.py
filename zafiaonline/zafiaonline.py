# import socket не используется
import json
import threading
import base64
import time
# import socks
from .utils.md5hash import Md5
# from .structures.packet_data_keys import PacketDataKeys
from .structures.models import ModelUser, ModelServerConfig, ModelRoom, ModelFriend, ModelMessage
from .structures.enums import Languages, Roles, Sex, RatingMode, RatingType
from typing import List
from secrets import token_hex
from msgspec.json import decode
from .web import WebClient
from queue import Queue
from websocket import create_connection


class Client(WebClient):
    def __init__(self,
                 debug: bool = False):  # кому нужен прокси в мафке? proxy.list = {ip:pass}, грубо упрощено. """proxy: list = None, """ было после self,
        self.token: str = None
        self.id: str = None
        self.md5hash = Md5()  # .utils.md5hash
        self.user: ModelUser = ModelUser()  # .structures.models
        self.server_config: ModelServerConfig = ModelServerConfig()
        self.address = "37.143.8.68"
        self.port = "7090"
        self.alive = True
        self.data = Queue()
        self.ws = None
        super().__init__(self)
        self.create_connection()

    def sign_in(self, email: str = "", password: str = "", token: str = "",
                user_id: str = "") -> ModelUser:
        """
        Sign in into user

        **Parametrs**
            - **email** : Email of the user
            - **password** : Password of the user
            - **token** : Token of the user
        **Returns**
            - **Success** : list
        """
        data = {
            "d": token_hex(10),  # DEVICE_ID_KEY
            "ty": "sin"  # SIGN_IN_KEY
        }
        data["e"] = email
        data["pw"] = self.md5hash.md5Salt(password) if password else ""
        data["o"] = user_id
        data["t"] = token
        self.send_server(data)
        time.sleep(.5)
        data = self._get_data("usi")
        while data["ty"] != "usi":  # USER_SIGN_IN_KEY
            return False
        self.user = decode(json.dumps(data["uu"]), type=ModelUser)
        self.server_config = decode(json.dumps(data["scfg"]),
                                    type=ModelServerConfig)  # SERVER_CONFIG (PacketDataKeys)
        self.token = self.user.token
        self.id = self.user.user_id
        return self.user

    def get_rating(self, rating_type: RatingType = RatingType.AUTHORITY, rating_mode: RatingMode = RatingMode.ALL_TIME):
        data = {
            "ty": "gr",  # GET_RATING_KEY
            "rt": rating_type,  # RATING_TYPE_KEY
            "rmd": rating_mode  # RATING_MODE_KEY
        }
        self.send_server(data)
        return self._get_data("rtg")  # RATING_KEY

    def kick_user_vote(self, room_id: str, value: bool = True) -> None:
        data = {
            "ty": "kuv",  # KICK_USER_VOTE_KEY
            "ro": room_id,
            "v": value
            # отсутствует
        }
        self.send_server(data)

    def kick_user(self, user_id: str, room_id: str) -> None:
        data = {
            "ty": "ku",  # KICK_USER_KEY
            "ro": room_id, # USER_OBJECT_ID_KEY
            "uo": user_id # ROOM_OBJECT_ID_KEY
        }
        self.send_server(data)

    def rename(self, nickname: str) -> None:  # смена ника
        data = {
            "ty": "uns",  # USERNAME_SET_KEY
            "u": nickname  # USERNAME_KEY
        }
        self.send_server(data)

    def select_language(self, language: Languages = Languages.RUSSIAN) -> None:
        data = {
            "ty": "usls",  # USER_SET_SERVER_LANGUAGE_KEY
            "slc": language  # SERVER_LANGUAGE_KEY
        }
        self.send_server(data)

    def vote_player_list(self, user_id: str, room_id: str) -> None:
        data = {
            "ty": "vpl",  # нет в PacketDataKeys
            "uo": user_id,  # USER_OBJECT_ID_KEY
            "ro": room_id  # ROOM_OBJECT_ID_KEY
        }
        self.send_server(data)

    def create_room(self, selected_roles: List[Roles] = [0], title: str = "", max_players: int = 8,
                    min_players: int = 5, password: str = "", min_level: int = 1,
                    vip_enabled: bool = False) -> ModelRoom:
        request_data = {
            "ty": "rc",  # ROOM_CREATE_KEY
            "rr": {  # ROOM_KEY
                "mnp": min_players,  #  MIN_PLAYERS_KEY
                "mxp": max_players,  # MAX_PLAYERS_KEY
                "pw": self.md5hash.md5Salt(password) if password else "",  # PASSWORD_KEY
                "d": 1337,
                # DEVICE_ID_KEY
                "sr": selected_roles,  # SELECTED_ROLES_KEY
                "mnl": min_level,  # MIN_LEVEL_KEY
                "tt": title,  # TITLE_KEY
                "venb": vip_enabled  # VIP_ENABLED_KEY
            }
        }
        self.send_server(request_data)
        time.sleep(1)  # zzzzzz
        data = self._get_data("rcd")  # "ROOM_CREATED_KEY"
        while data["ty"] != "rcd":  # "ROOM_CREATED_KEY"
            self.send_server(request_data)
            time.sleep(.5)  # zzzzzz
            data = self._get_data("rcd")  # ROOM_CREATED_KEY
            print("rerecvier")
        return decode(json.dumps(data["rr"]), type=ModelRoom)  # ROOM_KEY

    def friend_list(self) -> List[ModelFriend]:
        data = {
            "ty": "acfl"  # ADD_CLIENT_TO_FRIENDSHIP_LIST_KEY
        }
        self.send_server(data)
        data = self._get_data("frl")  # FRIENDSHIP_LIST_KEY
        friends: List[ModelFriend] = []
        for friend in data["frl"]:  # FRIENDSHIP_LIST_KEY
            friends.append(decode(json.dumps(friend), type=ModelFriend))
        return friends

    def remove_friend(self, friend_id: str) -> None:
        data = {
            "ty": "rf",  # REMOVE_FRIEND_KEY
            "f": friend_id
        }
        self.send_server(data)

    def update_photo(self, file: bytes) -> None:
        data = {
            "ty": "upp",  # ЗАГРУЗКА фотки профиля UPLOAD_PHOTO_KEY
            "f": base64.encodebytes(file).decode()
            # FRIEND_USER_OBJECT_ID_KEY
        }
        self.send_server(data)

    def update_photo_server(self, file: bytes) -> None:
        data = {
            "ty": "ups",  # UPLOAD_SCREENSHOT_KEY
            "f": base64.encodebytes(file).decode()  # FRIEND_USER_OBJECT_ID_KEY
        }
        self.send_server(data)

    def update_sex(self, sex: Sex) -> dict:
        data = {
            "ty": "ucs",  # USER_CHANGE_SEX_KEY
            "s": sex
        }
        self.send_server(data)
        return self.listen()

    def message_complaint(self, reason: str, screenshot_id: int, user_id: str) -> dict:
        data = {
            "ty": "mc",  # MAKE_COMPLAINT_KEY
            "uo": user_id,
            "r": reason,
            #  REASON_KEY
            "sc": screenshot_id  # get from update_photo_server()
        }
        self.send_server(data)
        return self.listen()

    def get_messages(self, friend_id: str) -> List[ModelMessage]:
        data = {
            "ty": "acpc",  # ADD_CLIENT_TO_PRIVATE_CHAT_KEY
            "fp": friend_id  # FRIENDSHIP_KEY
        }
        self.send_server(data)
        data = self._get_data(
            "pclms")  # этого значения нет в remove_player, в декомпилированной зафии оно лежит в smali/com/tokarev/mafia/privatechat/presentation/PrivateChatFragment.smali
        messages: List[ModelMessage] = []
        for message in data["ms"]:  # MESSAGES_KEY
            messages.append(decode(json.dumps(message), type=ModelMessage))  # потом
        return messages

    def remove_player(self, room_id: str) -> None:
        data = {
            "ty": "rp",  # REMOVE_PLAYER_KEY
            "ro": room_id # ROOM_OBJECT_ID_KEY
        }
        self.send_server(data)

    def create_player(self, room_id: str) -> None:
        """
        need run after join_room()

        :param room_id: id into room
        :return: None
        """
        data = {
            "ty": "cp",  # CREATE_PLAYER_KEY
            "ro": room_id # ROOM_OBJECT_ID_KEY
        }
        self.send_server(data)
        return self._get_data('pls')  # PLAYERS_KEY

    def join_room(self, room_id: str, password: str = "") -> None:
        data = {
            "ty": "re",  # ROOM_ENTER_KEY
            "psw": self.md5hash.md5Salt(password) if password else "",
            "ro": room_id
        }
        self.send_server(data)

    def leave_room(self, room_id: str) -> None:  # ничем не отличается от remove_player
        data = {
            "ty": "rp",  # REMOVE_PLAYER_KEY
            "ro": room_id # ROOM_OBJECT_ID_KEY
        }
        self.send_server(data)

    def role_action(self, user_id: str, room_id: str) -> None:
        data = {
            "ty": "ra",  # использовать спобоность роли (сесть) ROLE_ACTION_KEY
            "uo": user_id,  # айди жертвы
            "ro": room_idA  # айди румы
        }
        self.send_server(data, True)

    def acrl(self) -> None:
        data = {
            "ty": "acrl"
            # ADD_CLIENT_TO_ROOMS_LIST_KEY
        }
        self.send_server(data)

    def join_global_chat(self) -> None:
        data = {
            "ty": "acc"  # токен ADD_CLIENT_TO_CHAT_KEY
        }
        self.send_server(data)

    def leave_from_global_chat(self) -> None:
        self.dashboard()  # лив с чата через топ

    def dashboard(self) -> None:
        data = {
            "ty": "acd"  # ADD_CLIENT_TO_DASHBOARD_KEY
        }
        self.send_server(data)

    def send_message_friend(self, friend_id: str, content: str) -> None:
        data = {
            "ty": "pmc",  # PRIVATE_CHAT_MESSAGE_CREATE_KEY
            "m": {
                # в PacketDataKeys нет этого значения
                "fp": friend_id,  # FRIENDSHIP_KEY
                "tx": content  # TEXT_KEY
            }
        }
        self.send_server(data)

    def send_message_room(self, content: str, room_id: str, message_style: int = 0) -> None:
        data = {
            "ty": "rmc",  # ROOM_MESSAGE_CREATE_KEY
            "m": {
                "tx": content,  # TEXT_KEY
                "mstl": message_style  # MESSAGE_STYLE_KEY
            },
            "ro": room_id
        }
        self.send_server(data)

    def send_message_global(self, content: str, message_style: int = 0):
        """
        Send message to global chat

        **Parametrs**
            - **content** - Content of message
            - **message_style** - Style of message
        """
        data = {
            "ty": "cmc",  # CHAT_MESSAGE_CREATE_KEY
            "m": {
                "tx": content,  # TEXT_KEY
                "mstl": message_style,  # MESSAGE_STYLE_KEY
            }
        }
        self.send_server(data)

    def get_user(self, user_id: str) -> dict:
        data = {
            "ty": "gup",  # GET_USER_PROFILE_KEY  не путать с USER_PROFILE_KEY
            "uo": user_id
        }
        self.send_server(data)
        return self._get_data("uup")  # USER_PROFILE_KEY не путать с GET_USER_PROFILE_KEY

    def create_connection(self) -> None:
        self.ws = create_connection(f"ws://{self.address}:{self.port}")
        self.listener = threading.Thread(target=self.__listener).start()

    def __listener(
            self) -> None:
        while self.alive:
            try:
                r = self.ws.recv()
                self.data.put(r)
                self.ws.ping()
            except Exception as e:
                print("error get data")
                return
        pass

    def send_server(self, data: dict, remove_token_from_object: bool = False) -> None:
        if not remove_token_from_object:
            data["t"] = self.token
            data["uo"] = data.get("uo",
                                  self.id)  # мой недокод
            """ data[PacketDataKeys.TOKEN_KEY] = self.token #t
                data[PacketDataKeys.USER_OBJECT_ID_KEY] = data.get(PacketDataKeys.USER_OBJECT_ID_KEY, self.id) #uo"""
        self.ws.send((json.dumps(data) + "\n").encode())

    def listen(self) -> dict:
        response = self.data.get(timeout=5)
        return json.loads(response)

    def _get_data(self, type: str) -> dict:
        data = self.listen()
        while self.alive:
            if data.get("ty") in [type, "empty",
                                  "ero"]:  # ERROR_OCCUR_KEY -- "ero"
                return data
            data = self.listen()

    def __del__(self):
        self.alive = False
        self.ws.close()
