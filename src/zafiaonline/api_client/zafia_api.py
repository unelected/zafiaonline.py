import inspect
import functools

from secrets import token_hex
from typing import Any, Dict

from zafiaonline.structures.enums import MethodGetFavourites, RatingType
from zafiaonline.transport.http_module import HttpWrapper
from zafiaonline.structures.packet_data_keys import (ZafiaEndpoints,
                                                     ZafiaApiKeys)
from zafiaonline.utils.logging_config import logger

class ZafiaApi(HttpWrapper):
    @staticmethod
    def with_user_id(func):
        @functools.wraps(func)
        async def wrapper(self, endpoint: str, params: dict, user_id: str, *args, **kwargs):
            full_params: dict = {ZafiaApiKeys.USER_ID: user_id, **params}
            return await func(self, endpoint, full_params, user_id, *args,
                              **kwargs)

        return wrapper

    async def change_favorite_status(self, user_id: str, favorite_id: str) \
            -> Dict[str, bool]:
        endpoint: str = ZafiaEndpoints.CHANGE_FAVORITE_STATUS
        params: dict = {ZafiaApiKeys.FAVORITE_ID: favorite_id}

        return await self._get(endpoint, params = params, user_id =
        user_id)


    async def change_visible_top(self, user_id: str, show: bool = True) -> (
            Dict[str, bool]):
        endpoint: str = ZafiaEndpoints.CHANGE_VISIBLE_TOP
        params: dict = {ZafiaApiKeys.SHOW: str(show).lower()}

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_favorites_list(self, user_id: str, from_type:
    MethodGetFavourites = MethodGetFavourites.InviteMethod) -> Dict[str, Any]:
        endpoint: str = ZafiaEndpoints.GET_FAVORITES_LIST
        params: dict = {ZafiaApiKeys.FROM_TYPE: from_type}

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def check_profile(self, user_id: str, check_id: str,
                user_nickname: str, check_nickname: str) -> Dict[str, bool]:
        endpoint: str = ZafiaEndpoints.CHECK_PROFILE
        params: dict = {
            ZafiaApiKeys.CHECK_ID: check_id,
            ZafiaApiKeys.USER_NICKNAME: user_nickname,
            ZafiaApiKeys.CHECK_NICKNAME: check_nickname
        }

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_top(self, user_id: str, top_type: RatingType =
    RatingType.EXPERIENCE) -> (
            Dict[str, Any]):
        endpoint: str = ZafiaEndpoints.GET_TOP
        params: dict = {ZafiaApiKeys.TYPE: top_type}
        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_verifications(self, user_id: str, version: int = 15,
                                device_id: str = "") -> Dict[str, Any]:
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
        try:
            data =  await self.zafia_request("get",
                                            endpoint, params = params,
                                            user_id = user_id)
            if data is Dict:
                return data
            raise ValueError
        except Exception as e:
            logger.exception(f"Unexpected error {e} from {endpoint} request in"
                         f" {inspect.currentframe().f_back.f_code.co_name}")
            raise
