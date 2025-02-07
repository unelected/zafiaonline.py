import json
import logging
import asyncio

import websockets
from websocket import WebSocketTimeoutException
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

        except ConnectionError:
            logging.error("connection error")
            return
        except TimeoutError:
            logging.error("timeout")
            await self._reconnect()
            return
        except WebSocketTimeoutException:
            logging.error("websocket timeout")
            await self._reconnect()
            return
        except Exception as e:
            logging.error(f"create connection failed {e}")
            return

        asyncio.create_task(self.__listener())

    async def disconnect(self) -> None:
        if self.ws and self.alive:
            self.alive = False
            try:

                await self.ws.close(code=1000)
                logging.debug("websocket connection closed gracefully.")

            except ConnectionClosed as e:
                logging.debug(f"connection already closed: {e}")
                raise
            except Exception as e:
                logging.error(f"error while closing websocket connection: {e}")
                raise

        else:
            logging.debug("already closed")
        logging.debug("disconnected")

    async def send_server(self, data: dict, remove_token_from_object:
    bool = False) -> None:

        if not self.ws:
            logging.debug("websocket is not connected.")
            await self._reconnect()

        if not remove_token_from_object:
            data[PacketDataKeys.TOKEN] = self.client.token
            data[PacketDataKeys.USER_OBJECT_ID] = \
            data.get(PacketDataKeys.USER_OBJECT_ID, self.client.id)

        try:

            json_data = json.dumps(data) + "\n"
            await self.ws.send(json_data)

        except (TypeError, ValueError) as e:
            logging.error(f"error during JSON serialization: {e}")
            return
        except asyncio.CancelledError:
            logging.debug("send server task was cancelled.")
            raise
        except KeyboardInterrupt:
            pass
        except websockets.ConnectionClosed:
            logging.debug("websocket connection lost while sending data. "
                            "reconnecting...")
            await self._reconnect()
            raise
        except Exception as e:
            logging.error(f"unexpected error in json data send server: {e}")
            return

    async def listen(self) -> dict:
        while self.alive:
            try:

                response = await asyncio.wait_for(self.data_queue.get(),
                                                  timeout=5)
                if response is not None:
                    return json.loads(response)
                continue

            except asyncio.CancelledError:
                logging.debug("listen task was cancelled.")
                raise TimeoutError
            except asyncio.TimeoutError:
                continue
            except json.JSONDecodeError:
                logging.error("invalid JSON received.")
                continue
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

    async def _reconnect(self):
        logging.debug("reconnect")

        for attempt in range(3):
            try:

                await self.disconnect()
                await asyncio.sleep(1)
                await self.create_connection()
                break

            except asyncio.CancelledError:
                logging.debug("reconnection task was cancelled.")
                raise
            except KeyboardInterrupt:
                pass
            except Exception as e:
                logging.error(f"unexpected error in reconnect: {e}")
                logging.debug(f"attempt: {attempt+ 1 }")
                await asyncio.sleep(2 ** attempt)

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
                    continue


            except ConnectionClosedOK:
                logging.debug("connection closed normally (1000)")
                continue
            except websockets.exceptions.ConnectionClosedError as e:
                logging.debug(f"connection closed: {e}")
                continue
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
                pass
            except Exception as e:
                logging.error(f"unexpected error in listener: {e}")
                await self.disconnect()
                raise