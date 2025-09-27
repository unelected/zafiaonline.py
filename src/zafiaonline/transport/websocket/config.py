# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 unelected
#
# This file is part of the zafiaonline project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
WebSocket server configuration loader.

This module provides the `Config` class for loading WebSocket server
connection settings from a YAML file. The configuration includes server
address, port, and connection type, with sensible defaults if values
are missing.

Typical usage example:
    config = Config()
    print(config.address, config.port, config.connect_type)
"""
import yaml

from importlib.resources import files, as_file


class Config:
    """
    Loads WebSocket server configuration from a YAML file.

    Reads settings from a YAML configuration file and assigns them to instance
    attributes. If any values are missing, sensible defaults are used.

    Attributes:
        address (str): WebSocket server hostname or IP. Defaults to "dottap.com".
        port (int): WebSocket server port. Defaults to 7091.
        connect_type (str): WebSocket protocol ("ws" or "wss"). Defaults to "wss".
    """
    def __init__(self, path: str = "ws_config.yaml") -> None:
        """
        Initializes the Config instance by loading settings from a YAML file.

        Args:
            path (str): Path to the YAML configuration file. Defaults to 'ws_config.yaml'.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            yaml.YAMLError: If the YAML content is malformed.
        """
        config_path = files('zafiaonline.transport.websocket').joinpath(path)
        with as_file(config_path) as resource_file:
            with open(resource_file, "r") as config_file:
                config: dict = yaml.safe_load(config_file)
        self.address: str = config.get("address", "dottap.com")
        self.port: int = config.get("port", 7091)
        self.connect_type: str = config.get("connect_type", "wss")

