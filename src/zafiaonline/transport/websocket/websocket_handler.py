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
WebSocketHandler module.

Provides a high-level wrapper around a WebSocket client connection with
automatic reconnection, background message listening, and lifecycle
management. This class is designed to integrate with the zafiaonline
framework and handle unstable network conditions gracefully.

Typical usage example:
    from zafiaonline.transport.websocket.websocket_handler import WebSocketHandler
    from zafiaonline.transport.websocket.websocket_module import Websocket

    ws = Websocket(client)
    handler = WebSocketHandler(ws)
    await handler._connect()
    await handler._post_connect_setup()
"""
import asyncio
import websockets

from typing import TYPE_CHECKING
from websockets.exceptions import ConnectionClosedOK, ConnectionClosed
from websockets.asyncio.client import connect

from zafiaonline.utils.proxy_store import store
from zafiaonline.transport.websocket.config import Config
from zafiaonline.utils.logging_config import logger
from zafiaonline.utils.exceptions import BanError
if TYPE_CHECKING:
    from zafiaonline.transport.websocket.websocket_module import Websocket


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
        socket (Websocket): Optional reference to the parent client or controller.
    """
    def __init__(self, socket: "Websocket") -> None:
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
                message: str | bytes = await self.ws.recv()
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
                    "WebSocket connection lost. Attempting to reconnect..."
                )
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

    async def _connect(self) -> None:
        """
        Creates a WebSocket connection to the configured server URI.

        Initializes a low-level WebSocket connection using `self.uri`, applies
        the provided proxy settings, and includes a User-Agent header to mimic
        a common HTTP client. On success, sets `self.alive` to True.

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
            raise AttributeError("No headers in WebSocket")
        self.ws = await connect(
            self.uri,
            user_agent_header=str(headers),
            proxy=store.get_random_proxy()
        )
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
            return None

        logger.critical("Max reconnection attempts reached. Giving up.")
        return None

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
            await self.ws.close(code=1000)
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
            await asyncio.wait_for(
                self.websocket.create_connection(),
                timeout=10
            )
            return True
        except asyncio.TimeoutError:
            logger.error("Timeout while trying to reconnect.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in _try_create_connection: {e}")
            return False

    async def _possibility_of_sending(self) -> bool:
        """
        Check if sending data over the WebSocket is possible.

        This method verifies the connection state and attempts reconnection
        if the WebSocket is not alive. If reconnection fails or the client
        is banned, sending is not possible.

        Returns:
            bool: True if the WebSocket connection is alive and sending
            is possible, False otherwise.
        """
        if not self.alive:
            try: 
                logger.error(
                    "WebSocket is not connected. Attempting to reconnect..."
                )
                await self._reconnect()
                if not self.alive:
                    logger.error("Reconnection failed. Dropping message.")
                    return False
            except BanError:
                return False
        return True
