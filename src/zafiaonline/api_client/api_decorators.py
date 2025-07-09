import functools

from typing import Callable, Union

from zafiaonline.structures import ModelUser
from zafiaonline.structures.enums import MessageType
from zafiaonline.utils.exceptions import LoginError
from zafiaonline.utils.logging_config import logger


class ApiDecorators:
    def __init__(self):
        pass

    @staticmethod
    def fetch_player_id(func: Callable):
        """Decorator to search for player_id if it is not passed in."""

        @functools.wraps(func)
        async def wrapper(cls, player_id, player_nickname, *args, **kwargs):
            from zafiaonline.api_client.player_methods import (Players,
                                                               PacketDataKeys)
            players: "Players" = Players()

            if player_id is None:
                result: dict | None = await players.search_player(player_nickname)
                if result is None:
                    raise ValueError
                users: dict = result[PacketDataKeys.USERS]
                if not users:
                    raise ValueError(
                        f"Player with nickname '{player_nickname}' not found")
                user: dict = users[0]
                player_id: str = user[PacketDataKeys.OBJECT_ID]
            return await func(cls, player_id, player_nickname, *args, **kwargs)

        return wrapper

    @staticmethod
    def login_required(func: Callable):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Union[ModelUser, bool]:
            email: str = kwargs.get("email", "")
            password: str = kwargs.get("password", "")
            token: str = kwargs.get("token", "")
            user_id: str = kwargs.get("user_id", "")

            if not email and password:
                if not token and user_id:
                    logger.error("Not all login details have been entered")
                    raise LoginError

            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def requires_room_check(func: Callable):
        from zafiaonline.api_client.player_methods import (Players,
                                                           PacketDataKeys)
        players = Players()
        @functools.wraps(func)
        async def wrapper(self, room_id: str, *args, **kwargs):
            profile: dict | None = await players.get_user(self.client.user.user_id)
            if profile is None:
                raise ValueError
            user_room_id: str = profile.get(PacketDataKeys.ROOM, {}).get(
                PacketDataKeys.OBJECT_ID)

            if not user_room_id:
                raise ValueError("The user is not in the room")

            if user_room_id != room_id:
                raise ValueError(
                    f"The user is in another room "
                    f"(ID: {user_room_id}), but not in {room_id}")

            return await func(self, room_id, *args, **kwargs)

        return wrapper

    """@staticmethod
    def room_participation_required(func: Callable):
        @functools.wraps(func)
        def wrapper(self, room_id: str, *args, **kwargs) -> None:
            if not self.requires_room_check(
                    room_id):  # Проверяем, находится ли пользователь в комнате
                raise PermissionError("User is not in the room")

            return func(self, room_id, *args, **kwargs)

        return wrapper"""

    @staticmethod
    def extract_message(func: Callable):
        """Decorator for extracting message text and information about the
        user"""

        @functools.wraps(func)
        def wrapper(self, result, *args, **kwargs):
            from zafiaonline.structures.packet_data_keys import PacketDataKeys
            if result.get(PacketDataKeys.TYPE) == PacketDataKeys.MESSAGE:
                message: dict = result.get(PacketDataKeys.MESSAGE, {})
                message_type: int | None = message.get(PacketDataKeys.MESSAGE_TYPE)

                if message_type == MessageType.MAIN_TEXT:
                    user: dict = message.get(PacketDataKeys.USER, {})
                    content: str = message.get(PacketDataKeys.TEXT, "")

                    # Save user data
                    self.user_id = user.get(PacketDataKeys.OBJECT_ID)
                    self.user_name = user.get(PacketDataKeys.USERNAME)
                    self.sex = user.get(PacketDataKeys.SEX)

                    return func(self, content, *args, **kwargs)

            return None

        return wrapper
