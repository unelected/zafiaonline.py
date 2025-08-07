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
Utility decorators for user validation and message handling in MafiaOnline.

This module contains decorators used to simplify validation logic when handling
user messages and checking room participation in the MafiaOnline API client.

Typical usage example:
    @extract_message
    async def handle_text(self, content: str):
        print(f"User said: {content}")

    @room_participation_required
    async def send_to_room(self, room_id: str):
        pass
"""
import functools

from typing import TYPE_CHECKING, Awaitable, Callable, Union, Any

if TYPE_CHECKING:
    from zafiaonline.api_client.user_methods import Auth

from zafiaonline.structures import ModelUser
from zafiaonline.structures.enums import MessageType
from zafiaonline.utils.exceptions import LoginError
from zafiaonline.utils.logging_config import logger


class ApiDecorators:
    """
    A collection of static decorator methods for API request handling and validation.

    This class provides reusable decorators to be applied to asynchronous methods in
    API client classes. These decorators add functionality such as user authentication,
    player ID resolution, room validation, and packet message extraction. They help
    enforce consistency and reduce boilerplate across API interactions.
    """
    @staticmethod
    def fetch_player_id(func: Callable) -> Callable:
        """
        Decorator that ensures a valid `player_id` is passed to the decorated async method.

        If `player_id` is None, attempts to resolve it using `player_nickname` via an API
        call to the Players service. Raises an error if both values are missing or the
        nickname cannot be resolved.

        Args:
            func (Callable): The asynchronous function to decorate. Must accept the
                following arguments in order: cls, player_id, player_nickname, auth, *args, **kwargs.

        Returns:
            Callable: The decorated asynchronous function with resolved `player_id`.

        Raises:
            AttributeError: If both `player_id` and `player_nickname` are None.
            ValueError: If no user is found for the given `player_nickname`.
        """
        @functools.wraps(func)
        async def wrapper(cls, player_id: str | None,
                          player_nickname: str | None, auth: "Auth", *args, **kwargs) -> Awaitable[Any]:
            """
            Resolves `player_id` via `player_nickname` if not provided and calls the wrapped function.

            If `player_id` is None, this function uses the Players API with `auth` to
            look up the player by `player_nickname`. Raises an error if both are missing
            or if the lookup fails to find a user. Otherwise, it invokes `func` with
            a guaranteed non-None `player_id`.

            Args:
                cls: The class or instance for the method call.
                player_id (str | None): Unique identifier of the player, if known.
                player_nickname (str | None): Nickname to use for lookup when `player_id` is None.
                auth (Auth): Authentication object for API access.
                *args: Additional positional arguments passed to the wrapped function.
                **kwargs: Additional keyword arguments passed to the wrapped function.

            Returns:
                Awaitable[Any]: The result of calling the wrapped asynchronous function `func`.

            Raises:
                AttributeError: If both `player_id` and `player_nickname` are None.
                ValueError: If `player_nickname` lookup returns no matching player.
            """
            if TYPE_CHECKING:
                from zafiaonline.api_client.player_methods import Players
            from zafiaonline.structures.packet_data_keys import PacketDataKeys
            players: "Players" = Players(auth)

            if player_id is None:
                if player_nickname is None:
                    raise AttributeError("No nickname and no id")
                result: dict | None = await players.search_player(player_nickname)
                if result is None:
                    raise ValueError
                users: dict = result[PacketDataKeys.USERS]
                if not users:
                    raise ValueError(
                        f"Player with nickname '{player_nickname}' not found")
                user: dict = users[0]
                player_id = str(user[PacketDataKeys.OBJECT_ID])
            return await func(cls, player_id, player_nickname, *args, **kwargs)

        return wrapper

    @staticmethod
    def login_required(func: Callable) -> Callable:
        """
        Decorator that ensures sufficient login credentials are provided.

        This decorator checks that required authentication details (email, password,
        token, user_id) are present in keyword arguments. If essential login
        information is missing, it raises a `LoginError`.

        Args:
            func (Callable): The function requiring login validation.

        Returns:
            Callable: Wrapped function that raises `LoginError` if login credentials
            are incomplete, or otherwise proceeds with the original function call.

        Raises:
            LoginError: If neither a valid (email + password) nor (token + user_id)
            pair is provided.
        """
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> Union[ModelUser, bool]:
            """
            Validates presence of login credentials before executing the function.

            This function checks whether sufficient login credentials have been passed
            via keyword arguments. It requires either both `email` and `password`,
            or both `token` and `user_id`. If neither pair is fully provided,
            it raises a `LoginError`.

            Args:
                self: The class instance to which the method belongs.
                *args: Positional arguments passed to the original function.
                **kwargs: Keyword arguments expected to include login credentials.
                    email (str): User's email address.
                    password (str): User's password.
                    token (str): Authentication token.
                    user_id (str): User's unique identifier.

            Returns:
                Union[ModelUser, bool]: Result of the decorated function if login data
                is valid.

            Raises:
                LoginError: If required login credentials are missing.
            """
            email: str = kwargs.get("email", "")
            password: str = kwargs.get("password", "")
            token: str = kwargs.get("token", "")
            user_id: str = kwargs.get("user_id", "")

            if not email and password:
                if not token and user_id:
                    logger.error("Not all login details have been entered")
                    raise LoginError

            return await func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def requires_room_check(auth: "Auth") -> Callable:
        """
        Decorator to ensure the user is in the specified room before executing the function.

        This decorator checks the user's current room via the API. If the user is not in any room,
        or is in a different room than the one passed to the function, it raises a ValueError.

        Args:
            func (Callable): The asynchronous function to wrap.
            auth (Auth): The authentication object used to retrieve user information.

        Returns:
            Callable: The wrapped asynchronous function that performs a room consistency check.

        Raises:
            ValueError: If the user is not in a room, or if the room does not match the given room_id.
        """
        from zafiaonline.api_client.player_methods import (Players,
                                                           PacketDataKeys)
        players = Players(auth)

        async def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(self, room_id: str, *args, **kwargs) -> Awaitable[Any]:
                """
                Validates that the user is in the expected room before executing the function.

                This decorator fetches the current user's profile and checks whether the user
                is present in a room. If so, it ensures the user's room ID matches the expected
                `room_id`. If not, the function will raise an error.

                Args:
                    self: The instance the method is bound to.
                    room_id (str): The expected room ID the user must be in.
                    *args: Additional positional arguments passed to the decorated function.
                    **kwargs: Additional keyword arguments passed to the decorated function.

                Returns:
                    Awaitable[Any]: The result of the decorated asynchronous function.

                Raises:
                    ValueError: If the user is not in a room or is in a different room than `room_id`.
                """
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
        return decorator

    #TODO: @unelected - refactor to default func
    """@staticmethod
    def room_participation_required(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, room_id: str, *args, **kwargs) -> Union[Callable, PermissionError]:
            if not self.requires_room_check(
                    room_id):  # Проверяем, находится ли пользователь в комнате
                raise PermissionError("User is not in the room")

            return func(self, room_id, *args, **kwargs)

        return wrapper"""

    @staticmethod
    def extract_message(func: Callable) -> Callable:
        """
        Processes an incoming packet and passes the message text to the function if it is a main text message.

        Extracts the message content and user information from the packet structure if the packet type is
        MESSAGE and the message type is MAIN_TEXT. Stores the user ID, username, and sex in `self`.

        Args:
            func: An asynchronous function expecting arguments (self, content, *args, **kwargs),
                where `content` is the extracted message text.

        Returns:
            Callable: The wrapped function, or None if the packet is not a main text message.
        """
        @functools.wraps(func)
        async def wrapper(self, result, *args, **kwargs) -> Union[Awaitable[Any], None]:
            """
            Extracts and processes main text messages from the result before calling the wrapped function.

            If the incoming `result` contains a message of type MAIN_TEXT, the decorator extracts
            the user and message content, saves user information to `self`, and passes the message
            text to the wrapped function. If no such message is found, the wrapped function is not called.

            Args:
                self: The instance to which the decorated method belongs.
                result (dict): The incoming packet potentially containing a message.
                *args: Additional positional arguments to pass to the wrapped function.
                **kwargs: Additional keyword arguments to pass to the wrapped function.

            Returns:
                Awaitable[Any] | None: The result of the wrapped function if called, otherwise None.
            """
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

                    return await func(self, content, *args, **kwargs)

            return None

        return wrapper
