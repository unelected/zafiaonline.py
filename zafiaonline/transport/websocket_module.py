import json
import asyncio
import sys

import websockets

from websockets import ConnectionClosedOK, connect, ConnectionClosed
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from zafiaonline.main import Client
from zafiaonline.structures import PacketDataKeys
from zafiaonline.utils.exceptions import BanError
from zafiaonline.utils.logging_config import logger

class Config:
    #TODO сделать env
    address = "dottap.com"
    port = 7091

class Websocket:
    #TODO сделать метакласс
    def __init__(self, client: Optional["Client"] = None) -> None:
        """
        Initializes the WebSocket client for handling real-time communication.

        **Parameters**
            - **client** (*Client*): Reference to the main client instance.

        **Attributes**
            - **data_queue** (*asyncio.Queue*): Queue for storing incoming
            messages.
            - **alive** (*Optional[bool]*): Connection status flag.
            - **ws**: WebSocket connection
            instance.
            - **uri** (*str*): WebSocket server address.
            - **listener_task** (*Optional[asyncio.Task]*): Background task
            for listening to messages.
            - **ws_lock** (*asyncio.Lock*): Lock to ensure thread-safe
            WebSocket operations.
        """
        self.client = client
        self.data_queue = asyncio.Queue()
        self.alive: Optional[bool] = None
        self.ws = None
        self.uri = f"wss://{Config.address}:{Config.port}"
        self.listener_task: Optional[asyncio.Task] = None
        self.ws_lock = asyncio.Lock()
        self.user_id = None
        self.token = None

    def update_auth_data(self):
        """Обновляет user_id и token в Websocket после авторизации."""
        if self.client:
            self.user_id = self.client.user_id
            self.token = self.client.token

    async def create_connection(self) -> None:
        """
        Establishes a WebSocket connection if not already connected.

        This method is responsible for setting up a persistent WebSocket
        connection to the server. It ensures that only one active connection
        exists at a time, handles potential connection failures, and initiates
        necessary post-connection setup (such as authentication and starting
        the listener for incoming messages).

        **Workflow:**
            1. Checks if a connection is already active (`self.alive`).
            2. Attempts to establish a new WebSocket connection.
            3. Calls `_post_connect_setup()` to perform necessary
            initialization.
            4. Starts a background task (`__listener()`) to listen for
            incoming messages.
            5. If the connection attempt fails, retries using
            `_handle_reconnect()`.

        **Example Usage:**
            ```python
            client = WebsocketClient(uri="wss://example.com/socket")
            await client.create_connection()
            ```

        **Raises:**
            - `websockets.exceptions.ConnectionClosed`: If the WebSocket
            connection is closed unexpectedly.
            - `websockets.exceptions.InvalidStatus`: If the server
            responds with an invalid status code.
            - `Exception`: For any other unforeseen errors during
            connection initialization.

        **Notes:**
            - This method is asynchronous and should be awaited to ensure
            proper execution.
            - If the connection is lost, `_handle_reconnect()` will attempt
            to restore it.
        """
        if self.alive:
            logger.info("Connection already established.")
            return

        try:
            await self._connect()
            await self._post_connect_setup()
        except (ConnectionClosed, websockets.exceptions.InvalidStatus) as e:
            logger.error(f"Connection failed: {e}. Retrying...")
            await self._handle_reconnect()
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_connection: {e}")
            await self._handle_reconnect()
            raise

    async def _connect(self) -> None:
        """Creates a WebSocket connection to the server."""
        headers = {
            "User-Agent": "okhttp/4.12.0"
        }
        self.ws = await connect(self.uri, user_agent_header=headers)
        self.alive = True

    async def _post_connect_setup(self) -> None:
        """Handles actions after establishing a successful connection."""
        await self.__on_connect()
        self.listener_task = asyncio.create_task(self.__listener())

    async def _handle_reconnect(self) -> None:
        """Attempts to reconnect after a failed connection attempt."""
        self.alive = False
        asyncio.create_task(self._reconnect())

    async def disconnect(self) -> None:
        """
        Gracefully closes the WebSocket connection.

        This method ensures a clean shutdown of the WebSocket connection,
        preventing resource leaks and handling any unexpected errors that
        may occur during closure.
        If the connection is already closed, it simply logs the event and
        exits.

        **Workflow:**
            1. Checks if the connection is active (`self.alive`).
            2. Sets `self.alive` to `False` to prevent further operations.
            3. Calls `_close_websocket()` to properly close the connection.
            4. Cancels the background listener task (`__listener()`) to
            stop receiving messages.
            5. Logs the successful disconnection.

        **Example Usage:**
            ```python
            client = WebsocketClient(uri="wss://example.com/socket")
            await client.create_connection()
            # Do some operations...
            await client.disconnect()
            ```

        **Logs:**
            - Logs an attempt to close the connection.
            - Logs if the WebSocket is already closed.
            - Logs when the disconnection process is successfully completed.

        **Raises:**
            - `websockets.exceptions.ConnectionClosed`: If the connection
            was already closed.
            - `Exception`: If an unexpected error occurs while closing the
            connection.

        **Notes:**
            - This method is asynchronous and should be awaited to ensure
            proper execution.
            - After calling this method, the client instance should not be
            used unless reconnected.
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

    async def _close_websocket(self) -> None:
        """Closes the WebSocket connection with a normal status code (1000)."""
        try:
            await self.ws.close(code=1000)
            logger.debug("WebSocket connection closed gracefully.")
        except ConnectionClosed as e:
            logger.debug(f"Connection already closed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error while closing WebSocket connection: {e}")
            raise

    async def _cancel_listener_task(self) -> None:
        """Cancels the listener task if it is still running."""
        if self.listener_task and not self.listener_task.done():
            self.listener_task.cancel()
            logger.debug("Listener task cancelled.")

    async def send_server(self, data: dict,
                          remove_token_from_object: bool = False) -> None:
        """
        Sends data to the server via WebSocket.

        **Parameters**
            - **data** (*dict*): The data payload to send.
            - **remove_token_from_object** (*bool*): If True, removes the
            token before sending.

        **Behavior**
            - Ensures the WebSocket connection is alive.
            - Automatically attempts reconnection if disconnected.
            - Adds authentication details unless explicitly disabled.

        **Exceptions**
            - Logs errors for JSON encoding issues.
            - Handles WebSocket disconnections and attempts reconnection.
        """
        if not self.alive and not BanError:
            logger.error(
                "WebSocket is not connected. Attempting to reconnect...")
            await self._reconnect()
            if not self.alive:
                logger.error("Reconnection failed. Dropping message.")
                return None

        if not remove_token_from_object:
            data[PacketDataKeys.TOKEN] = self.token
            data.setdefault(PacketDataKeys.USER_OBJECT_ID, self.user_id)

        try:
            json_data = json.dumps(data)
            await self.ws.send(json_data)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data: {e}")

        except websockets.ConnectionClosed:
            logger.error(
                "WebSocket closed while sending data. Reconnecting...")
            asyncio.create_task(self._reconnect())
        return None

    async def listen(self) -> dict:
        """
        Listens for incoming messages from the WebSocket queue.

        **Returns**
            - **dict**: Decoded JSON response from the queue.

        **Behavior**
            - Waits for messages in the queue with a timeout of 5 seconds.
            - Handles JSON decoding errors gracefully.
            - Logs unexpected errors and continues listening.

        **Exceptions**
            - Raises `KeyboardInterrupt` for manual termination.
            - Logs and continues on unexpected exceptions.
        """
        while self.alive:
            try:
                response = await asyncio.wait_for(self.data_queue.get(),
                                                  timeout = 5)

                if response is None:
                    logger.error("Received None response from queue")
                    continue

                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {response}")
                    continue

            except asyncio.TimeoutError:
                logger.debug("Listen timeout, no data received.")
                continue

            except json.JSONDecodeError:
                logger.error("Invalid JSON format in received data.")
                raise

            except KeyboardInterrupt:
                raise

            except Exception as e:
                logger.error(f"Unexpected error in listen: {e}")
        return None

    async def get_data(self, mafia_type: str) -> Optional[dict]:
        """
        Retrieves data from the WebSocket listener and filters it based on
        the given mafia type.

        **Parameters**
            - **mafia_type** (*str*): The expected event type to filter
            responses.

        **Returns**
            - **dict**: The received and validated JSON data.

        **Behavior**
            - Listens for incoming data.
            - Checks if the event type matches the expected `mafia_type`,
            "empty", or an error.
            - Continues listening until a valid response is received.
            - Raises errors on unexpected exceptions.

        **Exceptions**
            - Raises `KeyboardInterrupt` for manual termination.
            - Logs and raises on unexpected errors.
        """
        while self.alive:
            try:
                data = await asyncio.wait_for(self.listen(), timeout = 10)

                if data is None:
                    logger.error("Data is None. Cannot proceed.")
                    raise ValueError("Received None data.")

                event = data.get(PacketDataKeys.TYPE)

                if event is None and PacketDataKeys.TIME not in data:
                    logger.error(
                        f"Received data without a valid event type. data"
                        f": {data}"
                    )
                    return None

                if event in [mafia_type, "empty", PacketDataKeys.ERROR_OCCUR]:
                    return data

                if event == PacketDataKeys.USER_BLOCKED:
                    raise BanError(data, self.client)

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

    async def safe_get_data(self, key, retries = 2, delay=2):
        for attempt in range(retries):
            try:
                data = await self.get_data(key)
                if data is not None:
                    return data
            except ValueError:
                return None
            except Exception as e:
                logger.error(f"Unexpected error in get_data: {e}")
                await asyncio.sleep(delay)
        raise ValueError(
            f"Failed to get data for {key} after {retries} retries")

    async def _reconnect(self) -> None:
        """
        Attempts to reconnect the WebSocket client.

        **Behavior**
            - Tries up to 5 times to reconnect.
            - Uses exponential backoff for retry delays.
            - Ensures the WebSocket is properly closed before reconnecting.
            - Stops if the connection is marked inactive.

        **Exceptions**
            - Logs errors and raises on repeated failures.
        """
        logger.warning("Attempting to reconnect...")

        max_attempts = 5
        for attempt in range(max_attempts):
            await self._attempt_disconnect()

            await asyncio.sleep(min(2 ** attempt, 30))  # Exponential backoff

            if await self._try_create_connection():
                logger.info("Reconnection successful.")
                return

            logger.error(f"Reconnection attempt {attempt + 1} failed.")

        if await self._should_stop_reconnect():
            return

        logger.critical("Max reconnection attempts reached. Giving up.")

    async def _should_stop_reconnect(self) -> bool:
        """Checks if reconnection should stop due to an inactive WebSocket."""
        if not self.alive:
            logger.info("WebSocket is inactive. Stopping reconnection.")
            return True
        return False

    async def _attempt_disconnect(self) -> None:
        """Safely attempts to disconnect the WebSocket before reconnecting."""
        try:
            async with self.ws_lock:
                if self.alive:
                    await self.disconnect()
        except Exception as e:
            logger.error(f"Error during disconnect before reconnect: {e}")

    async def _try_create_connection(self) -> bool:
        """Attempts to create a new WebSocket connection with a timeout."""
        try:
            await asyncio.wait_for(self.create_connection(), timeout=10)
            return True
        except asyncio.TimeoutError:
            logger.error("Timeout while trying to reconnect.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in _try_create_connection: {e}")
            return False

    async def __on_connect(self) -> None:
        """
        Handles actions to be performed upon establishing a WebSocket
        connection.

        **Behavior**
            - Sends a handshake message to confirm connection.
        """
        try:
            await self.ws.send("Hello, World!")
            logger.debug("Sent initial handshake message.")
        except websockets.ConnectionClosed as e:
            logger.error(f"WebSocket closed before sending handshake: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in __on_connect: {e}")

    async def __listener(self) -> None:
        """
        Listens for incoming WebSocket messages and adds them to the queue.

        **Behavior**
            - Continuously receives messages while the connection is active.
            - Handles various disconnection scenarios and attempts
            reconnection if necessary.
        """
        while self.alive:
            try:
                message = await self.ws.recv()
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
                await self.disconnect()
                break
