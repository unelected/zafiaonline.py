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
import os
import logging

from dotenv import load_dotenv
from zafiaonline import Client
from zafiaonline.api_client.api_decorators import ApiDecorators


class Main:
    @staticmethod
    async def main():
        data_handler = DataHandle()
        account_data = AccountData()
        message_handler = MessagesHandle()
        email, password = account_data.init_account_data()
        await client.auth.sign_in(email, password)
        await client.global_chat.join_global_chat()
        while True:
            result = await client.auth.listen()
            if not result:
                raise AttributeError
            content = data_handler.get_data(result)
            await message_handler.message_handle(content)


class AccountData:
    load_dotenv("data.env")
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")

    @classmethod
    def init_account_data(cls):
        return cls.EMAIL, cls.PASSWORD


class DataHandle:
    USER_NAME = None  # Переменная класса

    def __init__(self):
        self.user_name = None

    @ApiDecorators.extract_message
    def get_data(self, content):
        DataHandle.USER_NAME = self.user_name
        return content


class MessagesHandle:
    load_dotenv("data.env")
    DELAY: float = float(os.getenv("DELAY") or .4)
    TROLL_MESSAGE: str = os.getenv("TROLL_MESSAGE") or ""

    @staticmethod
    async def message_handle(content):
        prepare_data = PrepareData()
        message_handler = MessagesHandle()
        if prepare_data.cooldown_is_done(content):
            await prepare_data.farm_tea()
            await message_handler.trolling()

    @staticmethod
    async def trolling():
        message_handler = MessagesHandle()
        for _ in range(0, 10):
            await client.global_chat.leave_from_global_chat()
            await asyncio.sleep(message_handler.DELAY)
            await client.global_chat.join_global_chat()
            await asyncio.sleep(message_handler.DELAY)
        await client.global_chat.send_message_global(
            message_handler.TROLL_MESSAGE
        )


class PrepareData:
    load_dotenv("data.env")
    TEA_IS_READY_TO_BE_TAKEN = os.getenv(
        "TEA_IS_READY_TO_BE_TAKEN",
        "Новый чай готов для получения!"
    )
    BOT_NICKNAMES = os.getenv(
        "BOT_NICKNAMES",
        ""
    ).split(",")

    @staticmethod
    async def farm_tea():
        await client.global_chat.send_message_global("/фарм чая")

    @staticmethod
    def cooldown_is_done(content):
        prepare_data = PrepareData()
        data_handle = DataHandle()
        return (
            content == prepare_data.TEA_IS_READY_TO_BE_TAKEN
            and data_handle.USER_NAME
            in prepare_data.BOT_NICKNAMES
        )


if __name__ == "__main__":
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s - %(levelname)s - %(message)s",
        datefmt = "%H:%M:%S"
    )
    client = Client()
    main = Main()
    try:
        asyncio.run(main.main())
    except KeyboardInterrupt:
        pass
