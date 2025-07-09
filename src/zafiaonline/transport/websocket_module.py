import json
import asyncio
import sys
import os

import websockets
import yaml

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosedOK,  ConnectionClosed
from typing import Any, Optional, TYPE_CHECKING, Union
from importlib.resources import files, as_file

if TYPE_CHECKING:
    from zafiaonline.main import Client
from zafiaonline.structures import PacketDataKeys
from zafiaonline.utils.exceptions import BanError
from zafiaonline.utils.logging_config import logger


class Config:
    """
    Loads WebSocket server configuration from a YAML file.

    This class reads settings from a YAML file and assigns them to instance attributes.
    If any values are missing, sensible defaults are applied.

    Attributes:
        address (str): Hostname or IP address of the WebSocket server. Defaults to 'dottap.com'.
        port (int): Port number of the WebSocket server. Defaults to 7091.
        connect_type (str): Protocol type, either 'ws' or 'wss'. Defaults to 'wss'.

    Args:
        path (str, optional): Path to the YAML configuration file. Defaults to 'ws_config.yaml'.

    Raises:
        FileNotFoundError: If the YAML file is not found.
        yaml.YAMLError: If the YAML content is malformed.

    Examples:
        Instantiate and access attributes:

            config = Config()
            print(config.address)       # e.g. 'dottap.com'
            print(config.port)          # e.g. 7091
            print(config.connect_type)  # e.g. 'wss'

        Example contents of ws_conf.yaml:

            address: '37.143.8.68'
            port: 7090
            connect_type: 'ws'

    Notes:
        Default ports are based on the protocol:
            - 7090 for 'ws'
            - 7091 for 'wss'
    """
    def __init__(self, path: str = "ws_config.yaml") -> None:
        """
        Initializes the Config instance by loading settings from a YAML file.

        Args:
            path (str, optional): Path to the YAML configuration file. Defaults to 'ws_config.yaml'.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            yaml.YAMLError: If the YAML content is malformed.

        Attributes:
            Loads the following keys from the YAML file:
                - 'address' (str): WebSocket server hostname or IP. Defaults to 'dottap.com'.
                - 'port' (int): WebSocket server port. Defaults to 7091.
                - 'connect_type' (str): Protocol type ('ws' or 'wss'). Defaults to 'wss'.

        Notes:
            Default ports are based on the protocol:
                - 7090 for 'ws'
                - 7091 for 'wss'
        """
        config_path = files('zafiaonline.transport').joinpath(path)
        with as_file(config_path) as resource_file:
            with open(resource_file, "r") as config_file:
                config = yaml.safe_load(config_file)
        self.address: str = config.get("address", "dottap.com")
        self.port: int = config.get("port", 7091)
        self.connect_type: str = config.get("connect_type", "wss")


