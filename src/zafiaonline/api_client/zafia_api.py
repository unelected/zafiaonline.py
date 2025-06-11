import inspect
import functools

from secrets import token_hex
from typing import Any

from zafiaonline.structures.enums import MethodGetFavourites, RatingType
from zafiaonline.transport.http_module import Http
from zafiaonline.structures.packet_data_keys import (ZafiaEndpoints,
                                                     ZafiaApiKeys)
from zafiaonline.utils.logging_config import logger

class ZafiaApi(Http):
    @staticmethod
    def with_user_id(func):
        @functools.wraps(func)
        async def wrapper(self, endpoint, params, user_id, *args, **kwargs):
            full_params = {ZafiaApiKeys.USER_ID: user_id, **params}
            return await func(self, endpoint, full_params, user_id, *args,
                              **kwargs)

        return wrapper

    async def change_favorite_status(self, user_id: str, favorite_id: str) \
            -> dict[str, bool]:
        endpoint = ZafiaEndpoints.CHANGE_FAVORITE_STATUS
        params = {ZafiaApiKeys.FAVORITE_ID: favorite_id}

        return await self._get(endpoint, params = params, user_id =
        user_id)


    async def change_visible_top(self, user_id: str, show: bool = True) -> (
            dict[str, bool]):
        endpoint = ZafiaEndpoints.CHANGE_VISIBLE_TOP
        params = {ZafiaApiKeys.SHOW: str(show).lower()}

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_favorites_list(self, user_id: str, from_type:
    MethodGetFavourites = MethodGetFavourites.InviteMethod) -> dict[str, Any]:
        endpoint = ZafiaEndpoints.GET_FAVORITES_LIST
        params = {ZafiaApiKeys.FROM_TYPE: from_type}

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def check_profile(self, user_id: str, check_id: str,
                user_nickname: str, check_nickname: str) -> dict[str, bool]:
        endpoint = ZafiaEndpoints.CHECK_PROFILE
        params = {
            ZafiaApiKeys.CHECK_ID: check_id,
            ZafiaApiKeys.USER_NICKNAME: user_nickname,
            ZafiaApiKeys.CHECK_NICKNAME: check_nickname
        }

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_top(self, user_id: str, top_type: RatingType =
    RatingType.EXPERIENCE) -> (
            dict[str, Any]):
        endpoint = ZafiaEndpoints.GET_TOP
        params = {ZafiaApiKeys.TYPE: top_type}
        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_verifications(self, user_id: str, version: int = 15,
                                device_id: str = None) -> dict[str, Any]:
        endpoint = ZafiaEndpoints.GET_VERIFICATIONS
        params = {
            ZafiaApiKeys.VERSION: version,
            ZafiaApiKeys.DEVICE_ID: device_id or token_hex(8)
        }
        return await self._get(endpoint, params = params, user_id \
            = user_id)

    @with_user_id
    async def _get(self, endpoint: ZafiaEndpoints, params: dict[str, Any],
                   user_id: str) -> dict[str, Any]:
        try:
            return await self.zafia_request("GET",
                                            endpoint.value, params = params,
                                            user_id = user_id)
        except Exception as e:
            logger.exception(f"Unexpected error {e} from {endpoint} request in"
                         f" {inspect.currentframe().f_back.f_code.co_name}")
            raise