import base64
import string
import random
import aiohttp
import re

from typing import Any, Optional, Dict, Literal
from urllib.parse import urljoin
from aiohttp import ClientError
from PyBookAgents import dalvik_ugen

from zafiaonline.structures.packet_data_keys import Endpoints
from zafiaonline.utils.logging_config import logger

class Http:
    def __init__(self):
        self.zafia_url = "http://185.188.183.144:5000/zafia/"
        self.mafia_address = "dottap.com"
        self.api_mafia_address = f"api.mafia.{self.mafia_address}"
        self.mafia_url = f"https://{self.mafia_address}/"
        self.api_mafia_url = f"https://{self.api_mafia_address}/"
        self.zafia_headers = {
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.12.0"
        }
        self.mafia_headers = {
            "HOST": self.mafia_address,
            "User-Agent": self.generate_agent(),
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

    @staticmethod
    def generate_agent():
        return re.sub(r'\s*\[.*$', '', dalvik_ugen())

    @staticmethod
    def __generate_random_token(length:int = 32) -> str:
        return ''.join(random.choices(string.hexdigits.lower(), k=length))

    async def zafia_request(self, method:
                            Literal["get", "post", "put", "delete"],
                            endpoint:Endpoints, params: dict[str, Any],
                            user_id: str) -> Dict[str, Any]:
        url, headers = self.__build_zafia_headers(endpoint, user_id)
        return await self.__send_request(method = method, url = url,
                                params = params, headers = headers)

    async def mafia_request(self, method: Literal["get", "post", "put",
                            "delete"], endpoint: str,
                            params:Optional[dict[str,Any]]=None,
                            headers:Optional[dict[str, str]] = None):
        return await (self.__mafia_request(
            self.mafia_url, method, endpoint, params, headers))

    async def api_mafia_request(self, method: Literal["get", "post", "put",
                            "delete"], endpoint: str,
                            params:Optional[dict[str,Any]]=None,
                            headers:Optional[dict[str, str]] = None):
        return await (self.__mafia_request(
            self.api_mafia_url, method, endpoint, params, headers))


    async def __mafia_request(self, url, method: Literal["get", "post", "put",
                            "delete"], endpoint: Endpoints,
                            params:Optional[dict[str,Any]]=None,
                            headers:Optional[dict[str, str]] = None):
        url = urljoin(url, endpoint.value)
        return await self.__send_request(method, url, params, headers)

    def __build_headers(self, endpoint: Endpoints, user_id:
    str, headers) -> tuple[str, Dict[str, str]]:
        url = urljoin(self.zafia_url, endpoint.value)
        if endpoint == Endpoints.GET_VERIFICATIONS.value:
            return url, headers
        token = self.__generate_random_token()
        auth_raw = f"{user_id}=:={token}"
        auth_token = base64.b64encode(auth_raw.encode()).decode()
        headers["Authorization"] = auth_token
        return url, headers

    def __build_zafia_headers(self, endpoint: Endpoints, user_id:
    str) -> tuple[str, Dict[str, str]]:
        headers = self.zafia_headers.copy()
        self.__build_headers(endpoint, user_id, headers)

    def __build_mafia_headers(self, endpoint: Endpoints, user_id:
    str) -> tuple[str, Dict[str, str]]:
        headers = self.mafia_headers.copy()
        self.__build_headers(endpoint, user_id, headers)

    def __build_api_afia_headers(self, endpoint: Endpoints, user_id:
    str) -> tuple[str, Dict[str, str]]:
        #TODO: add new headers
        headers = self.mafia_headers.copy()
        self.__build_headers(endpoint, user_id, headers)

    @staticmethod
    async def __send_request(method: Literal["get", "post", "put", "delete"]
                           , url: str, params:Optional[dict[str,Any]]=None,
                           headers:Optional[dict[str, str]] = None) -> Dict[
        str, Any]:
        async with (aiohttp.ClientSession(headers=headers) as session):
            method = method.lower()
            try:
                async with getattr(session, method)(url, params = params
                                                    ) as response:
                    data = await response.json()
                    return data
            except ClientError as e:
                logger.error(
                    f"Network error during {method.upper()} request to"
                    f" {url}: {e}")
                raise
            except Exception as e:
                logger.error(f"Error {method.upper()} {url}: {e}")
                raise