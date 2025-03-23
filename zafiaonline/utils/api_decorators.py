import functools
import logging
from typing import Callable, Union

from zafiaonline.structures import ModelUser
from zafiaonline.structures.enums import MessageType


class ApiDecorators:
    def __init__(self):
        pass

    @staticmethod
    def fetch_player_id(func: Callable):
        """Декоратор для поиска player_id, если он не передан."""

        @functools.wraps(func)
        async def wrapper(cls, player_id, player_nickname, *args, **kwargs):
            from zafiaonline.main import Client, PacketDataKeys
            client = Client()
            if player_id is None:
                result = await client.search_player(player_nickname)
                users = result[PacketDataKeys.USERS]
                if not users:
                    raise ValueError(
                        f"Player with nickname '{player_nickname}' not found")
                user = users[0]
                player_id = user[PacketDataKeys.OBJECT_ID]
            return await func(cls, player_id, player_nickname, *args, **kwargs)

        return wrapper

    @staticmethod
    def login_required(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> Union[ModelUser, bool]:
            email = kwargs.get("email", "")
            password = kwargs.get("password", "")
            token = kwargs.get("token", "")
            user_id = kwargs.get("user_id", "")

            if not ((email and password) or not (token and user_id)):
                logging.error("Не все данные для входа были введены")
                return False

            return await func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def requires_room_check(func: Callable):
        from zafiaonline.main import Client, PacketDataKeys
        client = Client()
        @functools.wraps(func)
        async def wrapper(self, room_id: str, *args, **kwargs):
            profile = await client.get_user(self.client.user.user_id)
            user_room_id = profile.get(PacketDataKeys.ROOM, {}).get(
                PacketDataKeys.OBJECT_ID)

            if not user_room_id:
                raise ValueError("Пользователь не находится в комнате")

            if user_room_id != room_id:
                raise ValueError(
                    f"Пользователь находится в другой комнате "
                    f"(ID: {user_room_id}), а не в {room_id}")

            return await func(self, room_id, *args, **kwargs)

        return wrapper

    @staticmethod
    def room_participation_required(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, room_id: str, *args, **kwargs) -> None:
            decorators = ApiDecorators()
            if not decorators.requires_room_check(
                    room_id):  # Проверяем, находится ли пользователь в комнате
                raise PermissionError("User is not in the room")

            return await func(self, room_id, *args, **kwargs)

        return wrapper

    @staticmethod
    def extract_message(func: Callable):
        """Декоратор для извлечения текста сообщения и информации
        о пользователе"""

        @functools.wraps(func)
        async def wrapper(self, result, *args, **kwargs):
            from zafiaonline.main import PacketDataKeys
            if result.get(PacketDataKeys.TYPE) == PacketDataKeys.MESSAGE:
                message = result.get(PacketDataKeys.MESSAGE, {})
                message_type = message.get(PacketDataKeys.MESSAGE_TYPE)

                if message_type == MessageType.TEXT:  # Текстовое сообщение
                    user = message.get(PacketDataKeys.USER, {})
                    content = message.get(PacketDataKeys.TEXT, "")

                    # Сохраняем информацию о пользователе
                    self.user_id = user.get(PacketDataKeys.OBJECT_ID)
                    self.user_name = user.get(PacketDataKeys.USERNAME)
                    self.sex = user.get(PacketDataKeys.SEX)

                    return await func(self, content, *args, **kwargs)

            return None  # Если сообщение не соответствует критериям

        return wrapper
