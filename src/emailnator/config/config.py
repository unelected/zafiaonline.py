# Copyright (C) 2025 unelected
#
# This file is part of email_generator.
#
# account_generator is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# account_generator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with account_generator. If not, see
# <https://www.gnu.org/licenses/>.

"""
Configuration settings for the EmailNator client.

This module provides functions to load configuration settings from a YAML
file into a Config object. It includes settings for the API base URL,
timeout, HTTP options, user agent, and Gmail-specific configuration.


Typical Usage Example:
    config = load_config()
    print(config.BASE_URL)
    'https://www.emailnator.com'
"""
import yaml

from pathlib import Path

from emailnator.config.helpers import format_gmail_config
from emailnator.helpers.logger import logger


class Config:
    """
    Configuration settings for the EmailNator client.

    This class holds all constants and default settings required for
    interacting with the EmailNator API, including the base URL, timeout,
    HTTP options, user agent, and Gmail-specific configuration.

    Attributes:
        BASE_URL (str): Base URL of the EmailNator API.
        TIMEOUT (int): Default timeout for API requests, in seconds.
        USE_HTTP2 (bool): Whether to use HTTP/2 for requests.
        USER_AGENT (str): Default User-Agent header for HTTP requests.
        GMAIL_CONFIG (list): Default options for generating Gmail addresses.
        PROXY (str | None): Proxy address (e.g., "http://127.0.0.1:8080") or
        - ``None`` if no proxy is used.
    """
    BASE_URL: str
    TIMEOUT: int
    USE_HTTP2: bool
    USER_AGENT: str
    GMAIL_CONFIG: list
    PROXY: str | None

    def set_proxy(self, proxy: str | None) -> None:
        """
        Set or remove the proxy configuration.

        Args:
            proxy (str | None): Proxy address to use for requests.
            - Use ``None`` to disable proxying.
        """
        self.PROXY = proxy

def load_config(
        path: str | Path = Path(__file__).parent / "config.yaml"
) -> Config:
    """
    Load configuration settings from a YAML file into a Config object.

    Reads the YAML file at the given path and populates a Config instance
    with values for API base URL, timeout, HTTP options, user agent, and
    Gmail generation configuration. Default values are used if keys are
    missing.

    Args:
        path (str | Path, optional): Path to the YAML configuration file.
            Defaults to `config.yaml` in the same directory as this module.

    Returns:
        Config: An instance of the Config class populated with settings
            from the YAML file or default values.
    """
    try:
        with open(path, "r", encoding="utf-8") as config_file:
            data: dict[str, int | bool | str] = yaml.safe_load(config_file)
    except FileNotFoundError:
        logger.error(f"File {path}is not found")
        raise

    config: Config = Config()
    config.BASE_URL = str(data.get("BASE_URL", "https://www.emailnator.com"))
    config.TIMEOUT = int(data.get("TIMEOUT", 15))
    config.USE_HTTP2 = bool(data.get("USE_HTTP2", True))
    config.USER_AGENT = str(
        data.get(
            "USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        )
    )
    value = data.get("GMAIL_CONFIG", ["dotGmail", "plusGmail"])
    config.GMAIL_CONFIG = format_gmail_config(value)
    proxy = data.get("PROXY", None)
    config.PROXY = None if proxy is None else str(proxy)
    return config


config: Config = load_config()
