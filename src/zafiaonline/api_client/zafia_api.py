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
Client module for interacting with the Zafia API.

This module provides an asynchronous wrapper around several HTTP-based endpoints
used to interact with Zafia user profiles, such as modifying favorites, retrieving
rankings, checking verification data, and more.

Typical usage example:

    api = ZafiaApi()
    top = await api.get_top(user_id="user_xxxx")

The `ZafiaApi` class extends `HttpWrapper` and handles endpoint-specific requests
with automatic parameter formatting and error logging.
"""
import inspect
import functools

from secrets import token_hex
from typing import Any, Awaitable, Callable, Dict

from zafiaonline.structures.enums import MethodGetFavourites, RatingType
from zafiaonline.transport.http_module import HttpWrapper
from zafiaonline.structures.packet_data_keys import (ZafiaEndpoints,
                                                     ZafiaApiKeys)
from zafiaonline.utils.logging_config import logger

class ZafiaApi(HttpWrapper):
    """
    Asynchronous API client for interacting with Zafia user data and profile features.

    This class provides high-level methods to access various Zafia endpoints,
    including actions like managing favorites, checking profile data,
    fetching leaderboard statistics, and verifying user accounts.

    Attributes:
        proxy (str | None): Optional HTTP proxy to be used for requests.
    """
    def __init__(self, proxy: str | None = None):
        """
        Initializes the ZafiaApi instance with an optional proxy.

        Args:
            proxy (str | None): Optional proxy string for routing HTTP requests.
        """
        super().__init__(proxy)

    @staticmethod
    def with_user_id(func: Callable) -> Callable:
        """
        Decorator that injects the 'user_id' into the request parameters.

        This decorator modifies the 'params' dictionary passed to the wrapped
        function by adding the 'user_id' key.

        Args:
            func (Callable): The asynchronous function to wrap.

        Returns:
            Callable: The wrapped asynchronous function with 'user_id' injected
            into the parameters.
        """
        @functools.wraps(func)
        async def wrapper(self, endpoint: str, params: dict,
                          user_id: str, *args, **kwargs) -> Awaitable[Any]:
            """
            Injects the user ID into the request parameters before calling the wrapped function.

            Adds the `user_id` to the `params` dictionary under the expected key, then forwards
            the updated parameters to the wrapped function.

            Args:
                self: The instance of the class using this decorator.
                endpoint (str): The API endpoint to call.
                params (dict): Initial request parameters.
                user_id (str): The user ID to include in the parameters.
                *args: Additional positional arguments for the wrapped function.
                **kwargs: Additional keyword arguments for the wrapped function.

            Returns:
                Awaitable[Any]: The result of the wrapped function.
            """
            full_params: dict = {ZafiaApiKeys.USER_ID: user_id, **params}
            return await func(self, endpoint, full_params, user_id, *args,
                              **kwargs)

        return wrapper

    async def change_favorite_status(self, user_id: str, favorite_id: str) \
            -> Dict[str, bool]:
        """
        Toggle the favorite status for a specific item by the user.

        Sends a request to mark or unmark an item (identified by `favorite_id`) as a favorite
        for the specified user.

        Args:
            user_id (str): The ID of the user performing the action.
            favorite_id (str): The ID of the item to be marked or unmarked as favorite.

        Returns:
            Dict[str, bool]: The server response indicating whether the update was successful.
        """
        endpoint: str = ZafiaEndpoints.CHANGE_FAVORITE_STATUS
        params: dict = {ZafiaApiKeys.FAVORITE_ID: favorite_id}

        return await self._get(endpoint, params = params, user_id =
        user_id)


    async def change_visible_top(self, user_id: str, show: bool = True) -> (
            Dict[str, bool]):
        """
        Changes the visibility status of the user on the top list.

        Sends a request to the server to update whether the specified user
        should appear in the visible top list or not.

        Args:
            user_id (str): The unique identifier of the user.
            show (bool, optional): Indicates whether the user should be shown in
                the top list. Defaults to True.

        Returns:
            Dict[str, bool]: A dictionary indicating whether the visibility status was successfully changed.
        """
        endpoint: str = ZafiaEndpoints.CHANGE_VISIBLE_TOP
        params: dict = {ZafiaApiKeys.SHOW: str(show).lower()}

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_favorites_list(self, user_id: str, from_type:
    MethodGetFavourites = MethodGetFavourites.InviteMethod) -> Dict[str, Any]:
        """
        Retrieves the list of favorite users for the specified user.

        This method fetches the user's favorites based on the specified method type,
        such as favorites added through invites or friend list means.

        Args:
            user_id (str): The unique identifier of the user.
            from_type (MethodGetFavourites, optional): The method by which the favorites were added.
                Defaults to MethodGetFavourites.InviteMethod.

        Returns:
            Dict[str, Any]: A dictionary containing the list of favorite users.
        """
        endpoint: str = ZafiaEndpoints.GET_FAVORITES_LIST
        params: dict = {ZafiaApiKeys.FROM_TYPE: from_type}

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def check_profile(self, user_id: str, check_id: str,
                user_nickname: str, check_nickname: str) -> Dict[str, bool]:
        """
        Compares the specified user's profile with another user's profile.

        This method checks whether the provided nicknames and user IDs match 
        or meet some criteria defined by the backend for profile comparison.

        Args:
            user_id (str): The unique identifier of the current user.
            check_id (str): The unique identifier of the user to check against.
            user_nickname (str): The nickname of the current user.
            check_nickname (str): The nickname of the user being checked.

        Returns:
            Dict[str, bool]: A dictionary indicating whether the profile comparison passed.
        """
        endpoint: str = ZafiaEndpoints.CHECK_PROFILE
        params: dict = {
            ZafiaApiKeys.CHECK_ID: check_id,
            ZafiaApiKeys.USER_NICKNAME: user_nickname,
            ZafiaApiKeys.CHECK_NICKNAME: check_nickname
        }

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_top(self, user_id: str, top_type: RatingType =
                      RatingType.EXPERIENCE) -> (Dict[str, Any]):
        """
        Retrieves the leaderboard data for a given rating type.

        This method fetches the top users from the specified leaderboard, such as by experience
        or other rating metrics.

        Args:
            user_id (str): The ID of the user making the request.
            top_type (RatingType, optional): The type of leaderboard to retrieve.
                Defaults to RatingType.EXPERIENCE.

        Returns:
            Dict[str, Any]: A dictionary containing leaderboard data.
        """
        endpoint: str = ZafiaEndpoints.GET_TOP
        params: dict = {ZafiaApiKeys.TYPE: top_type}
        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_verifications(self, user_id: str, version: int = 15,
                                device_id: str = "") -> Dict[str, Any]:
        """
        Retrieves the list of verifications required for the client.

        Sends a request to fetch current verification depending on the
        client version and device identifier.

        Args:
            user_id (str): The ID of the user making the request.
            version (int, optional): The client version. Defaults to 15.
            device_id (str, optional): The device identifier. If not provided,
                a random one will be generated.

        Returns:
            Dict[str, Any]: A dictionary containing verification data.
        """
        endpoint: str = ZafiaEndpoints.GET_VERIFICATIONS
        params: dict = {
            ZafiaApiKeys.VERSION: version,
            ZafiaApiKeys.DEVICE_ID: device_id or token_hex(8)
        }
        return await self._get(endpoint, params = params, user_id \
            = user_id)

    @with_user_id
    async def _get(self, endpoint: ZafiaEndpoints, params: dict[str, Any],
                   user_id: str) -> Dict[str, Any]:
        """
        Executes a GET request to the Zafia API and returns the response as a dictionary.

        Used for internal GET requests with automatic error handling and logging of
        the calling function's name in case of failure.

        Args:
            endpoint (ZafiaEndpoints): The API endpoint to query.
            params (dict[str, Any]): The parameters to include in the request.
            user_id (str): The ID of the user making the request.

        Returns:
            dict[str, Any]: The server response as a dictionary.

        Raises:
            ValueError: If the response is of type `bytes` instead of `dict`.
            Exception: Re-raises any exception that occurs during the request.
        """
        try:
            data: Dict | bytes =  await self.zafia_request("get",
                                            endpoint, params = params,
                                            user_id = user_id)
            if isinstance(data, dict):
                return data
            raise ValueError
        except Exception as e:
            frame: Any = inspect.currentframe()
            caller_name: Any = "Unknown function"
            if frame and frame.f_back and frame.f_back.f_code:
                caller_name = frame.f_back.f_code.co_name
            logger.exception(f"Unexpected error {e} from {endpoint} request in {caller_name}")
            raise
