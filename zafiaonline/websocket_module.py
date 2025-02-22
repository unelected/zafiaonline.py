import json
import logging
import asyncio
import websockets

from websockets import ConnectionClosedOK, connect, ConnectionClosed
from typing import Optional

from zafiaonline.structures import PacketDataKeys

class Websocket:
    def __init__(self, client) -> None:
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
        self.uri = f"ws://{self.client.address}:{self.client.port}"
        self.listener_task: Optional[asyncio.Task] = None
        self.ws_lock = asyncio.Lock()

    async def create_connection(self) -> None:
        """
        Establishes a WebSocket connection if not already connected.

        - Creates a new WebSocket connection to the server.
        - Calls `__on_connect()` to handle post-connection setup.
        - Starts the listener task for incoming messages.
        - If the connection fails, attempts to reconnect.

        **Raises**
            - **ConnectionClosed, InvalidStatus** - If the connection fails,
            it retries.
            - **Exception** - Logs unexpected errors and attempts reconnection.
        """
        try:
            if not self.alive:
                self.ws = await connect(self.uri)
                await self.__on_connect()
                self.alive = True
                self.listener_task = asyncio.create_task(self.__listener())
            else:
                logging.info("Connection already established.")

        except (ConnectionClosed, websockets.exceptions.InvalidStatus) as e:
            logging.error(f"Connection failed: {e}. Retrying...")
            await self._reconnect()
            raise
        except Exception as e:
            logging.error(f"Unexpected error in create_connection: {e}")
            await self._reconnect()
            raise

    async def disconnect(self) -> None:
        """
        Closes the WebSocket connection gracefully.

        **Logs:**
            - Attempts to close the connection.
            - Confirms successful closure.
            - Handles possible exceptions.

        **Raises:**
            - ConnectionClosed: If the connection is already closed.
            - Exception: If an unexpected error occurs.
        """
        logging.debug(
            f"Attempting to close WebSocket. self.alive={self.alive}")

        if not self.alive:
            logging.debug("WebSocket already closed.")
            return

        self.alive = False
        await self._close_websocket()
        await self._cancel_listener_task()
        logging.debug("Disconnected.")

    async def _close_websocket(self) -> None:
        """Closes the WebSocket connection with a normal status code (1000)."""
        try:
            await self.ws.close(code=1000)
            logging.debug("WebSocket connection closed gracefully.")
        except ConnectionClosed as e:
            logging.debug(f"Connection already closed: {e}")
            raise
        except Exception as e:
            logging.error(f"Error while closing WebSocket connection: {e}")
            raise

    async def _cancel_listener_task(self) -> None:
        """Cancels the listener task if it is still running."""
        if self.listener_task and not self.listener_task.done():
            self.listener_task.cancel()
            logging.debug("Listener task cancelled.")

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
        if not self.alive:
            logging.error(
                "WebSocket is not connected. Attempting to reconnect...")
            await self._reconnect()
            if not self.alive:
                logging.error("Reconnection failed. Dropping message.")
                return

        if not remove_token_from_object:
            data[PacketDataKeys.TOKEN] = self.client.token
            data.setdefault(PacketDataKeys.USER_OBJECT_ID, self.client.id)

        try:
            json_data = json.dumps(data)
            await self.ws.send(json_data)

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON data: {e}")

        except websockets.ConnectionClosed:
            logging.error(
                "WebSocket closed while sending data. Reconnecting...")
            await self._reconnect()

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
                                                  timeout=5)

                if response is None:
                    logging.error("Received None response from queue")
                    continue

                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    logging.error(f"Invalid JSON received: {response}")
                    continue

            except asyncio.TimeoutError:
                logging.debug("Listen timeout, no data received.")
                continue

            except json.JSONDecodeError:
                logging.error("Invalid JSON format in received data.")
                raise

            except KeyboardInterrupt:
                raise

            except Exception as e:
                logging.error(f"Unexpected error in listen: {e}")

    async def get_data(self, mafia_type: str) -> dict:
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
        try:
            data = await self.listen()
        except KeyboardInterrupt:
            raise

        while self.alive:
            try:
                if data is None:
                    logging.debug("Data is None. Cannot proceed.")
                    raise ValueError("Received None data.")

                event = data.get(PacketDataKeys.TYPE)
                if event in [mafia_type, "empty", PacketDataKeys.ERROR_OCCUR]:
                    return data

            except KeyboardInterrupt:
                raise
            except Exception as e:
                logging.error(f"Unexpected error in get_data: {e}")
                raise

            data = await self.listen()

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
        logging.warning("Attempting to reconnect...")

        max_attempts = 5
        for attempt in range(max_attempts):
            if await self._should_stop_reconnect():
                return

            await self._attempt_disconnect()

            await asyncio.sleep(min(2 ** attempt, 30))  # Exponential backoff

            if await self._should_stop_reconnect():
                return

            if await self._try_create_connection():
                logging.info("Reconnection successful.")
                return

            logging.error(f"Reconnection attempt {attempt + 1} failed.")

        logging.critical("Max reconnection attempts reached. Giving up.")

    async def _should_stop_reconnect(self) -> bool:
        """Checks if reconnection should stop due to an inactive WebSocket."""
        if not self.alive:
            logging.info("WebSocket is inactive. Stopping reconnection.")
            return True
        return False

    async def _attempt_disconnect(self) -> None:
        """Safely attempts to disconnect the WebSocket before reconnecting."""
        try:
            async with self.ws_lock:
                if self.alive:
                    await self.disconnect()
        except Exception as e:
            logging.error(f"Error during disconnect before reconnect: {e}")

    async def _try_create_connection(self) -> bool:
        """Attempts to create a new WebSocket connection with a timeout."""
        try:
            await asyncio.wait_for(self.create_connection(), timeout=10)
            return True
        except asyncio.TimeoutError:
            logging.error("Timeout while trying to reconnect.")
            return False
        except Exception as e:
            logging.error(f"Unexpected error in _try_create_connection: {e}")
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
            logging.debug("Sent initial handshake message.")
        except websockets.ConnectionClosed as e:
            logging.error(f"WebSocket closed before sending handshake: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in __on_connect: {e}")

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
                logging.debug("Connection closed normally (1000).")
                break
            except websockets.exceptions.ConnectionClosedError as e:
                logging.warning(f"Connection closed unexpectedly: {e}")
                break
            except asyncio.CancelledError:
                logging.debug("Listener task was cancelled.")
                break
            except websockets.ConnectionClosed:
                logging.warning(
                    "WebSocket connection lost. Attempting to reconnect...")
                await self._reconnect()
                break
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logging.error(f"Unexpected error in __listener: {e}")
                await self.disconnect()
                break
