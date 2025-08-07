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
WebSocket support for real-time client-server communication.

This module handles low-level asynchronous messaging over WebSocket for a client,
including authentication, message parsing, error handling, and lifecycle control.

It is intended to be used as part of a larger client framework.

Typical usage example:

    client = Client(...)
    ws = Websocket(client)
    await ws.create_connection()
    data = await ws.get_data("some_event")
    await ws.disconnect()
"""
import json
import asyncio
import sys
import ssl

import websockets
import yaml

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosedOK,  ConnectionClosed
from typing import Any, TYPE_CHECKING, Union
from importlib.resources import files, as_file

if TYPE_CHECKING:
    from zafiaonline.main import Client
from zafiaonline.structures import PacketDataKeys
from zafiaonline.utils.exceptions import BanError
from zafiaonline.utils.logging_config import logger


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
        config_path = files('zafiaonline.transport').joinpath(path)
        with as_file(config_path) as resource_file:
            with open(resource_file, "r") as config_file:
                config = yaml.safe_load(config_file)
        self.address: str = config.get("address", "dottap.com")
        self.port: int = config.get("port", 7091)
        self.connect_type: str = config.get("connect_type", "wss")


class WebSocketHandler():
    """Manages the lifecycle of a WebSocket client connection.

    Handles connection setup, graceful disconnection, reconnection with
    exponential backoff, and background listening for incoming messages.
    Designed for robust operation in unreliable network environments.

    Attributes:
        alive (bool): Indicates whether the connection is currently active.
        ws (websockets.WebSocketClientProtocol | None): The active WebSocket connection instance.
        uri (str): The WebSocket server URI to connect to.
        ws_lock (asyncio.Lock): Lock used to protect concurrent access to the WebSocket.
        listener_task (asyncio.Task | None): Background task that listens for incoming messages.
        websocket (Any): The WebSocket wrapper that manages low-level connection logic.
        data_queue (asyncio.Queue): Queue for storing received messages.
        client (Any): Optional reference to the parent client or controller.
    """
    def __init__(self, socket) -> None:
        """
        Initializes the WebSocket handler with configuration and state.

        Args:
            socket (Websocket): The underlying WebSocket client wrapper.

        """
        config: Config = Config()
        self.alive: bool | None = None
        self.ws: websockets.ClientConnection | None = None
        self.data_queue: asyncio.Queue = asyncio.Queue()
        self.listener_task: asyncio.Task | None = None
        self.uri: str = f"{config.connect_type}://{config.address}:{config.port}"
        self.ws_lock: asyncio.Lock = asyncio.Lock()
        self.websocket: Websocket = socket


    async def __listener(self) -> None:
        """
        Listens for incoming WebSocket messages and enqueues them.

        Continuously receives text or binary messages from the active WebSocket
        connection and adds them to `self.data_queue`, handling normal and
        unexpected disconnections, task cancellation, and reconnection.

        Returns:
            None

        Raises:
            AttributeError: If there is no active WebSocket connection.
            KeyboardInterrupt: If the listener is interrupted by a keyboard interrupt.
        """
        while self.alive:
            try:
                if not self.ws:
                    raise AttributeError
                message: Union[str, bytes] = await self.ws.recv()
                await self.data_queue.put(message)

            except ConnectionClosedOK:
                logger.debug("Connection closed normally (1000).")
                break
            except websockets.exceptions.ConnectionClosedError as e:
                logger.warning(f"Connection closed unexpectedly: {e}")
                break
            except asyncio.CancelledError:
                logger.debug("Listener task was cancelled.")
                break
            except websockets.ConnectionClosed:
                logger.warning(
                    "WebSocket connection lost. Attempting to reconnect...")
                asyncio.create_task(self._reconnect())
                break
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"Unexpected error in __listener: {e}")
                if self.websocket is None:
                    raise AttributeError("No WebSocket")
                await self.websocket.disconnect()
                break

    async def __on_connect(self) -> None:
        """
        Performs handshake actions after establishing a WebSocket connection.

        Sends an initial handshake message over the active WebSocket and logs the event.
        ConnectionClosed and other exceptions are handled internally and logged.

        Returns:
            None
        """
        try:
            if not self.ws:
                raise AttributeError
            await self.ws.send("Hello, World!")
            logger.debug("Sent initial handshake message.")
        except websockets.ConnectionClosed as e:
            logger.error(f"WebSocket closed before sending handshake: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in __on_connect: {e}")

    async def _cancel_listener_task(self) -> None:
        """
        Cancels the background listener task if it is still running.

        If `self.listener_task` exists and is not yet done, this method
        cancels it to stop processing incoming WebSocket messages, enabling
        a graceful shutdown or reconnection. It is safe to call multiple times.

        Returns:
            None
        """
        if self.listener_task and not self.listener_task.done():
            self.listener_task.cancel()
            logger.debug("Listener task cancelled.")

    async def _connect(self, proxy: str | None = None) -> None:
        """
        Creates a WebSocket connection to the configured server URI.

        Initializes a low-level WebSocket connection using `self.uri`, applies
        the provided proxy settings, and includes a User-Agent header to mimic
        a common HTTP client. On success, sets `self.alive` to True.

        Args:
        proxy:
            Optional proxy URL for the connection. If None, no proxy is used.

        Returns:
        None.

        Raises:
        websockets.exceptions.InvalidURI:
            If `self.uri` has an invalid format.
        websockets.exceptions.InvalidHandshake:
            If the WebSocket handshake fails.
        Exception:
            For any other errors encountered during the connection attempt.
        """
        headers: dict[str, str] = {
            "User-Agent": "okhttp/4.12.0"
        }
        if not headers:
            raise AttributeError("No headers")
        self.ws = await connect(self.uri, user_agent_header = str(headers), 
                                proxy = proxy, ssl = ssl._create_unverified_context()) 
        #FIXME: @unelected - ssl certificate is not secure
        self.alive = True

    async def _post_connect_setup(self) -> None:
        """
        Performs post-connection initialization tasks.

        Calls `__on_connect` to handle any immediate post-connection logic
        and starts the background listener task for incoming messages.

        Returns:
        None
        """
        await self.__on_connect()
        self.listener_task = asyncio.create_task(self.__listener())

    async def _reconnect(self) -> None:
        """
        Attempts to re-establish the WebSocket connection with backoff.

        When the connection is lost, this method makes up to five reconnection
        attempts using exponential backoff delays (1s, 2s, 4s, 8s, 16s, capped at 30s).
        Before each attempt, it safely closes any existing connection state by
        calling `_attempt_disconnect`. If `_try_create_connection` succeeds, the
        method returns immediately. If all attempts fail and `_should_stop_reconnect`
        returns True, it stops retrying without raising an exception.

        Returns:
            None
        """
        logger.warning("Attempting to reconnect...")

        max_attempts: int = 5
        for attempt in range(max_attempts):
            await self._attempt_disconnect()

            await asyncio.sleep(min(2 ** attempt, 30))

            if await self._try_create_connection():
                logger.info("Reconnection successful.")
                return

            logger.error(f"Reconnection attempt {attempt + 1} failed.")

        if await self._should_stop_reconnect():
            return

        logger.critical("Max reconnection attempts reached. Giving up.")

    async def _handle_reconnect(self) -> None:
        """
        Initiates a background reconnection process after connection failure.

        Sets `self.alive` to False and schedules the `_reconnect` coroutine as
        a background task without awaiting it.

        Returns:
            None
        """
        self.alive = False
        logger.info("Starting reconnection process.")
        asyncio.create_task(self._reconnect())

    async def _close_websocket(self) -> None:
        """
        Closes the WebSocket connection with a normal closure code.

        If an active WebSocket connection exists, closes it using code 1000
        (normal closure). Safe to call if the connection is already closed or
        uninitialized.

        Returns:
            None

        Raises:
            Exception: If an unexpected error occurs during closure.
        """
        try:
            if not self.ws:
                raise AttributeError
            await self.ws.close(code = 1000)
            logger.debug("WebSocket connection closed gracefully.")
        except ConnectionClosed as e:
            logger.debug(f"Connection already closed: {e}")
            return
        except Exception as e:
            logger.error(f"Error while closing WebSocket connection: {e}")
            raise

    async def _should_stop_reconnect(self) -> bool:
        """
        Determines whether reconnection attempts should cease.

        Returns:
            bool: True if the WebSocket connection is inactive and reconnection
                should stop; otherwise, False.
        """
        if not self.alive:
            logger.info("WebSocket is inactive. Stopping reconnection.")
            return True
        return False

    async def _attempt_disconnect(self) -> None:
        """
        Safely disconnects the WebSocket before attempting to reconnect.

        Acquires `self.ws_lock` to ensure no concurrent operations, then calls
        the `disconnect` method on the underlying WebSocket if the connection is alive.

        Returns:
            None
        """
        try:
            async with self.ws_lock:
                if self.alive:
                    if self.websocket is None:
                        raise AttributeError("No WebSocket")
                    await self.websocket.disconnect()
        except Exception as e:
            logger.error(f"Error during disconnect before reconnect: {e}")

    async def _try_create_connection(self) -> bool:
        """
        Attempts to establish a new WebSocket connection within a timeout.

        Calls `self.websocket.create_connection()` and waits up to 10 seconds
        for it to complete.

        Returns:
            bool: True if the connection was established successfully within
                the timeout; otherwise, False (on timeout or other errors).
        """
        try:
            if self.websocket is None:
                raise AttributeError("No WebSocket")
            await asyncio.wait_for(self.websocket.create_connection(), timeout = 10)
            return True
        except asyncio.TimeoutError:
            logger.error("Timeout while trying to reconnect.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in _try_create_connection: {e}")
            return False


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
            self.user_id = self.client.user_id
            self.token = self.client.token

    async def create_connection(self, proxy: str | None = None) -> None:
        """
        Establishes a WebSocket connection if not already connected.

        Args:
            proxy: Optional proxy address to use for the connection.

        Raises:
            websockets.exceptions.ConnectionClosed: If the WebSocket connection is closed unexpectedly.
            websockets.exceptions.InvalidStatus: If the server responds with an invalid status code.
            Exception: If an unexpected error occurs during connection initialization.
        """
        if self.alive:
            logger.info("Connection already established.")
            return

        try:
            await self._connect(proxy)
            await self._post_connect_setup()
        except (ConnectionClosed, websockets.exceptions.InvalidStatus) as e:
            logger.error(f"Connection failed: {e}. Retrying...")
            await self._handle_reconnect()
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_connection: {e}")
            await self._handle_reconnect()
            raise

    async def disconnect(self) -> None:
        """
        Gracefully closes the WebSocket connection.

        Raises:
            websockets.exceptions.ConnectionClosed: If the connection was already closed.
            Exception: If an unexpected error occurs while closing the connection.
        """
        logger.debug(
            f"Attempting to close WebSocket. self.alive={self.alive}")

        if not self.alive:
            logger.debug("WebSocket already closed.")
            return

        self.alive = False
        await self._close_websocket()
        await self._cancel_listener_task()
        logger.debug("Disconnected.")

    async def send_server(self, data: dict,
                          remove_token_from_object: bool = False) -> None:
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
        if not self.alive:
            try:
                logger.error(
                    "WebSocket is not connected. Attempting to reconnect...")
                await self._reconnect()
                if not self.alive:
                    logger.error("Reconnection failed. Dropping message.")
                    return None
            except BanError:
                return

        if not remove_token_from_object:
            if self.token and self.token is not None:
                data[PacketDataKeys.TOKEN] = self.token
            if self.user_id and self.user_id is not None:
                data.setdefault(PacketDataKeys.USER_OBJECT_ID, self.user_id)

        try:
            json_data = json.dumps(data)
            if not self.ws:
                raise AttributeError
            await self.ws.send(json_data)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data: {e}")

        except websockets.ConnectionClosed:
            logger.error(
                "WebSocket closed while sending data. Reconnecting...")
            asyncio.create_task(self._reconnect())
        return None

    async def listen(self) -> dict[str, Any] | None:
        """
        Waits for and returns a single decoded JSON message from the WebSocket queue.

        Returns:
            dict[str, Any] | None: The decoded JSON message if successful, otherwise None.

        Raises:
            KeyboardInterrupt: If execution is interrupted manually.
            json.JSONDecodeError: If a JSON decoding error escapes internal handling.
            Exception: If an unexpected error occurs during processing.
        """
        while self.alive:
            try:
                response = await asyncio.wait_for(self.data_queue.get(),
                                                  timeout = 5)

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
        return None

    async def get_data(self, mafia_type: str) -> dict[str, Any] | None:
        """
        Waits for and returns a WebSocket event matching the expected mafia type.

        Args:
            mafia_type (str): The expected event type to match. Only messages with this type,
                "empty", or an error type (`PacketDataKeys.ERROR_OCCUR`) are considered valid.

        Returns:
            dict[str, Any] | None: A dictionary with the matching message data, or None if
            listening times out or is interrupted.

        Raises:
            ValueError: If the listener returns None.
            BanError: If a USER_BLOCKED event is received.
            asyncio.TimeoutError: If no valid data is received within 10 seconds.
            KeyboardInterrupt: If execution is interrupted manually.
            Exception: For all other unexpected exceptions.
        """
        while self.alive:
            try:
                data: dict[str, Any] | None = await asyncio.wait_for(self.listen(), timeout = 10)

                if data is None:
                    logger.error("Data is None. Cannot proceed.")
                    raise ValueError("Received None data.")

                event: str | None = data.get(PacketDataKeys.TYPE)

                if event is None and PacketDataKeys.TIME not in data:
                    logger.error(
                        f"Received data without a valid event type. data"
                        f": {data}"
                    )
                    return None

                if event in [mafia_type, PacketDataKeys.ERROR_OCCUR]: # "empty"
                    return data

                if event == PacketDataKeys.USER_BLOCKED:
                    raise BanError(self.client, data)

                logger.debug(
                    f"Unexpected event type received: {event}. Ignoring...")

            except BanError as e:
                logger.warning(e)
                await self.disconnect()
                sys.exit()

            except asyncio.TimeoutError:
                logger.warning(
                    "Timeout reached while waiting for data. Resetting...")
                return None

            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt")
                raise

            except Exception as e:
                logger.error(f"Unexpected error in get_data: {e}")
                raise
        return None

    async def safe_get_data(self, key: str, retries: int = 2, delay: int = 2) -> dict[str, Any]:
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
            f"Failed to get data for {key} after {retries} retries")
