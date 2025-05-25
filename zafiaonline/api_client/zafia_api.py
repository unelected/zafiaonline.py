import inspect
import functools

from secrets import token_hex
from typing import Any

from zafiaonline.structures.enums import MethodGetFavourites, RatingType
from zafiaonline.transport.http_module import Http
from zafiaonline.structures.packet_data_keys import Endpoints
from zafiaonline.utils.logging_config import logger

class ZafiaApi(Http):
    @staticmethod
    def with_user_id(func):
        @functools.wraps(func)
        async def wrapper(self, endpoint, params, user_id, *args, **kwargs):
            full_params = {"userId": user_id, **params}
            return await func(self, endpoint, full_params, user_id, *args,
                              **kwargs)

        return wrapper

    async def change_favorite_status(self, user_id: str, favorite_id: str) \
            -> dict[str, bool]:
        endpoint = Endpoints.CHANGE_FAVORITE_STATUS
        params = {"favoriteId": favorite_id}

        return await self._get(endpoint, params = params, user_id =
        user_id)


    async def change_visible_top(self, user_id: str, show: bool = True) -> (
            dict[str, bool]):
        endpoint = Endpoints.CHANGE_VISIBLE_TOP
        params = {"show": str(show).lower()}

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_favorites_list(self, user_id: str, from_type:
    MethodGetFavourites = MethodGetFavourites.InviteMethod) -> dict[str, Any]:
        endpoint = Endpoints.GET_FAVORITES_LIST
        params = {"fromType": from_type}

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def check_profile(self, user_id: str, check_id: str,
                user_nickname: str, check_nickname: str) -> dict[str, bool]:
        endpoint = Endpoints.CHECK_PROFILE
        params = {
            "checkId": check_id,
            "userNickname": user_nickname,
            "checkNickname": check_nickname
        }

        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_top(self, user_id: str, top_type: RatingType =
    RatingType.EXPERIENCE) -> (
            dict[str, Any]):
        endpoint = Endpoints.GET_TOP
        params = {"type": top_type}
        return await self._get(endpoint, params = params, user_id
        = user_id)


    async def get_verifications(self, user_id: str, version: int = 15,
                                device_id: str = None) -> dict[str, Any]:
        endpoint = Endpoints.GET_VERIFICATIONS
        params = {
            "version": version,
            "deviceId": device_id or token_hex(10)
        }
        return await self._get(endpoint, params = params, user_id \
            = user_id)

    @with_user_id
    async def _get(self, endpoint: Endpoints, params: dict[str, Any],
                   user_id: str) -> dict[str, Any]:
        try:
            return await self.zafia_request("GET",
                                            endpoint.value, params = params,
                                            user_id = user_id)
        except Exception as e:
            logger.exception(f"Unexpected error {e} from {endpoint} request in"
                         f" {inspect.currentframe().f_back.f_code.co_name}")
            raise