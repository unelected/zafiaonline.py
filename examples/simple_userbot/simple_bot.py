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

import asyncio
import logging
import sys
import os

from typing import NoReturn
from dotenv import load_dotenv
from aioconsole import ainput

from zafiaonline.api_client.api_decorators import ApiDecorators
from zafiaonline.utils.exceptions import ListenExampleErrorException
from zafiaonline.main import Client


class SimpleBot:
    def __init__(self) -> None:
        self.task1 = None
        self.task2 = None
        self.task3 = None
        self.user_bot_config: dict | None = None
        self.content = None
        self.user_name = None

    async def main(self) -> None:
        load_dotenv("account_data.env")
        email: str = os.getenv("EMAIL") or "email"
        password: str = os.getenv("PASSWORD") or "password"
        await mafia.auth.sign_in(email, password)
        await mafia.global_chat.join_global_chat()  # join in global chat
        await self.run_tasks()


    @staticmethod
    async def rejoin() -> None:
        await mafia.global_chat.leave_from_global_chat()
        await mafia.global_chat.join_global_chat()

    async def reenter_timer(self) -> None:
        try:
            await asyncio.sleep(300)
            await self.rejoin()
        except asyncio.CancelledError:
            pass

    async def chat_listener(self) -> NoReturn:
        while True:
            try:
                result: dict = await mafia.auth.listen()
            except ListenExampleErrorException as e:
                await mafia.auth.disconnect()
                raise SystemExit("listen error", e)
            except Exception as e:
                logging.error(f"unexcepted exception {e}")
                raise
            logging.info(result)
            self.print_message(result)
        # await chat.send_message_global(content)
        
    @ApiDecorators.extract_message
    def print_message(self, content: str) -> None:
        self.content = content
        print(f"{self.user_name}: {self.content}")

    async def chat_sender(self) -> None:
        """Main loop for reading user input and dispatching messages/commands."""
        while True:
            my_message: str = await ainput()
            if not await self._validate_message(my_message):
                continue

            if await self._handle_command(my_message):
                continue

            if await self._handle_phrase(my_message):
                continue

            await self._send_default(my_message)

    async def _validate_message(self, message: str | None) -> bool:
        """Checks whether the message is valid for sending."""
        if message is None:
            logging.info("empty message not send")
            return False
        if not self.user_bot_config:
            raise AttributeError("Missing user_bot_config")
        if not self.task1 or not self.task2:
            raise AttributeError("Tasks not initialized")
        return True


    async def _handle_command(self, message: str) -> bool:
        """Handles special commands like cancel or rejoin. Returns True if handled."""
        if self.user_bot_config:
            if message not in self.user_bot_config["commands"]:
                return False
            
            command: dict = self.user_bot_config["commands"][message]

            if command.get("cancel_tasks"):
                await self._cancel_tasks()
                await mafia.global_chat.leave_from_global_chat()
                await mafia.auth.disconnect()
                print(command["message"])
                sys.exit()

            if command.get("rejoin"):
                await self.rejoin()
                return True

        return False

    async def _cancel_tasks(self) -> None:
        """Cancels running tasks gracefully."""
        if self.task1 and self.task2:
            self.task1.cancel()
            self.task2.cancel()
            try:
                await asyncio.gather(self.task1, self.task2)
            except asyncio.CancelledError:
                pass


    async def _handle_phrase(self, message: str) -> bool:
        """Checks if message is a phrase trigger, sends responses. Returns True if handled."""
        if self.user_bot_config:
            if message not in self.user_bot_config["phrases"]:
                return False

            responses: list[dict] = self.user_bot_config["phrases"][message]
            for response in responses:
                text = response["text"].format(input=message)
                await mafia.global_chat.send_message_global(text)

                delay = response.get("delay", 0)
                if delay > 0:
                    await asyncio.sleep(delay)
            return True
        return False


    async def _send_default(self, message: str) -> None:
        """Sends a default message when no command or phrase matched."""
        await mafia.global_chat.send_message_global(message)

    async def run_tasks(self) -> None:
        self.task1 = asyncio.create_task(self.reenter_timer())  # timer
        self.task2 = asyncio.create_task(self.chat_listener())  # listener
        self.task3 = asyncio.create_task(self.chat_sender())  # chat sender
        try:
            await asyncio.gather(self.task1, self.task2, self.task3)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    logging.basicConfig(
    filename='my_log.log',        # имя файла для логов
    filemode='a',                 # 'w' — перезаписывать, 'a' — добавлять
    level=logging.INFO,           # уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
    mafia: Client = Client()
    bot: SimpleBot = SimpleBot()
    try:
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        pass
