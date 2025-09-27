from typing import Any

from zafiaonline.structures.packet_data_keys import Endpoints
from zafiaonline.transport.http.http_wrapper import HttpWrapper
from zafiaonline.structures.enums import HttpsTrafficTypes


class HttpsHelpers:
    def __init__(self) -> None:
        self.http: HttpWrapper = HttpWrapper()

    async def get_mafia_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None
    ) -> dict[str, Any] | bytes:
        """
        Perform a GET request to the MafiaOnline API.

        Args:
            endpoint (str): API endpoint path or full URL.
            params (dict[str, Any] | None): Optional query parameters.

        Returns:
            dict[str, Any] | bytes: JSON-decoded response if available,
            otherwise raw bytes or dict with an "error" key.
        """
        return await self.http.mafia_request(
            HttpsTrafficTypes.GET,
            endpoint,
            params=params
        )

    async def post_api_mafia_request(
        self,
        endpoint: Endpoints,
        data: dict[str, Any] | None = None
    ) -> dict[str, Any] | bytes:
        """
        Perform a POST request to the MafiaOnline API.

        Args:
            endpoint (str): API endpoint path or full URL.
            data (dict[str, Any] | None): Data to include in the POST body.
            headers (dict[str, str] | None): Optional request headers.

        Returns:
            dict[str, Any] | bytes: JSON-decoded response if available,
            otherwise raw bytes or dict with an "error" key.
        """
        return await self.http.api_mafia_request(
            HttpsTrafficTypes.POST,
            endpoint,
            data
        )

    async def get_api_mafia_request(
        self,
        endpoint: Endpoints,
        data: dict[str, Any] | None = None
    ) -> dict[str, Any] | bytes:
        """
        Perform a GET request to the MafiaOnline API.

        Args:
            endpoint (str): API endpoint path or full URL.
            data (dict[str, Any] | None): Data to include in the POST body.
            headers (dict[str, str] | None): Optional request headers.

        Returns:
            dict[str, Any] | bytes: JSON-decoded response if available,
            otherwise raw bytes or dict with an "error" key.
        """
        return await self.http.api_mafia_request(
            HttpsTrafficTypes.GET,
            endpoint,
            data
        )
