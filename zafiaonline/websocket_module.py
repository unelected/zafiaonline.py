import json
import logging
import asyncio

import websockets
from websockets import ConnectionClosedOK, connect, ConnectionClosed

from zafiaonline.structures import PacketDataKeys

class Websocket:
    def __init__(self, client) -> None:
        self.client = client
        self.data_queue = asyncio.Queue()
        self.alive = True
        self.ws = None
        self.uri = f"ws://{self.client.address}:{self.client.port}"
        self.listener_task = asyncio.create_task(self.__listener())
        self.ws_lock = asyncio.Lock()

    async def create_connection(self) -> None:
        try:

            self.ws = await connect(self.uri)
            await self.__on_connect()
            self.alive = True
            if self.listener_task and not self.listener_task.done():
                self.listener_task.cancel()
            asyncio.create_task(self.__listener())

        except (
        ConnectionClosed, websockets.exceptions.InvalidStatus) as e:
            logging.error(f"Connection failed: {e}. Retrying...")
            await self._reconnect()
        except Exception as e:
            logging.error(f"Unexpected error in create_connection: {e}")
            await self._reconnect()
            raise

    async def disconnect(self) -> None:
        if self.ws and not self.ws.close:
            self.alive = False
            try:

                await self.ws.close(code=1000)
                logging.debug("Websocket connection closed gracefully.")
                if self.listener_task:
                    self.listener_task.cancel()

            except ConnectionClosed as e:
                logging.debug(f"Connection already closed: {e}")
            except Exception as e:
                logging.error(f"Error while closing websocket connection: {e}")
                raise

        else:
            logging.debug("Already closed")
        logging.debug("Disconnected")

    async def send_server(self, data: dict,
                          remove_token_from_object: bool = False) -> None:
        if not self.ws:
            logging.error(
                "Websocket is not connected. Attempting to reconnect...")
            await self._reconnect()
            if not self.ws:
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
                "Websocket closed while sending data. Reconnecting...")
            await self._reconnect()

    async def listen(self) -> dict:
        while self.alive:
            try:
                response = await asyncio.wait_for(self.data_queue.get(),
                                                  timeout=5)
                if response is not None:
                    return json.loads(response)
                raise ValueError("Received None response from queue")
            except asyncio.CancelledError:
                logging.debug("Listen task was cancelled.")
                raise TimeoutError
            except asyncio.TimeoutError:
                raise
            except json.JSONDecodeError:
                logging.error("Invalid JSON received.")
                raise
            except KeyboardInterrupt:
                pass
            except Exception as e:
                logging.error(f"Unexpected error in listen: {e}")
                raise

    async def get_data(self, mafia_type: str) -> dict:
        try:
            data = await self.listen()

        except asyncio.CancelledError:
            logging.debug("Get data task was cancelled")
            raise

        while self.alive:
            try:
                if data is None:
                    logging.debug("Data is none. Cannot proceed")
                    raise

                event = data.get(PacketDataKeys.TYPE)
                if event in [mafia_type, "empty", PacketDataKeys.ERROR_OCCUR]:
                    return data

            except asyncio.CancelledError:
                logging.debug("Get data task was cancelled")
                raise
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logging.error(f"Unexpected error in get data: {e}")
                raise

            data = await self.listen()

    async def _reconnect(self) -> None:
        logging.warning("Attempting to reconnect...")
        max_attempts = 5
        for attempt in range(max_attempts):
            if not self.alive:
                logging.info(
                    "Websocket is no longer active. Stopping reconnection.")
                return
            try:
                async with self.ws_lock:
                    if self.ws:
                        await self.disconnect()
                await asyncio.sleep(min(2 ** attempt, 30))
                if not self.alive:
                    logging.info(
                        "Websocket was marked as inactive. Stopping "
                        "reconnection.")
                    return
                try:
                    await asyncio.wait_for(self.create_connection(),
                                           timeout=10)
                except asyncio.TimeoutError:
                    logging.error("Timeout while trying to reconnect")
                logging.info("Reconnection successful.")
                return

            except asyncio.CancelledError:
                logging.error("Reconnection task was cancelled.")
                break
            except Exception as e:
                logging.error(
                    f"Reconnection attempt {attempt + 1} failed: {e}")
                raise
        logging.critical("Max reconnection attempts reached. Giving up.")

    async def __on_connect(self):
        await self.ws.send("Hello, World!")

    async def __listener(self) -> None:
        while self.ws and self.alive:
            try:

                if self.alive:
                    message = await self.ws.recv()
                    await self.data_queue.put(message)
                else:
                    raise ConnectionClosed


            except ConnectionClosedOK:
                logging.debug("Connection closed normally (1000)")
                break
            except websockets.exceptions.ConnectionClosedError as e:
                logging.debug(f"Connection closed: {e}")
                break
            except asyncio.CancelledError:
                logging.debug("Listener task was cancelled.")
                raise
            except websockets.ConnectionClosed:
                logging.debug("Websocket connection closed in "
                                "listener data. reconnecting...")
                await self._reconnect()
                raise
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logging.error(f"Unexpected error in listener: {e}")
                await self.disconnect()
                break