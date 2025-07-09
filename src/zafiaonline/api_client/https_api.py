from secrets import token_hex

from zafiaonline.structures import MafiaLanguages
from zafiaonline.structures.packet_data_keys import Endpoints, HttpsApiKeys
from zafiaonline.transport.http_module import HttpWrapper
from zafiaonline.utils.md5hash import Md5


class HttpsApi(HttpWrapper):
    def __init__(self):
        super().__init__()
        self.md5hash: "Md5" = Md5()

    async def remove_user_account_request(self, language: MafiaLanguages =
                                          MafiaLanguages.English) -> dict | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.REMOVE_ACCOUNT)
        data: dict = {HttpsApiKeys.LANGUAGE: language.value}
        return await self.api_mafia_request("post", endpoint, data)

    async def get_profile_photo_request(self, user_id: str) -> dict | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.PROFILE_PHOTO.format(user_id))
        return await self.mafia_request("get", endpoint)

    async def get_client_config(self, version: int = 50) -> dict | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.CLIENT_CONFIG.format(version))
        return await self.mafia_request("get", endpoint)

    async def get_client_feature_config(self) -> dict | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.CLIENT_FEATURE_CONFIG)
        return await self.api_mafia_request("get", endpoint)

    async def sign_out(self) -> dict | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.USER_SIGN_OUT)
        return await self.api_mafia_request("post", endpoint)

    async def sign_up(self, email:str, password, username: str|None = None,
                      language: MafiaLanguages =
                      MafiaLanguages.English) -> dict | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.USER_SIGN_UP)
        data:dict = {
            HttpsApiKeys.EMAIL: email,
            HttpsApiKeys.USERNAME: username,
            HttpsApiKeys.PASSWORD: self.md5hash.md5salt(password),
            HttpsApiKeys.DEVICE_ID: token_hex(8),
            HttpsApiKeys.LANGUAGE: language
        }
        return await self.api_mafia_request("post", endpoint, data)

    async def verify_email(self, language: MafiaLanguages =
    MafiaLanguages.English) -> dict[str, str] | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.USER_EMAIL_VERIFY)
        data: dict[str, str] = {
            HttpsApiKeys.LANGUAGE: language
        }
        return await self.api_mafia_request("post", endpoint, data)

    async def change_email(self, new_email: str, password: str,
                           language: MafiaLanguages =
                           MafiaLanguages.English) -> dict | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.USER_CHANGE_EMAIL)
        data: dict[str, str] = {
            HttpsApiKeys.NEW_EMAIL: new_email,
            HttpsApiKeys.CURRENT_PASSWORD: self.md5hash.md5salt(password),
            HttpsApiKeys.LANGUAGE: language
        }
        return await self.api_mafia_request("post", endpoint, data)

    async def email_verification(self, verification_code: str) -> dict | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.USER_EMAIL_VERIFICATION)
        data: dict[str, str] = {
            HttpsApiKeys.VERIFICATION_CODE: verification_code
        }
        return await self.api_mafia_request("post", endpoint, data)

    async def user_get(self, user_id: str) -> dict | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.USER_GET)
        data: dict[str, str] = {
            HttpsApiKeys.USER_OBJECT_ID: user_id
        }
        return await self.api_mafia_request("post", endpoint, data)

    async def backpack_get(self) -> dict | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.BACKPACK_GET)
        return await self.api_mafia_request("post", endpoint)

    async def backpack_get_bonus_prices(self) -> dict | bytes:
        endpoint: Endpoints = Endpoints(Endpoints.BACKPACK_GET_BONUS_PRICES)
        return await self.api_mafia_request("post", endpoint)
