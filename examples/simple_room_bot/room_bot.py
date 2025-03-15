import asyncio
import logging
import random

from aioconsole import ainput

from zafiaonline import Client
from zafiaonline.structures.packet_data_keys import PacketDataKeys
from zafiaonline.structures.enums import MessageType

from data import *

class RoomBot:
    def __init__(self):
        self.bot_username = None
        self.room_id = None
        self.sex = None
        self.user_name = None
        self.user_id = None
        self.players = []
        self.players_nickname = []
        self.past_players = []
        self.muted_players = []

    async def main(self):
        await self.prepare_bot()
        asyncio.create_task(self.chat_sender())
        await self.process_messages()

    async def prepare_bot(self):
        await client.sign_in(BotData.nickname, BotData.password)
        self.bot_username = client.user.username
        await self.prepare_mutes()
        await self.create_room_and_join()

    async def prepare_mutes(self):
        muted_list = MutedPlayersData.muted_list
        for muted in muted_list:
            self.muted_players.append(muted)

    async def process_messages(self):
        while True:
            try:
                result = await client.listen()
            except Exception as e:
                logging.debug(f"ошибка в получении сообщения {e}")
                break
            content = await self.get_data_from_results(result)
            nickname = self.user_name
            if content and nickname not in self.muted_players:
                logging.info(f"{nickname}: {content}")

    async def get_data_from_results(self, result):
        content = await self.get_messages(result)
        if result[PacketDataKeys.TYPE] == PacketDataKeys.ADD_PLAYER:
            await self.join_handle(result)
        if result[PacketDataKeys.TYPE] == PacketDataKeys.REMOVE_PLAYER:
            await self.exit_handle(result)
        return content

    async def join_handle(self, result):
        user_id, username = await self.prepare_join_player_data(result)
        self.players.append(user_id)
        self.players_nickname.append(username)
        if len(self.players) >= (RoomData.min_players -
                                 RoomData.quantity_players_for_leave):
            logging.info("слишком много игроков, пересоздаем")
            await self.recreate_room()
        logging.info(f"{username} вошёл")

    @staticmethod
    async def prepare_join_player_data(result):
        player = result[PacketDataKeys.PLAYER]
        user = player[PacketDataKeys.USER]
        user_id = user[PacketDataKeys.OBJECT_ID]
        username = user[PacketDataKeys.USERNAME]
        return user_id, username

    async def recreate_room(self):
        await client.remove_player(self.room_id)
        await asyncio.sleep(2)
        await self.create_room_and_join()

    async def create_room_and_join(self):
        room = await client.create_room(
            selected_roles = RoomData.selected_roles,
            title = RoomData.title, max_players = RoomData.max_players,
            min_players = RoomData.min_players, password = RoomData.password,
            min_level = RoomData.min_level, vip_enabled = RoomData.vip_enabled)

        if room:
            self.room_id = room.room_id
            await client.create_player(self.room_id)

    async def exit_handle(self, result):
        user_id = result[PacketDataKeys.USER_OBJECT_ID]
        self.players.remove(user_id)

    async def chat_sender(self):
        while True:
            my_message = await ainput()
            if await self.commands_handle(my_message):
                continue
            await client.send_message_room(my_message, self.room_id,
                message_style = MessageStyleData.style)

    async def commands_handle(self, my_message):
        if my_message == "/игроки":
            print(self.players_nickname)
            return True
        elif my_message.startswith("/мут"):
            await self.mute_handle(my_message)
            return True
        elif my_message.startswith("/унмут"):
            await self.unmute_handle(my_message)
            return True

    async def mute_handle(self, my_message):
        parts = my_message.split(maxsplit=1)
        if len(parts) > 1:
            nickname = parts[1]
            self.muted_players.append(nickname)
            logging.info(f"игрок {nickname} в муте")

    async def unmute_handle(self, my_message):
        parts = my_message.split(maxsplit=1)
        if len(parts) > 1:
            nickname = parts[1]
            self.muted_players.remove(nickname)
            logging.info(f"игрок {nickname} больше не в муте")

    async def delayed_send(self, response, delay):
        await asyncio.sleep(delay)
        await client.send_message_room(response, self.room_id)

    async def get_messages(self, result):
        if result[PacketDataKeys.TYPE] == PacketDataKeys.MESSAGE:
            message, message_type = await self.prepare_message_data(result)

            if message_type == MessageType.TEXT:
                return await self.text_message_handle(message)

            if message_type == MessageType.JOIN:
                await self.join_message_handle(message)

            if message_type == MessageType.LEAVE:
                await self.leave_message_handle(message)

            if message_type == MessageType.KICK_RESULTS:
                await self.kick_results_message_handle(message)

    @staticmethod
    async def prepare_message_data(result):
        message = result.get(PacketDataKeys.MESSAGE)
        message_type = message[PacketDataKeys.MESSAGE_TYPE]
        return message, message_type

    async def kick_results_message_handle(self, message):
        results = message[PacketDataKeys.TEXT]
        kick_vote, not_kick = map(int, results.split('|'))
        if kick_vote > not_kick:
            logging.info("бота выгнали :|\n пересоздаем")
            await self.recreate_room()

    async def leave_message_handle(self, message):
        nickname = message[PacketDataKeys.TEXT]
        logging.info(f"{nickname} вышел")
        self.players_nickname.remove(nickname)
        self.past_players.append(nickname)

    async def join_message_handle(self, message):
        nickname = message[PacketDataKeys.TEXT]
        if (nickname
                and nickname not in self.past_players
                and nickname not in self.muted_players
                and nickname != self.bot_username):
            delay = random.randint(2, 5)
            asyncio.create_task(
                self.delayed_send(f"привет, {nickname}", delay))

    async def text_message_handle(self, message):
        user = message[PacketDataKeys.USER]
        content = message[PacketDataKeys.TEXT]
        self.user_id = user[PacketDataKeys.OBJECT_ID]
        self.user_name = user[PacketDataKeys.USERNAME]
        self.sex = user[PacketDataKeys.SEX]
        return content


if __name__ == "__main__":
    client = Client()
    bot = RoomBot()
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        datefmt="%H:%M:%S")
    try:
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        logging.info("успешный выход из программы")