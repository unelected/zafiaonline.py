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
WebSocket support for real-time client-server communication.

This module provides an asynchronous WebSocket client with support for
authentication, message handling, error management, and lifecycle control.
It is designed as part of the zafiaonline framework to enable robust
real-time communication between client and server.

Typical usage example:
    from zafiaonline.main import Client
    from zafiaonline.transport.websocket.websocket import Websocket

    client = Client(...)
    ws = Websocket(client)
    await ws.create_connection()
    await ws.send_server({"ty": "sin"})
    data = await ws.get_data("sin")
    await ws.disconnect()
"""
import json
import asyncio
import sys

import websockets

from websockets.exceptions import  ConnectionClosed
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from zafiaonline.main import Client
from zafiaonline.structures import PacketDataKeys
from zafiaonline.utils.exceptions import BanError
from zafiaonline.utils.logging_config import logger
from zafiaonline.transport.websocket.websocket_handler import WebSocketHandler


#TODO: @unelected - сделать метакласс
class Websocket(WebSocketHandler):
    """
    Manages a WebSocket connection with support for authentication, message handling,
    and graceful shutdown.

    Attributes:
        client (Client): Reference to the main client instance, used for syncing data.
        user_id (str | None): Identifier of the authenticated user, synced from the client.
        token (str | None): Authentication token, synced from the client.
    """
    def __init__(self, client: "Client") -> None:
        """
        Initializes the WebSocket client for handling real-time communication.

        Args:
            client (Client): Reference to the main client instance.
        """
        self.client: Client = client
        self.user_id: str | None = None
        self.token: str | None = None
        super().__init__(self)

    def update_auth_data(self) -> None:
        """
        Updates `user_id` and `token` from the client instance.

        Copies authentication data from the associated client, if available.

        Returns:
            None
        """
        if self.client:
            self.user_id = self.client.auth.user_id
            self.token = self.client.auth.token
        return None

    async def create_connection(self) -> None:
        """
        Establishes a WebSocket connection if not already connected.

        Raises:
            websockets.exceptions.ConnectionClosed: If the WebSocket connection is closed unexpectedly.
            websockets.exceptions.InvalidStatus: If the server responds with an invalid status code.
            Exception: If an unexpected error occurs during connection initialization.
        """
        if self.alive:
            logger.info("Connection already established.")
            return None

        try:
            await self._connect()
            await self._post_connect_setup()
        except (ConnectionClosed, websockets.exceptions.InvalidStatus) as e:
            logger.error(f"Connection failed: {e}. Retrying...")
            await self._handle_reconnect()
            raise
        except websockets.exceptions.InvalidProxy as e:
            logger.error(f"Proxy is invalid: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_connection: {e}")
            await self._handle_reconnect()
            raise
        return None

    async def disconnect(self) -> None:
        """
        Gracefully closes the WebSocket connection.

        Raises:
            websockets.exceptions.ConnectionClosed: If the connection was already closed.
            Exception: If an unexpected error occurs while closing the connection.
        """
        logger.debug(
            f"Attempting to close WebSocket. self.alive={self.alive}"
        )

        if not self.alive:
            logger.debug("WebSocket already closed.")
            return

        self.alive = False
        await self._close_websocket()
        await self._cancel_listener_task()
        logger.debug("Disconnected.")

    async def send_server(
        self,
        data: dict,
        remove_token_from_object: bool = False
    ) -> None:
        """
        Sends a JSON-encoded payload to the WebSocket server.

        Args:
            data (dict): The data payload to send over the WebSocket.
            remove_token_from_object (bool): If True, omits authentication
                details ('token' and 'user_id') from the outgoing message.

        Raises:
            json.JSONDecodeError: If serialization fails.
            AttributeError: If the WebSocket instance is unexpectedly missing.
            websockets.ConnectionClosed: If the WebSocket is closed during send.

        Returns:
            None
        """

        packet: dict = await self._make_packet(
            data,
            remove_token_from_object
        )

        try:
            json_data: str = json.dumps(packet)
            if not self.ws:
                raise AttributeError("No self.ws")
            await self.ws.send(json_data)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data: {e}")

        except websockets.ConnectionClosed:
            logger.error(
                "WebSocket closed while sending data. Reconnecting..."
            )
            asyncio.create_task(self._reconnect())
        return None

    async def _make_packet(
            self,
            data: dict,
            remove_token_from_object: bool
    ) -> dict:
        """
        Build the final packet structure for WebSocket transmission.

        This method wraps the provided payload into a packet that follows
        the server communication protocol. The payload is placed under the
        data key, while a fixed version code is added at the root level.
        Optionally, authentication details (token and user_id) are
        included in the payload.

        Args:
            data (dict): The payload data to embed inside the packet.
            remove_token_from_object (bool): If True, omits authentication
            details (token and user_id) from the payload.

        Returns:
            dict: A dictionary representing the final packet structure.
        """
        inner: dict = data.copy()
        if not remove_token_from_object:
            if self.token and self.token is not None:
                inner[PacketDataKeys.TOKEN] = self.token
            if self.user_id and self.user_id is not None:
                inner.setdefault(
                    PacketDataKeys.USER_OBJECT_ID,
                    self.user_id
                )
        return {
            PacketDataKeys.DATA: inner,
            PacketDataKeys.VERSION_CODE: 55
        }

    async def listen(self) -> dict[str, Any]:
        """
        Waits for and returns a single decoded JSON message from the WebSocket queue.

        Returns:
            dict[str, Any]: The decoded JSON message.

        Raises:
            KeyboardInterrupt: If execution is interrupted manually.
            asyncio.CancelledError: If the listener stops because self.alive is False.
            json.JSONDecodeError: If a JSON decoding error escapes internal handling.
            Exception: If an unexpected error occurs during processing.
        """
        while self.alive:
            try:
                response: str = await asyncio.wait_for(
                    self.data_queue.get(),
                    timeout = 5
                )
                if response is None:
                    logger.error("Received None response from queue")

                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {response}")

            except asyncio.TimeoutError:
                logger.debug("Listen timeout, no data received.")

            except json.JSONDecodeError:
                logger.error("Invalid JSON format in received data.")
                raise

            except KeyboardInterrupt:
                raise

            except Exception as e:
                logger.error(f"Unexpected error in listen: {e}")

        raise asyncio.CancelledError("Listener stopped because self.alive is False")

    async def get_data(self, mafia_type: str) -> dict[str, Any]:
        """
        Waits for and returns a WebSocket event matching the expected mafia type.

        Args:
            mafia_type (str): The expected event type to match. Only messages with this type,
            "empty", or an error type (`PacketDataKeys.ERROR_OCCUR`) are considered valid.

        Returns:
            dict[str, Any]: A dictionary with the matching message data.

        Raises:
            RuntimeError: If an unexpected event is received (e.g., GAME_STARTED).
            BanError: If a USER_BLOCKED event is received.
            asyncio.CancelledError: If the get_data stops because self.alive is False.
            asyncio.TimeoutError: If no valid data is received within 10 seconds.
            KeyboardInterrupt: If execution is interrupted manually.
            Exception: For all other unexpected exceptions.
        """
        while self.alive:
            try:
                data: dict[str, Any] = await asyncio.wait_for(
                    self.listen(),
                    timeout=10
                )
                event: str | None = data.get(PacketDataKeys.TYPE)

                if event is None and PacketDataKeys.TIME not in data:
                    raise TypeError(
                        f"Received data without a valid event type. data"
                        f": {data}"
                    )

                if event in [mafia_type, PacketDataKeys.ERROR_OCCUR]: # "empty"
                    return data

                if event == PacketDataKeys.USER_BLOCKED:
                    raise BanError(self.client, data)

                elif event == PacketDataKeys.GAME_STARTED:
                    raise RuntimeError(f"Game in room is started")

                elif event == PacketDataKeys.USER_USING_DOUBLE_ACCOUNT:
                    raise RuntimeError(
                        "Used double account. Please use proxy"
                    )

                logger.debug(
                    f"Unexpected event type received: {event}."
                )

            except BanError as e:
                logger.warning(e)
                await self.disconnect()
                sys.exit()

            except asyncio.TimeoutError:
                logger.warning(
                    "Timeout reached while waiting for data. Resetting..."
                )
                raise

            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt")
                raise

            except Exception as e:
                logger.error(f"Unexpected error in get_data: {e}")
                raise
        raise asyncio.CancelledError(
            "get_data stopped because self.alive is False"
        )

    async def safe_get_data(
            self,
            key: str,
            retries: int = 2,
            delay: int = 2
    ) -> dict[str, Any]:
        """
        Attempts to retrieve data associated with the given key, retrying on failure.

        Args:
            key (str): The event type to request via `get_data`.
            retries (int, optional): Number of retry attempts. Defaults to 2.
            delay (int, optional): Delay between retries in seconds. Defaults to 2.

        Returns:
            dict[str, Any]: The first non-None response returned by `get_data`.

        Raises:
            ValueError: If all attempts fail or return None.
        """
        for _ in range(retries):
            try:
                data: dict[str, Any] | None = await self.get_data(key)
                if data is not None:
                    return data
            except Exception as e:
                logger.error(f"Unexpected error in get_data: {e}")
                await asyncio.sleep(delay)
        raise ValueError(
            f"Failed to get data for {key} after {retries} retries"
        )