class Websocket:
    #TODO сделать метакласс
    def __init__(self, client: "Client") -> None:
        """
        Initializes the WebSocket client for handling real-time communication.

        Args:
            client (Optional[Client]): Reference to the main client instance.

        Attributes:
            client (Optional[Client]): The main client instance (if provided).
            data_queue (asyncio.Queue): Queue for storing incoming messages.
            alive (Optional[bool]): Connection status flag.
            ws (Optional[websockets.WebSocketClientProtocol]): WebSocket connection instance.
            uri (str): WebSocket server address.
            listener_task (Optional[asyncio.Task]): Background task for listening to messages.
            ws_lock (asyncio.Lock): Lock to ensure thread-safe WebSocket operations.
            user_id (Optional[str]): Identifier of the user (to be set after auth).
            token (Optional[str]): Authentication token (to be set after auth).
        """
        config = Config()
        self.client = client
        self.data_queue = asyncio.Queue()
        self.alive: bool | None = None
        self.ws = None
        self.uri = f"{config.connect_type}://{config.address}:{config.port}"
        self.listener_task: Optional[asyncio.Task] = None
        self.ws_lock = asyncio.Lock()
        self.user_id = None
        self.token = None

    def update_auth_data(self) -> None:
        """
        Updates `user_id` and `token` from the client instance after authentication.

        If the WebSocket instance has an associated client, this method copies
        the `user_id` and `token` attributes from the client to the WebSocket
        instance.

        Returns:
            None
        """
        if self.client:
            self.user_id = self.client.user_id
            self.token = self.client.token

    async def create_connection(self, proxy: str | None = None) -> None:
        """
        Establishes a WebSocket connection if not already connected.

        This method sets up a persistent WebSocket connection to the server. It ensures
        that only one active connection exists, handles potential connection failures,
        and performs necessary post-connection setup (such as authentication and
        starting the listener for incoming messages).

        Example:
            client = WebsocketClient(uri="wss://example.com/socket")
            await client.create_connection()

        Raises:
            websockets.exceptions.ConnectionClosed: If the WebSocket connection is closed unexpectedly.
            websockets.exceptions.InvalidStatus: If the server responds with an invalid status code.
            Exception: For any other unforeseen errors during connection initialization.

        Notes:
            - This method is asynchronous and should be awaited.
            - If the connection is lost, `_handle_reconnect()` will attempt to restore it.

        Workflow:
            1. Checks if a connection is already active (`self.alive`).
            2. Attempts to establish a new WebSocket connection.
            3. Calls `_post_connect_setup()` to perform initialization.
            4. Starts a background task (`__listener()`) to listen for incoming messages.
            5. If the connection attempt fails, retries using `_handle_reconnect()`.
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

    async def _connect(self, proxy: str | None = None) -> None:
        """
        Creates a WebSocket connection to the specified server URI.

        This method initializes the low-level WebSocket connection using the
        configured `self.uri`, attaches required headers, and sets the connection
        status flag `self.alive` to `True` on success.

        Raises:
            websockets.exceptions.InvalidURI: If the URI format is incorrect.
            websockets.exceptions.InvalidHandshake: If the handshake fails.
            Exception: For any other errors during the connection attempt.

        Notes:
            - The following header is included in the connection request:
            - User-Agent: "okhttp/4.12.0" (to mimic a common HTTP client)
        """
        headers: dict[str, str] = {
            "User-Agent": "okhttp/4.12.0"
        }
        if not headers:
            raise AttributeError
        #if proxy:
        #    os.environ['wss_proxy'] = proxy
        self.ws = await connect(self.uri, user_agent_header = str(headers), proxy = proxy)
        self.alive = True

    async def _post_connect_setup(self) -> None:
        """
        Handles necessary setup after establishing a successful WebSocket connection.

        This method performs post-connection initialization tasks, including
        triggering the `__on_connect` hook and starting the background listener
        task to handle incoming messages.

        Notes:
            - This method should be called only after a successful connection.
            - It is asynchronous and should be awaited.

        Workflow:
            1. Calls `__on_connect()` to perform any logic needed immediately
            after a successful connection.
            2. Starts `__listener()` as a background task to listen for messages.
        """
        await self.__on_connect()
        self.listener_task = asyncio.create_task(self.__listener())

    async def _handle_reconnect(self) -> None:
        """
        Initiates a reconnection attempt after a failed WebSocket connection.

        Sets the connection status flag to False and starts a background task
        to handle reconnection logic.

        Notes:
            - This method does not await the reconnection task directly.
            - Reconnection logic should handle rate limiting and backoff.
        """
        self.alive = False
        logger.info("Starting reconnection process.")
        asyncio.create_task(self._reconnect())

    async def disconnect(self) -> None:
        """
        Gracefully closes the WebSocket connection.

        Ensures a clean shutdown of the WebSocket connection to prevent resource
        leaks and handle any unexpected errors that may occur during closure.
        If the connection is already closed, the method logs the event and exits silently.

        Example:
            client = WebsocketClient(uri="wss://example.com/socket")
            await client.create_connection()
            # Do some operations...
            await client.disconnect()

        Raises:
            websockets.exceptions.ConnectionClosed: If the connection was already closed.
            Exception: If an unexpected error occurs while closing the connection.

        Notes:
            - This method is asynchronous and should be awaited.
            - After calling this method, the client should not be used unless reconnected.
            - The method performs the following steps:
                1. Checks if the connection is active (`self.alive`).
                2. Sets `self.alive` to `False` to prevent further operations.
                3. Calls `_close_websocket()` to properly close the connection.
                4. Cancels the background listener task (`__listener()`).
                5. Logs the disconnection status.
            - Logging includes:
                - Attempting to close the connection.
                - Detecting if already closed.
                - Successful disconnection.
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
        """
        Closes the WebSocket connection with a normal closure code (1000).

        This method gracefully shuts down the current WebSocket connection, if one exists.
        It attempts to close the connection using the standard WebSocket closure code 1000
        (indicating a normal closure). It also handles cases where the connection may have
        already been closed or is not initialized.

        Example:
            await websocket_client._close_websocket()

        Raises:
            Exception: If an unexpected error occurs during closure.

        Notes:
            - This method is safe to call even if the connection is already closed.
            - If the connection object is not initialized (`self.ws is None`),
            it logs a warning and exits silently.

        Workflow:
            1. Checks if the WebSocket (`self.ws`) is set.
            2. Attempts to close the connection using `close(code=1000)`.
            3. Catches and logs `ConnectionClosed` if the connection is already closed.
            4. Catches and logs unexpected exceptions.
            5. Resets `self.ws` to `None` to mark the connection as inactive.
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

    async def _cancel_listener_task(self) -> None:
        """
        Cancels the background listener task if it is still running.

        This method checks whether the listener task responsible for handling
        incoming WebSocket messages is active. If it is, the task is cancelled
        to prevent further processing and to allow graceful shutdown of the client.

        Example:
            await websocket_client._cancel_listener_task()

        Notes:
            - This method is safe to call multiple times; it will only act if the
            task exists and is not already completed or cancelled.
            - It is typically used during client shutdown or reconnection.

        Workflow:
            1. Verifies that `self.listener_task` exists.
            2. Checks if the task is still pending or running.
            3. Cancels the task and logs the cancellation.
        """
        if self.listener_task and not self.listener_task.done():
            self.listener_task.cancel()
            logger.debug("Listener task cancelled.")

    async def send_server(self, data: dict,
                          remove_token_from_object: bool = False) -> None:
        """
        Sends a JSON-encoded payload to the WebSocket server.

        This method handles serialization, attaches authentication details
        (if available), and ensures the WebSocket is connected before sending.
        If the connection is lost, it attempts an automatic reconnection.
        In case of a known ban (e.g., BanError), the method exits silently.

        Args:
            data (dict): The data payload to send over the WebSocket.
            remove_token_from_object (bool): If True, omits authentication
                details ('token' and 'user_id') from the outgoing message.

        Example:
            await client.send_server({
                "PacketDataKeys.TYPE": "PacketDataKeys.UPLOAD_PHOTO",
                "PacketDataKeys.FILE": base64.encodebytes(file).decode()
            })

        Raises:
            json.JSONDecodeError: On serialization failure.
            AttributeError: If the WebSocket instance is unexpectedly missing.
            websockets.ConnectionClosed: If sending fails due to closed socket.

        Notes:
            - Attempts to be fault-tolerant: reconnects if disconnected,
            gracefully skips banned clients.
            - Skips sending if reconnection fails or connection remains unavailable.
            - Handles errors internally; the caller is not expected to manage exceptions.
            - If a BanError is raised during reconnection, the message is dropped silently.
            - This method is asynchronous and must be awaited to ensure correct operation.

        Workflow:
            1. Checks if the WebSocket connection is active (self.alive).
            2. If inactive, tries to reconnect. On failure or BanError, drops message.
            3. Attaches authentication data (if applicable and not suppressed).
            4. Serializes the payload to JSON.
            5. Sends the data via self.ws.send().
            6. On connection closure, triggers a reconnection in background.
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
            if self.token:
                data[PacketDataKeys.TOKEN] = self.token
            if self.user_id:
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
        Listen for a single incoming message from the WebSocket queue.

        This asynchronous method continuously monitors the internal message queue
        (`self.data_queue`) while the listener is alive (`self.alive`). It attempts
        to retrieve and decode a JSON message, with built-in handling for timeouts,
        decoding issues, and unexpected exceptions.

        Returns:
            dict | None: The parsed JSON object if a valid message is received and
            decoded successfully. Returns `None` if no valid message is retrieved
            before `self.alive` becomes `False`, or if all retries within a cycle fail.

        Raises:
            KeyboardInterrupt: Propagated if the user manually interrupts execution
            (e.g., via Ctrl+C).
            json.JSONDecodeError: Raised if an invalid JSON is encountered outside
            the inner try block (rare, but accounted for).
            Exception: Any other unexpected exceptions are logged but not re-raised.

        Notes:
            - Uses `asyncio.wait_for` with a 5-second timeout for each message.
            - If a message is received:
                - If the message is `None`, an error is logged.
                - Attempts to decode it from JSON:
                    - If decoding succeeds, returns the resulting dictionary.
                    - If decoding fails, logs the malformed message and continues.
            - If no message is received within 5 seconds, a debug message is logged
              and the loop continues waiting.
            - All exceptions except `KeyboardInterrupt` are caught and logged internally.
            - JSON decoding errors and unexpected values are logged with context.
            - Timeout events are logged at the debug level to reduce noise.
            - Unexpected exceptions are captured and logged without interrupting the loop.
            - This method is designed to run in a persistent listening loop within
              an asynchronous context and will return after handling a single message,
              or `None` if the loop ends without valid input.
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

        This coroutine listens for JSON messages from the WebSocket using the `listen()`
        method, and filters them based on the specified `mafia_type`. It handles timeouts,
        unexpected event types, and block conditions. Returns a valid matching message
        as a dictionary, or raises an exception if necessary.

        Args:
            mafia_type (str): The event type to wait for. Only messages with this type,
                "empty", or an error type (`PacketDataKeys.ERROR_OCCUR`) are considered valid.

        Returns:
            dict or None: A dictionary containing the valid message data, or `None` if
            listening is interrupted or no suitable data is received within the timeout.

        Raises:
            ValueError: If a `None` response is received from the listener.
            BanError: If the server signals the user has been blocked via a `USER_BLOCKED` event.
            asyncio.TimeoutError: If no data is received within 10 seconds.
            KeyboardInterrupt: If the user manually interrupts execution.
            Exception: For all other unexpected exceptions.

        Notes:
            - Listens for one message at a time using a 10-second timeout.
            - If the received message's `type` field matches one of the following, it is returned:
                - The expected `mafia_type`
                - "empty"
                - `PacketDataKeys.ERROR_OCCUR`
            - If a `USER_BLOCKED` event is received:
                - A `BanError` is raised.
                - The client is disconnected.
                - The process exits using `sys.exit()`.
            - Unexpected or unrelated events are logged and ignored.
            - If a `None` or malformed message is received, it is either skipped or raises an error.
            - This method is typically used in response to game events such as
              `PacketDataKeys.GAME_STARTED`, `PacketDataKeys.GAME_STATUS`, or
              `PacketDataKeys.GAME_FINISHED`, filtering out all others until a match is found.
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

        This method repeatedly calls `self.get_data(key)` until it returns a non-None value
        or the maximum number of retries is reached. If an exception is raised during a call,
        the method logs the error, waits for the specified delay, and retries. If no valid
        data is retrieved after all attempts, a ValueError is raised.

        Args:
            key (str): The event type or key used to request data from `get_data`.
            retries (int, optional): Maximum number of retry attempts. Defaults to 2.
            delay (int, optional): Delay in seconds between retry attempts. Defaults to 2.

        Returns:
            dict: The first non-None response returned by `get_data`.

        Raises:
            ValueError: If all retry attempts fail or only None values are returned.
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

    async def _reconnect(self) -> None:
        """
        Performs a controlled reconnection process for the WebSocket client.

        This method is used when the connection to the WebSocket server has been
        lost or needs to be re-established. It performs up to 5 reconnection
        attempts, with exponential backoff delays between each attempt to avoid
        aggressive reconnect loops. Before each attempt, the current connection
        (if any) is safely closed using `_attempt_disconnect()`.

        If a reconnection attempt is successful (i.e., `_try_create_connection()`
        returns True), the method exits early. If all attempts fail and
        `_should_stop_reconnect()` returns True, the method stops retrying
        gracefully without raising an exception.

        This mechanism is intended to support graceful degradation and recovery
        in unreliable network environments, especially where WebSocket stability
        is not guaranteed.

        Args:
            None

        Returns:
            None

        Behavior:
            - Logs the reconnection process with attempt counts.
            - Attempts up to 5 reconnection tries using exponential backoff.
            - Backoff time doubles with each retry, capped at 30 seconds:
            1s, 2s, 4s, 8s, 16s (but you use min(2 ** attempt, 30)).
            - Each attempt:
                1. Calls `_attempt_disconnect()` to safely close existing state.
                2. Waits for backoff delay.
                3. Calls `_try_create_connection()` to open a new WebSocket.
            - If a connection is re-established, logs success and returns.
            - If all attempts fail and `_should_stop_reconnect()` returns True,
            logs a critical message and exits quietly.

        Example:
            await self._reconnect()

        Notes:
            - This method should be called internally after a disconnect or
            connection failure.
            - No exception is raised if reconnection fails; the method assumes
            that failure handling is done elsewhere.
            - Designed to be safe to call even when the connection is already closed.
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
            await asyncio.wait_for(self.create_connection(), timeout = 10)
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

        Behavior
            - Sends a handshake message to confirm connection.
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

    async def __listener(self) -> None:
        """
        Listens for incoming WebSocket messages and adds them to the queue.

        Behavior
            - Continuously receives messages while the connection is active.
            - Handles various disconnection scenarios and attempts
            reconnection if necessary.
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
                await self.disconnect()
                break
