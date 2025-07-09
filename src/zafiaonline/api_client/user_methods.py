import base64
import json

from typing import  Optional, TYPE_CHECKING, Any
from secrets import token_hex
from msgspec.json import decode

if TYPE_CHECKING:
    from zafiaonline.main import Client
from zafiaonline.structures import PacketDataKeys
from zafiaonline.api_client.api_decorators import ApiDecorators
from zafiaonline.utils.logging_config import logger
from zafiaonline.transport.websocket_module import Websocket
from zafiaonline.utils.md5hash import Md5
from zafiaonline.structures.models import ModelUser, ModelServerConfig
from zafiaonline.structures.enums import Languages, Sex, MafiaLanguages
from zafiaonline.utils.utils import get_user_attributes


class Auth(Websocket):
    def __init__(self, client: "Client", proxy: str | None = None) -> None:
        """
        Initializes the Client.

        Parameters:
            proxy (Optional[List[str]]): List of proxy addresses. Defaults
            to an empty list.
        """
        self.client: "Client" = client
        self.proxy: str | None = proxy or None
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.device_id: str = ""
        self.md5hash: "Md5" = Md5()
        self.user: "ModelUser" = ModelUser()
        self.server_configi: "ModelServerConfig" = ModelServerConfig()
        super().__init__(client = client) # тут может быть баг

    @ApiDecorators.login_required
    async def sign_in(self, email: str = "", password: str = "",
                      token: str = "", user_id: str = "") -> ModelUser | bool:
        """
        Signs in a user.

        Parameters:
            email (str): The user's email. Defaults to an empty string.
            password (str): The user's password. Defaults to an empty string.
            token (str): The user's authentication token. Defaults to an
            empty string.
            user_id (str): The user's ID. Defaults to an empty string.

        Returns:
            ModelUser: The user object if authentication is successful.
            bool: False if authentication fails.
        """
        self._warn_if_default_email(email)
        await self._ensure_connection()

        auth_data: dict = self._prepare_auth_data(email, password, token, user_id)
        await self.send_server(auth_data)

        return await self._process_auth_response()

    @staticmethod
    def _warn_if_default_email(email: str) -> None:
        """
        Logs a warning if the email is set to the default value.

        Parameters:
            email (str): The email address to check.

        Returns:
            None
        """
        default_email: str = "email"
        if email.strip().lower() == default_email:
            logger.warning(
                "Your email is literally 'email'. Please update your config "
                "if this is incorrect."
            )

    async def _ensure_connection(self) -> None:
        """
        Ensures the client is connected before performing an action.

        If the connection is not alive, it attempts to create a new one.
        """
        if not self.alive:
            logger.debug("Connection not active. Attempting to connect...")
            await self.create_connection(self.proxy)

    def _prepare_auth_data(self, email: str, password: str, token: str,
                           user_id: str) -> dict:
        """
        Prepares the authentication payload for the sign-in request.

        Parameters:
            email (str): The user's email address.
            password (str): The user's password.
            token (str): The authentication token.
            user_id (str): The unique identifier of the user.

        Returns:
            dict: The authentication payload.
        """
        self.device_id: str = token_hex(8)
        return {
            PacketDataKeys.DEVICE_ID: self.device_id,
            # Generates a random device ID
            PacketDataKeys.TYPE: PacketDataKeys.SIGN_IN,
            PacketDataKeys.EMAIL: email,
            PacketDataKeys.PASSWORD: self.md5hash.md5salt(password or ""),
            # Hashes password
            PacketDataKeys.OBJECT_ID: user_id,
            PacketDataKeys.TOKEN: token,
        }

    async def _process_auth_response(self) -> ModelUser | bool:
        """
        Processes the server response after attempting to sign in.

        Returns:
            ModelUser: The authenticated user object if sign-in is successful.
            bool: False if authentication fails.
        """
        received_data: dict | None = await self.get_data(PacketDataKeys.USER_SIGN_IN)

        if not received_data or received_data.get(
                PacketDataKeys.TYPE) != PacketDataKeys.USER_SIGN_IN:
            logger.error("Sign-in data retrieval error")
            return False

        self._set_user_data(received_data)
        return self.user

    def _set_user_data(self, received_data: dict) -> None:
        """
        Parses and stores user data from the sign-in response.

        Args:
            received_data (dict): The response data containing user and
            server info.
        """
        try:
            user_data: str | None = received_data.get(PacketDataKeys.USER)
            server_config_data: str | None = received_data.get(
                PacketDataKeys.SERVER_CONFIG)

            if not user_data or not server_config_data:
                logger.error("Missing user or server config data in response")
                return

            self.user: ModelUser = decode(json.dumps(user_data).encode(), type = ModelUser)
            self.server_config: ModelServerConfig = decode(json.dumps(server_config_data),
                                        type = ModelServerConfig)

            self.token = self.user.token
            self.user_id = self.user.user_id

            self.update_auth_data()

        except Exception as e:
            logger.error(f"Error parsing user data: {e}", exc_info=True)


