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
User-related operations for the Mafia client-server application.

Provides the User class which wraps several high-level user actions by
sending requests to the server through the authenticated client connection.

These include nickname updates, language settings, VIP purchases,
profile photo uploads, gender updates, and dashboard management.

Typical usage example:

    auth = Auth(...)
    user = User(auth)
    await user.username_set("CoolPlayer123")
    await user.select_language(Languages.ENGLISH)
    await user.buy_vip()
"""
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
    """
    Handles user authentication and session-related metadata for WebSocket communication.

    Attributes:
        client (Client): The main client instance used for communication.
        proxy (Optional[str]): Proxy address used for network requests.
        token (Optional[str]): Authentication token for the current session.
        user_id (Optional[str]): Unique identifier of the authenticated user.
        device_id (str): Identifier of the device used in this session.
        md5hash (Md5): Utility for generating MD5 hashes.
        user (ModelUser): Model representing the authenticated user.
        server_configi (ModelServerConfig): Model for server configuration.
    """
    def __init__(self, client: "Client", proxy: str | None = None) -> None:
        """
        Initialize the Auth handler with client and optional proxy.

        Args:
            client (Client): The main client instance.
            proxy (Optional[str]): Optional proxy address.
        """
        self.client: "Client" = client
        self.proxy: str | None = proxy or None
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.device_id: str = ""
        self.md5hash: "Md5" = Md5()
        self.user: "ModelUser" = ModelUser()
        self.server_config: "ModelServerConfig" = ModelServerConfig()
        super().__init__(client = client)

    @ApiDecorators.login_required
    async def sign_in(self, email: str = "", password: str = "",
                      token: str = "", user_id: str = "") -> ModelUser | bool:
        """
        Signs in a user using email/password or token-based authentication.

        Args:
            email (str): User's email address. Defaults to "".
            password (str): User's password (in plaintext). Defaults to "".
            token (str): Authentication token, used instead of password if provided. Defaults to "".
            user_id (str): ID of the user to associate with the session. Defaults to "".

        Returns:
            ModelUser: User object on successful authentication.
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
        Logs a warning if the email is set to the literal default value "email".

        Args:
            email (str): The email address to check.
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

        If the connection is not alive, attempts to create a new one.
        """
        if not self.alive:
            logger.debug("Connection not active. Attempting to connect...")
            await self.create_connection(self.proxy)

    def _prepare_auth_data(self, email: str, password: str, token: str,
                           user_id: str) -> dict:
        """
        Prepares the authentication payload for the sign-in request.

        Args:
            email (str): The user's email address.
            password (str): The user's password.
            token (str): The authentication token.
            user_id (str): The unique identifier of the user.

        Returns:
            dict: A dictionary containing the sign-in request payload.
        """
        self.device_id: str = token_hex(8)
        data: dict = {
            # Generates a random device ID
            PacketDataKeys.TYPE: PacketDataKeys.SIGN_IN,
            PacketDataKeys.EMAIL: email,
            PacketDataKeys.PASSWORD: self.md5hash.md5salt(password or ""),
            PacketDataKeys.OBJECT_ID: user_id,
            PacketDataKeys.DEVICE_ID: self.device_id,
            PacketDataKeys.TOKEN: token,
            }
        return data

    async def _process_auth_response(self) -> ModelUser | bool:
        """
        Processes the server response after a sign-in attempt.

        Waits for the expected user data packet. If valid data is received,
        populates the user object and returns it. Otherwise, returns False.

        Returns:
            ModelUser: The authenticated user object if successful.
            bool: False if authentication fails or response is invalid.
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
        Parses and stores user and server configuration data from the sign-in response.

        Args:
            received_data (dict): The response payload containing serialized user
                                and server config information.
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
    """
    Handles user-related actions within the Mafia client.

    This class provides functionality for interacting with user-specific
    endpoints of the Mafia API. It allows operations such as setting the 
    username, selecting a preferred language, purchasing VIP status, and 
    updating profile photos. It relies on an authenticated `Auth` client
    to send these requests to the server.

    Attributes:
        client (Auth): An instance of the authenticated client used to
            communicate with the Mafia API for user-specific actions.
    """
    def __init__(self, client: "Auth"):
        """
        Initializes the User interaction interface.

        This constructor stores a reference to the provided authenticated
        client, which will be used to perform all user-related operations.
        If a valid client is passed, it also performs initial setup by 
        calling `get_user_attributes()` to fetch or update local user state.

        Args:
            client (Auth): The authenticated Mafia client used for making
                user-related API calls.
        """
        self.client: "Auth" = client
        if self.client:
            get_user_attributes(self.client)

    async def send_server(self, data: dict[str, Any],
                          remove_token_from_object: bool = False) -> None:
        """
        Sends a data payload to the server through the authenticated client.

        This method delegates the actual sending of data to the underlying
        `Auth` client, allowing the `User` class to abstract communication
        with the Mafia server. It can optionally remove the token from the
        payload before sending.

        Args:
            data (dict[str, Any]): The dictionary payload to be sent to the server.
            remove_token_from_object (bool): If True, removes the token from the
                payload before sending. Defaults to False.

        Returns:
            None
        """
        await self.client.send_server(data, remove_token_from_object)

    async def listen(self) -> dict | None:
        """
        Listens for incoming messages from the server.

        This method delegates the listening functionality to the underlying
        authenticated client. It waits asynchronously for a message from
        the server and returns the received payload.

        Returns:
            dict | None: The message or data received from the server. The exact
            type and structure of the response depends on the server's protocol.
        """
        return await self.client.listen()

    async def username_set(self, nickname: str) -> None:
        """
        Sends a request to the server to update the user's username.

        This method constructs and dispatches a packet to set a new nickname
        for the currently authenticated user. The server is expected to process
        the request and update the user's profile accordingly.

        Args:
            nickname (str): The desired username to assign to the user's account.

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
        Sends a request to the server to update the user's preferred language.

        This method changes the language setting associated with the user's profile
        on the server. The selected language will affect future server responses 
        (such as system messages, UI text, etc.), depending on server-side support.

        Args:
            language (Languages): The target language to set for the user.
                Defaults to `Languages.RUSSIAN`.

        Returns:
            None
        """
        language_update_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USER_SET_SERVER_LANGUAGE,
            PacketDataKeys.SERVER_LANGUAGE: language
        }
        await self.send_server(language_update_request)

    async def buy_vip(self, app_language = MafiaLanguages.Russian) -> None:
        """
        Sends a request to purchase a VIP account for the user.

        This method initiates the purchase of a VIP account via the in-game market system.
        It includes the selected application language in the request payload, which may affect
        localization of the server response or purchase dialog (depending on server behavior).

        Args:
            app_language (MafiaLanguages, optional): The language used for the request context.
                Defaults to `MafiaLanguages.Russian`.

        Returns:
            None
        """
        buy_vip_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.BUY_MARKET_ITEM,
            PacketDataKeys.APP_LANGUAGE: app_language.value,
            PacketDataKeys.OBJECT_ID: PacketDataKeys.VIP_ACCOUNT
        }
        await self.send_server(buy_vip_request)

    async def update_photo(self, file: bytes) -> None:
        """
        Uploads and sets a new profile photo for the user.

        This method sends a request to the server to update the user's profile
        picture. The provided image file is expected to be in raw byte format,
        which will be base64-encoded before transmission.

        Args:
            file (bytes): The image file in bytes. Typically a PNG or JPEG.

        Returns:
            None
        """
        update_photo_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.UPLOAD_PHOTO,
            PacketDataKeys.FILE: base64.encodebytes(file).decode()
        }
        await self.send_server(update_photo_request)

    async def update_sex(self, sex: Sex) -> dict | None:
        """
        Sends a request to update the user's gender on the server.

        This method updates the user's gender information by sending the 
        appropriate payload to the backend. The gender is typically selected 
        from a predefined enumeration (`Sex`), and the change is immediately 
        reflected on the server after confirmation.

        Args:
            sex (Sex): The new gender to assign to the user. Must be a value 
                    from the `Sex` enum (e.g., MALE, FEMALE).

        Returns:
            dict | None: The server response indicating the success or failure 
            of the operation. Usually a confirmation packet with updated user 
            data or status.
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

        This method encodes the provided screenshot file (in bytes) into 
        a base64 string and sends it to the server as part of a request to 
        update or store the screenshot. It is typically used for sending 
        game screenshots, user reports, or debugging information.

        Args:
            file (bytes): The raw image data of the screenshot to be uploaded.
                        Must be a valid byte sequence representing an image.

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

        This method communicates with the server to add the current client
        session to the dashboard context. It is often used to initialize the
        user's presence in the main interface or lobby of the application,
        allowing access to account details, menus, or multiplayer features.

        Typically, this is called after successful authentication and
        before interacting with dashboard-level features.

        Returns:
            None
        """
        account_payload: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_DASHBOARD
        }
        await self.send_server(account_payload)
