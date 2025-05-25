from secrets import token_hex

from zafiaonline.structures import MafiaLanguages
from zafiaonline.structures.packet_data_keys import Endpoints
from zafiaonline.transport.http_module import Http
from zafiaonline.utils.md5hash import Md5


class HttpsApi(Http):
    async def remove_user_account_request(self, language: MafiaLanguages =
                                          MafiaLanguages.English) -> dict:
        endpoint = Endpoints.REMOVE_ACCOUNT
        data = {'lang': language.value}
        return await self.api_mafia_request("POST", endpoint, data)

    async def get_profile_photo_request(self, user_id: str) -> bytes:
        endpoint = Endpoints.PROFILE_PHOTO.format(user_id)
        return await self.mafia_request("GET", endpoint)

    async def get_client_config(self, version: int = 48) -> dict:
        endpoint = Endpoints.CLIENT_CONFIG.format(version)
        return await self.mafia_request("GET", endpoint)

    async def get_client_feature_config(self) -> dict:
        endpoint = Endpoints.CLIENT_FEATURE_CONFIG
        return await self.api_mafia_request("GET", endpoint)

    async def sign_out(self) -> dict:
        endpoint = Endpoints.USER_SIGN_OUT
        return await self.api_mafia_request("POST", endpoint)

    async def sign_up(self, email:str, password, username: str|None = None,
                      language: MafiaLanguages =
                      MafiaLanguages.English.value) -> dict:
        md5hash = Md5()
        endpoint = Endpoints.USER_SIGN_UP
        data:dict = {
            'email': email,
            'username': username,
            'password': md5hash.md5salt(password),
            'deviceId': token_hex(8),
            'lang': language
        }
        return await self.api_mafia_request("POST", endpoint, data)

    async def verify_email(self, language: MafiaLanguages =
    MafiaLanguages.English.value) -> dict:
        endpoint = "user/email/verify"
        data:dict = {
            'lang': language
        }
        return await self.api_mafia_request("POST", endpoint, data)

    async def change_email(self, new_email: str, password: str,
                           language: MafiaLanguages =
                           MafiaLanguages.English.value) -> dict:
        md5hash = Md5()
        endpoint = "user/change/email"
        data = {
            'newEmail': new_email,
            'currentPassword': md5hash.md5salt(password),
            'lang': language
        }
        return await self.api_mafia_request("POST", endpoint, data)

    async def email_verification(self, verification_code: str) -> dict:
        endpoint = "user/email/verification"
        data = {
            'verificationCode': verification_code
        }
        return await self.api_mafia_request("POST", endpoint, data)

    async def user_get(self, user_id):
        endpoint = "user/get"
        data = {
            'userObjectId': user_id
        }
        return await self.api_mafia_request("POST", endpoint, data)

    async def backpack_get(self):
        endpoint = "backpack/get"
        return await self.api_mafia_request("POST", endpoint)

    async def backpack_get_bonus_prices(self):
        endpoint = "backpack/get_bonus_prices"
        return await self.api_mafia_request("POST", endpoint)