class User:
    def __init__(self, client: "Auth"):
        self.client: "Auth" = client
        if self.client:
            get_user_attributes(self.client)

    async def send_server(self, data: dict[str, Any], remove_token_from_object: bool = False):
        await self.client.send_server(data, remove_token_from_object)

    async def listen(self):
        return await self.client.listen()

    async def username_set(self, nickname: str) -> None:
        """
        Sends a request to update the user's nickname.

        Parameters:
            nickname (str): The new nickname to be set.

        Returns:
            None
        """
        username_update_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USERNAME_SET,
            PacketDataKeys.USERNAME: nickname
        }
        await self.send_server(username_update_request)

    async def select_language(self, language: Languages = Languages.RUSSIAN)\
            -> None:
        """
        Sends a request to update the user's preferred language.

        Parameters:
            language (Languages): The language to be set. Defaults to Russian.

        Returns:
            None
        """
        language_update_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USER_SET_SERVER_LANGUAGE,
            PacketDataKeys.SERVER_LANGUAGE: language
        }
        await self.send_server(language_update_request)

    async def buy_vip(self, app_language = MafiaLanguages.Russian):
        buy_vip_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.BUY_MARKET_ITEM,
            PacketDataKeys.APP_LANGUAGE: app_language.value,
            PacketDataKeys.OBJECT_ID: PacketDataKeys.VIP_ACCOUNT
        }
        await self.send_server(buy_vip_request)

    async def update_photo(self, file: bytes) -> None:
        """
        Uploads and updates the user's profile photo.

        Parameters:
            file (bytes): The image file in bytes to be uploaded.

        Returns:
            None
        """
        update_photo_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.UPLOAD_PHOTO,
            PacketDataKeys.FILE: base64.encodebytes(file).decode()
        }
        await self.send_server(update_photo_request)

    async def update_sex(self, sex: Sex) -> dict | Any:
        """
        Updates the user's gender.

        Parameters:
            sex (Sex): The new gender to be set for the user.

        Returns:
            dict: The server response after updating the gender.
        """
        update_sex_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USER_CHANGE_SEX,
            PacketDataKeys.SEX: sex
        }
        await self.send_server(update_sex_request)
        return await self.listen()

    async def update_photo_server(self, file: bytes) -> None:
        """
        Uploads and updates a screenshot on the server.

        Parameters:
            file (bytes): The screenshot file in bytes to be uploaded.

        Returns:
            None
        """
        upload_photo_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.UPLOAD_SCREENSHOT,
            PacketDataKeys.FILE: base64.encodebytes(file).decode()
        }
        await self.send_server(upload_photo_request)

    async def dashboard(self) -> None:
        """
        Sends a request to add the client to the dashboard.

        This function requests the server to place the client on the
        dashboard, typically used for accessing account-related information
        or lobby interactions.

        Returns:
            None
        """
        account_payload: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_DASHBOARD
        }
        await self.send_server(account_payload)
