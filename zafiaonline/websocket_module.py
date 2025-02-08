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

    async def create_connection(self) -> None:
        try:

            self.ws = await connect(self.uri)
            await self.__on_connect()
            self.alive = True
            asyncio.create_task(self.__listener())

        except (
        ConnectionClosed, websockets.exceptions.InvalidStatus) as e:
            logging.error(f"Connection failed: {e}. Retrying...")
            await self._reconnect()
        except Exception as e:
            logging.error(f"Unexpected error in create_connection: {e}")
            await self._reconnect()

    async def disconnect(self) -> None:
        if self.ws and self.alive:
            self.alive = False
            try:

                await self.ws.close(code=1000)
                logging.debug("websocket connection closed gracefully.")

            except ConnectionClosed as e:
                logging.debug(f"connection already closed: {e}")
            except Exception as e:
                logging.error(f"error while closing websocket connection: {e}")

        else:
            logging.debug("already closed")
        logging.debug("disconnected")

    async def send_server(self, data: dict,
                          remove_token_from_object: bool = False) -> None:
        if not self.ws:
            logging.warning(
                "WebSocket is not connected. Attempting to reconnect...")
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
            logging.warning(
                "WebSocket closed while sending data. Reconnecting...")
            await self._reconnect()

    async def listen(self) -> dict:
        while self.alive:
            try:
                response = await asyncio.wait_for(self.data_queue.get(),
                                                  timeout=5)
                if response is not None:
                    return json.loads(response)
                raise
            except asyncio.CancelledError:
                logging.debug("listen task was cancelled.")
                raise TimeoutError
            except asyncio.TimeoutError:
                raise
            except json.JSONDecodeError:
                logging.error("invalid JSON received.")
                raise
            except KeyboardInterrupt:
                pass
            except Exception as e:
                logging.error(f"unexpected error in listen: {e}")
                raise

    async def get_data(self, mafia_type: str) -> dict:
        try:
            data = await self.listen()

        except asyncio.CancelledError:
            logging.debug("get data task was cancelled")
            raise

        while self.alive:
            try:
                if data is None:
                    logging.debug("data is none. cannot proceed")
                    continue

                event = data.get(PacketDataKeys.TYPE)
                if event in [mafia_type, "empty", PacketDataKeys.ERROR_OCCUR]:
                    return data

            except asyncio.CancelledError:
                logging.debug("get data task was cancelled")
                raise
            except KeyboardInterrupt:
                pass
            except Exception as e:
                logging.error(f"unexpected error in get data: {e}")
                continue

            data = await self.listen()

    async def _reconnect(self) -> None:
        logging.warning("Attempting to reconnect...")
        max_attempts = 5
        for attempt in range(max_attempts):
            if not self.alive:
                logging.info(
                    "WebSocket is no longer active. Stopping reconnection.")
                return
            try:
                await self.disconnect()
                await asyncio.sleep(
                    min(2 ** attempt, 30))  # Экспоненциальный бэкофф
                await self.create_connection()
                logging.info("Reconnection successful.")
                return

            except asyncio.CancelledError:
                logging.warning("Reconnection task was cancelled.")
                return
            except Exception as e:
                logging.error(
                    f"Reconnection attempt {attempt + 1} failed: {e}")
        logging.critical("Max reconnection attempts reached. Giving up.")

    async def __on_connect(self):
        await self.ws.send("Hello, World!")

    async def __listener(self) -> None:
        while self.ws and self.alive:
            try:

                if self.alive:
                    message = await self.ws.recv()
                    logging.debug(f"received message: {message}")
                    await self.data_queue.put(message)
                else:
                    raise


            except ConnectionClosedOK:
                logging.debug("connection closed normally (1000)")
                break
            except websockets.exceptions.ConnectionClosedError as e:
                logging.debug(f"connection closed: {e}")
                break
            except asyncio.CancelledError:
                logging.debug("listener task was cancelled.")
                raise
            except websockets.ConnectionClosed:
                logging.debug("websocket connection closed in "
                                "listener "
                                "data. "
                                "reconnecting...")
                await self._reconnect()
                raise
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logging.error(f"unexpected error in listener: {e}")
                await self.disconnect()
                break
