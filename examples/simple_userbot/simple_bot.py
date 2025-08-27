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

from dotenv import load_dotenv
from aioconsole import ainput

from zafiaonline.api_client.api_decorators import ApiDecorators
from zafiaonline.utils.exceptions import ListenExampleErrorException
from zafiaonline.main import Client

class SimpleBot:
    def __init__(self):
        self.task1 = None
        self.task2 = None
        self.task3 = None
        self.user_bot_config: dict | None = None
        self.content = None
        self.user_name = None

    async def main(self):
        load_dotenv("account_data.env")
        email:str = os.getenv("EMAIL") or "email"
        password:str = os.getenv("PASSWORD") or "password"
        await mafia.auth.sign_in(email, password)
        await mafia.global_chat.join_global_chat()  # join in global chat
        await self.run_tasks()


    @staticmethod
    async def rejoin():
        await mafia.global_chat.leave_from_global_chat()
        await mafia.global_chat.join_global_chat()

    async def reenter_timer(self):
        try:
            await asyncio.sleep(300)
            await self.rejoin()
        except asyncio.CancelledError:
            pass

    async def chat_listener(self):
        while True:
            try:
                result = await mafia.auth.listen()
            except ListenExampleErrorException as e:
                await mafia.auth.disconnect()
                raise SystemExit("listen error", e)
            except Exception as e:
                logging.error(f"unexcepted exception {e}")
                raise
            if not result:
                logging.error("received empty result from listen.")
                continue
            
            if result:
                logging.info(result)
                self.print_message(result)
        # await chat.send_message_global(content)
        
    @ApiDecorators.extract_message
    def print_message(self, content):
        self.content = content
        print(f"{self.user_name}: {self.content}")

    async def chat_sender(self):
        while True:
            my_message = await ainput()
            if my_message is None:
                logging.info("empty message not send")
                continue
            if not self.user_bot_config:
                raise AttributeError
            if not self.task1 or not self.task2:
                raise AttributeError
            if my_message in self.user_bot_config["commands"]:
                command = self.user_bot_config["commands"][my_message]
                if command.get("cancel_tasks"):
                    self.task1.cancel()
                    self.task2.cancel()
                    try:
                        await asyncio.gather(self.task1, self.task2)
                    except asyncio.CancelledError:
                        pass
                    await mafia.global_chat.leave_from_global_chat()
                    await mafia.auth.disconnect()
                    print(command["message"])
                    sys.exit()
                elif command.get("rejoin"):
                    await self.rejoin()
                    continue

            # Обработка фраз
            if my_message in self.user_bot_config["phrases"]:
                responses = self.user_bot_config["phrases"][my_message]
                if responses:
                    for response in responses:
                        # Замена {input} на введенное сообщение
                        text = response["text"].format(input=my_message)
                        await mafia.global_chat.send_message_global(text)

                        # Задержка перед следующим сообщением
                        delay = response.get("delay", 0)
                        if delay > 0:
                            await asyncio.sleep(delay)
                    continue

            # По умолчанию отправлять сообщение
            await mafia.global_chat.send_message_global(my_message)

    async def run_tasks(self):
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
        level=logging.INFO,       # уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
    mafia = Client()
    bot = SimpleBot()
    try:
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        pass
