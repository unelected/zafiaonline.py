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
HTTPS API client for Mafia Online.

Provides an interface for communicating with the Mafia Online backend
via HTTPS requests. This module includes account management, configuration
retrieval, backpack interactions, and other client-related endpoints.

Typical usage example:

    api = HttpsApi(proxy="http://localhost:8080")
    response = await api.sign_up(email="user@example.com", password="secure123")
    config = await api.get_client_config()
"""
from secrets import token_hex

from zafiaonline.structures import MafiaLanguages
from zafiaonline.structures.packet_data_keys import Endpoints, HttpsApiKeys
from zafiaonline.transport.http_module import HttpWrapper
from zafiaonline.utils.md5hash import Md5


class HttpsApi(HttpWrapper):
    """
    Provides HTTPS API interaction with optional proxy support.

    This class extends `HttpWrapper` to provide additional functionality
    for secure API access over HTTPS, including hashing utilities.

    Attributes:
        md5hash: An instance of `Md5` used for computing MD5 hashes.
    """
    def __init__(self, proxy: str | None = None):
        """
        Initializes the HttpsApi client with optional proxy configuration.

        Args:
            proxy: Optional. A proxy URL to route HTTPS requests through.
        """
        super().__init__(proxy)
        # TODO: @unelected - DRY proxy
        self.md5hash: "Md5" = Md5()

    async def remove_user_account_request(self, language: MafiaLanguages =
                                          MafiaLanguages.English) -> dict | bytes:
        """
        Sends a request to remove the user's account.

        This method sends a POST request to the server to initiate account removal,
        using the specified language for localization.

        Args:
            language: A `MafiaLanguages` enum value indicating the language
                to use in the request. Defaults to English.

        Returns:
            dict | bytes: The server's response to the account removal request,
            typically a dictionary or raw bytes depending on API implementation.
        """
        endpoint: Endpoints = Endpoints(Endpoints.REMOVE_ACCOUNT)
        data: dict = {HttpsApiKeys.LANGUAGE: language.value}
        return await self.api_mafia_request("post", endpoint, data)

    async def get_profile_photo_request(self, user_id: str) -> dict | bytes:
        """
        Retrieves the profile photo of a user by user ID.

        Sends a GET request to the server to fetch the profile picture
        associated with the specified user.

        Args:
            user_id: The unique identifier of the user whose profile photo
                should be retrieved.

        Returns:
            dict | bytes: The server response containing the profile photo data.
            This can be a dictionary with metadata or raw image bytes.
        """
        endpoint: Endpoints = Endpoints(Endpoints.PROFILE_PHOTO.format(user_id))
        return await self.mafia_request("get", endpoint)

    async def get_client_config(self, version: int = 50) -> dict | bytes:
        """
        Fetches the client configuration for a given version.

        Sends a GET request to retrieve configuration settings used by the client,
        such as feature flags, limits, or layout settings.

        Args:
            version: The version number of the client configuration to retrieve.
                Defaults to 50.

        Returns:
            dict | bytes: The client configuration data returned by the server.
            Can be a parsed JSON dictionary or raw response bytes.
        """
        endpoint: Endpoints = Endpoints(Endpoints.CLIENT_CONFIG.format(version))
        return await self.mafia_request("get", endpoint)

    async def get_client_feature_config(self) -> dict | bytes:
        """
        Fetches the client feature configuration.

        Sends a GET request to retrieve a list of enabled or experimental features
        available to the client.

        Returns:
            dict | bytes: The feature configuration returned by the server.
            May be a parsed JSON dictionary or raw response bytes.
        """
        endpoint: Endpoints = Endpoints(Endpoints.CLIENT_FEATURE_CONFIG)
        return await self.api_mafia_request("get", endpoint)

    async def sign_out(self) -> dict | bytes:
        """
        Signs the user out of the current session.

        Sends a POST request to terminate the user's active session on the server.

        Returns:
            dict | bytes: The server's response to the sign-out request, which may be
            a parsed JSON dictionary or raw response bytes.
        """
        endpoint: Endpoints = Endpoints(Endpoints.USER_SIGN_OUT)
        return await self.api_mafia_request("post", endpoint)

    async def sign_up(self, email: str, password: str,
                      username: str | None = None,
                      language: MafiaLanguages =
                      MafiaLanguages.English) -> dict | bytes:
        """
        Registers a new user account.

        Sends a sign-up request to the server with email, password, and optional username.

        Args:
            email (str): The user's email address.
            password (str): The user's password, which will be hashed before sending.
            username (str, optional): An optional display name for the user.
            language (MafiaLanguages): The preferred language for the account.

        Returns:
            dict | bytes: The server's response to the sign-up request, either as
            parsed JSON or raw bytes.
        """
        endpoint: Endpoints = Endpoints(Endpoints.USER_SIGN_UP)
        data: dict = {
            HttpsApiKeys.EMAIL: email,
            HttpsApiKeys.USERNAME: username,
            HttpsApiKeys.PASSWORD: self.md5hash.md5salt(password),
            HttpsApiKeys.DEVICE_ID: token_hex(8),
            HttpsApiKeys.LANGUAGE: language
        }
        return await self.api_mafia_request("post", endpoint, data)

    async def verify_email(self, language: MafiaLanguages =
    MafiaLanguages.English) -> dict[str, str] | bytes:
        """
        Sends a verification email to the user's address.

        Args:
            language (MafiaLanguages): The preferred language for the email content.

        Returns:
            dict[str, str] | bytes: The server's response containing status or 
            raw response bytes.
        """
        endpoint: Endpoints = Endpoints(Endpoints.USER_EMAIL_VERIFY)
        data: dict[str, str] = {
            HttpsApiKeys.LANGUAGE: language
        }
        return await self.api_mafia_request("post", endpoint, data)

    async def change_email(self, new_email: str, password: str,
                           language: MafiaLanguages =
                           MafiaLanguages.English) -> dict | bytes:
        """
        Sends a request to change the user's email address.

        Args:
            new_email (str): The new email address to set for the user.
            password (str): The user's current password (used for verification).
            language (MafiaLanguages): The preferred language for the response.

        Returns:
            dict | bytes: A dictionary with the server response on success,
            or raw bytes if the response is not JSON.
        """
        endpoint: Endpoints = Endpoints(Endpoints.USER_CHANGE_EMAIL)
        data: dict[str, str] = {
            HttpsApiKeys.NEW_EMAIL: new_email,
            HttpsApiKeys.CURRENT_PASSWORD: self.md5hash.md5salt(password),
            HttpsApiKeys.LANGUAGE: language
        }
        return await self.api_mafia_request("post", endpoint, data)

    async def email_verification(self, verification_code: str) -> dict | bytes:
        """
        Submits the email verification code to complete verification.

        Args:
            verification_code (str): The code sent to the user's email for verification.

        Returns:
            dict | bytes: A dictionary containing the server response,
            or raw bytes if the response is not in JSON format.
        """
        endpoint: Endpoints = Endpoints(Endpoints.USER_EMAIL_VERIFICATION)
        data: dict[str, str] = {
            HttpsApiKeys.VERIFICATION_CODE: verification_code
        }
        return await self.api_mafia_request("post", endpoint, data)

    async def user_get(self, user_id: str) -> dict | bytes:
        """
        Retrieves public information about a user by their ID.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            dict | bytes: A dictionary with the user's public profile data,
            or raw bytes if the response is not in JSON format.
        """
        endpoint: Endpoints = Endpoints(Endpoints.USER_GET)
        data: dict[str, str] = {
            HttpsApiKeys.USER_OBJECT_ID: user_id
        }
        return await self.api_mafia_request("post", endpoint, data)

    async def backpack_get(self) -> dict | bytes:
        """
        Fetches the contents of the user's backpack.

        Returns:
            dict | bytes: A dictionary containing the backpack items,
            or raw bytes if the response is not in JSON format.
        """
        endpoint: Endpoints = Endpoints(Endpoints.BACKPACK_GET)
        return await self.api_mafia_request("post", endpoint)

    async def backpack_get_bonus_prices(self) -> dict | bytes:
        """
        Retrieves bonus price information for backpack items.

        Returns:
            dict | bytes: A dictionary with bonus pricing details,
            or raw bytes if the response is not in JSON format.
        """
        endpoint: Endpoints = Endpoints(Endpoints.BACKPACK_GET_BONUS_PRICES)
        return await self.api_mafia_request("post", endpoint)
