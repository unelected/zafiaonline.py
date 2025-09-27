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
import random

from aioconsole import ainput
from typing import NoReturn

from zafiaonline import Client
import zafiaonline
from zafiaonline.structures.packet_data_keys import PacketDataKeys
from zafiaonline.structures.enums import MessageType, Sex

from data import *

class RoomBot:
    def __init__(self) -> None:
        self.bot_username: str = ""
        self.room_id: str = ""
        self.sex: Sex = Sex.MEN
        self.user_name: str = ""
        self.user_id: str = ""
        self.players: list[str] = []
        self.players_nickname: list[str] = []
        self.past_players: list[str] = []
        self.muted_players: list[str] = []

    async def main(self) -> None:
        await self.prepare_bot()
        asyncio.create_task(self.chat_sender())
        await self.process_messages()
        return None

    async def prepare_bot(self) -> None:
        await client.auth.sign_in(BotData.nickname, BotData.password)
        self.bot_username = str(client.auth.user.username)
        await self.prepare_mutes()
        await self.create_room_and_join()
        return None

    async def prepare_mutes(self) -> None:
        muted_list: list = MutedPlayersData.muted_list
        for muted in muted_list:
            self.muted_players.append(muted)
        return None

    async def process_messages(self) -> None:
        while True:
            try:
                result: dict = await client.auth.listen()
            except Exception as e:
                logging.debug(f"ошибка в получении сообщения {e}")
                break
            content: str = await self.get_data_from_results(result)
            nickname: str = self.user_name
            if content and nickname not in self.muted_players:
                logging.info(f"{nickname}: {content}")
        return None

    async def get_data_from_results(self, result: dict) -> str:
        content: str | None = await self.get_messages(result)
        if isinstance(content, str):
            if result[PacketDataKeys.TYPE] == PacketDataKeys.ADD_PLAYER:
                await self.join_handle(result)
            if result[PacketDataKeys.TYPE] == PacketDataKeys.REMOVE_PLAYER:
                await self.exit_handle(result)
            return content
        raise TypeError("Invalid content type")

    async def join_handle(self, result: dict) -> None:
        user_id, username = await self.prepare_join_player_data(result)
        self.players.append(user_id)
        self.players_nickname.append(username)
        if len(self.players) >= (
            RoomData.min_players - RoomData.quantity_players_for_leave
        ):
            logging.info("слишком много игроков, пересоздаем")
            await self.recreate_room(True)
        logging.info(f"{username} вошёл")
        return None

    @staticmethod
    async def prepare_join_player_data(result: dict) -> tuple[str, str]:
        player: dict = result[PacketDataKeys.PLAYER]
        user: dict = player[PacketDataKeys.USER]
        user_id: str = user[PacketDataKeys.OBJECT_ID]
        username: str = user[PacketDataKeys.USERNAME]
        return user_id, username

    async def recreate_room(self, is_fast_rejoin: bool = True) -> None:
        await client.room.remove_player(self.room_id)
        if is_fast_rejoin is False:
            await asyncio.sleep(10)
        await self.create_room_and_join()
        asyncio.create_task(self.clear_past_players())
        return None

    async def clear_past_players(self) -> None:
        await asyncio.sleep(30)
        self.past_players.clear()
        self.players.clear()
        return None

    async def create_room_and_join(self) -> None:
        selected_roles: list[Roles | int |None] = RoomData.selected_roles
        room: zafiaonline.structures.ModelRoom | None = await client.room.create_room(
            selected_roles=selected_roles,
            title=RoomData.title,
            max_players=RoomData.max_players,
            min_players=RoomData.min_players,
            password=RoomData.password,
            min_level=RoomData.min_level,
            vip_enabled=RoomData.vip_enabled
        )

        if room:
            self.room_id: str = str(room.room_id)
            await client.room.create_player(self.room_id)
        return None

    async def exit_handle(self, result: dict) -> None:
        user_id: str = result[PacketDataKeys.USER_OBJECT_ID]
        if user_id in self.players:
            self.players.remove(user_id)
        return None

    async def chat_sender(self) -> NoReturn:
        while True:
            my_message: str = await ainput()
            if await self.commands_handle(my_message):
                continue
            await client.room.send_message_room(
                my_message,
                self.room_id,
                message_style=MessageStyleData.style
            )

    async def commands_handle(self, my_message: str) -> bool:
        if my_message == "/игроки":
            print(self.players_nickname)
            return True
        elif my_message.startswith("/мут"):
            await self.mute_handle(my_message)
            return True
        elif my_message.startswith("/унмут"):
            await self.unmute_handle(my_message)
            return True
        return False

    async def mute_handle(self, my_message: str) -> None:
        parts: list[str] = my_message.split(maxsplit=1)
        if len(parts) > 1:
            nickname: str = parts[1]
            self.muted_players.append(nickname)
            logging.info(f"игрок {nickname} в муте")
        return None

    async def unmute_handle(self, my_message: str):
        parts: list[str] = my_message.split(maxsplit=1)
        if len(parts) > 1:
            nickname: str = parts[1]
            self.muted_players.remove(nickname)
            logging.info(f"игрок {nickname} больше не в муте")

    async def delayed_send(
        self,
        response: str,
        delay: int,
        nickname: str | None = None
    ) -> None:
        await asyncio.sleep(delay)
        if self.check_player(nickname):
            await client.room.send_message_room(
                response,
                self.room_id,
                message_style=MessageStyleData.style
            )
        return None

    async def get_messages(self, result: dict) -> str | None:
        if result[PacketDataKeys.TYPE] == PacketDataKeys.MESSAGE:
            message, message_type = await self.prepare_message_data(result)

            if message_type == MessageType.MAIN_TEXT:
                return await self.text_message_handle(message)

            if message_type == MessageType.USER_HAS_ENTERED:
                await self.join_message_handle(message)

            if message_type == MessageType.USER_HAS_LEFT:
                await self.leave_message_handle(message)

            if message_type == MessageType.KICK_VOTING_HAS_FINISHED:
                await self.kick_results_message_handle(message)
        return None

    @staticmethod
    async def prepare_message_data(result: dict) -> tuple:
        message: dict | None = result.get(PacketDataKeys.MESSAGE)
        if message is None:
            raise RuntimeError(f"strange event: {result}")
        message_type: int = message[PacketDataKeys.MESSAGE_TYPE]
        return message, message_type

    async def kick_results_message_handle(self, message: dict) -> None:
        results: str = message[PacketDataKeys.TEXT]
        (kick_vote, not_kick) = map(int, results.split('|'))
        if kick_vote > not_kick:
            logging.info("бота выгнали :|\n    пересоздаем")
            await self.recreate_room()
        return None

    async def leave_message_handle(self, message: dict) -> None:
        nickname: str = message[PacketDataKeys.TEXT]
        logging.info(f"{nickname} вышел")
        self.players_nickname.remove(nickname)
        self.past_players.append(nickname)
        return None

    async def join_message_handle(self, message: dict) -> None:
        nickname: str = message[PacketDataKeys.TEXT]
        if (
            nickname
            and nickname not in self.past_players
            and nickname not in self.muted_players
            and nickname != self.bot_username
        ):
            delay: int = random.randint(2, 5)
            asyncio.create_task(
                self.delayed_send(
                    f"привет, {nickname}",
                    delay,
                    nickname
                )
            )
        return None

    def check_player(self, nickname: str | None) -> bool:
        if nickname not in self.players_nickname:
            return False
        return True

    async def text_message_handle(self, message: dict) -> str:
        user: dict = message[PacketDataKeys.USER]
        content: str = message[PacketDataKeys.TEXT]
        self.user_id = user[PacketDataKeys.OBJECT_ID]
        self.user_name = user[PacketDataKeys.USERNAME]
        self.sex = Sex(user[PacketDataKeys.SEX])
        return content


if __name__ == "__main__":
    client = Client()
    bot = RoomBot()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    try:
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        logging.info("успешный выход из программы")
