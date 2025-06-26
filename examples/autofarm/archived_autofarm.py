import asyncio
import random
import secrets
import time
import json
import string
import logging

from dataclasses import dataclass, field
from typing import List, Optional, Union

from zafiaonline.structures import PacketDataKeys
from zafiaonline.main import Client
from zafiaonline.structures.enums import Roles

UPTIME: int = int(time.time())

shadow_password = random.choice(string.ascii_lowercase)

config = input('config << ')
if not config:
    config = 'default'
try:
    with open(f'./configs/{config}.json', 'r', encoding='utf-8-sig') as cfg:
        config = json.load(cfg)
except FileNotFoundError:
    logging.error("ошибка в пути файла")
    raise
HOST: str = config.get('host', '')
ROLE: int = config.get('role', [])
REMOVE_FROM_SERVER_KILLED: bool = config.get('remove_from_server_killed', True)
TITLE: str = config.get('room_title', f'farm({shadow_password})')
PASSWORD: str = config.get('room_password', shadow_password)
MIN_LEVEL: int = config.get('min_level', 1)
VIP_ENABLED: bool = config.get('vip_enabled', False)
SHUFFLE_ACCOUNTS: bool = config.get('shuffle_accounts', False)

"""
    **MODE**
        - 1 -- победа отдается только мафиям
        - 2 -- победа отдается только мирным
        - 3 -- победа отдается в зависимости от роли основного аккаунта
        - 4 -- основной аккаунт всегда будет проигрывать
"""
MODE = int(config['mode'])
"""
    **FORCE**
        - true - победа зависит от основного аккаунта
        - false - победа не зависит от основного аккаунта
"""
FORCE = config['force']
MAX_PLAYERS = int(config['max_players'])
ACCOUNTS = config['accounts'][str(MAX_PLAYERS)]
MAIN_ACCOUNT_DATA: Union[str, List[str]] = config['main']
DISABLED_ROLES: List[int] = []

if SHUFFLE_ACCOUNTS:
    random.shuffle(ACCOUNTS)
if MAX_PLAYERS >= 9:
    DISABLED_ROLES = [Roles.SPY, Roles.CIVILIAN]
if MAX_PLAYERS == 11:
    DISABLED_ROLES = [Roles.SPY, Roles.CIVILIAN, Roles.BODYGUARD]
elif MAX_PLAYERS >= 12:
    DISABLED_ROLES = [Roles.SPY, Roles.BODYGUARD, Roles.CIVILIAN]
MAFIAS = [
    Roles.MAFIA,
    Roles.BARMAN,
    Roles.INFORMER,
    Roles.TERRORIST
]
CIVILIANS = [
    Roles.CIVILIAN,
    Roles.LOVER,
    Roles.SHERIFF,
    Roles.SPY,
    Roles.DOCTOR,
    Roles.JOURNALIST,
    Roles.BODYGUARD
]
ENABLED_ROLES: List[Roles] = [Roles.INFORMER,
                              Roles.SPY, Roles.DOCTOR, Roles.LOVER,
                              Roles.JOURNALIST]
if MODE == 1:
    ENABLED_ROLES: List[Roles] = [Roles.BARMAN, Roles.TERRORIST,
                                  Roles.LOVER, Roles.SPY, Roles.JOURNALIST,
                                  Roles.DOCTOR]


@dataclass
class Player:
    client: Client
    role: Union["Roles", int] = -1
    email: str = ""
    password: str = ""
    abr: List = field(default_factory=lambda: [])
    alive: bool = False
    disconn: bool = False

    def get_nickname(self):
        return f"{self.client.user.username}"


class Farm:
    mafia_main_data: Player

    def __init__(self):

        self.svodka_text = None
        self.rh = None
        self.played = None
        self.accounts = []
        self.players = []
        self.self_role = 0
        self.room_id = ""
        self.mafia_main = None
        self.from_file()

    def from_file(self):
        """
        Это файл с данными от аккаунтов в формате '''email:password'''
        """
        for account in ACCOUNTS:
            data = account.split(":")
            self.accounts.append([data[0], data[1]])

    @property
    def is_killing_mafia(self) -> bool:
        if MODE == 3:
            # return self.self_role in [Roles.CIVILIAN,
            # Roles.LOVER, Roles.SHERIFF, Roles.SPY]
            # and self.find_by_username('kwepfi')[1] in
            # [Roles.CIVILIAN, Roles.LOVER, Roles.SHERIFF, Roles.SPY]
            return self.self_role in CIVILIANS
        if MODE == 4:
            return not (self.self_role in CIVILIANS)
        return bool(MODE - 1)

    @property
    def get_who_civs(self):
        return list(filter(lambda x: x.role in CIVILIANS and x.alive,
                           self.players))

    @property
    def get_who_mafia(self):
        return list(filter(lambda x: x.role in MAFIAS and x.alive,
                           self.players))

    def get_who_civ_may_kill(self, role: int = 0):
        if role:
            if role in CIVILIANS:
                return self.get_who_mafia
            elif role in MAFIAS:
                return self.get_who_civs
        if self.is_killing_mafia:
            return self.get_who_mafia
        return self.get_who_civs

    def get_who_mafia_may_kill(self):
        informer_or_barmen = list(filter(lambda x: x.role not in MAFIAS and
                                                   x.alive, self.players))
        if self.is_killing_mafia and len(
                list(filter(lambda x: x.role in [Roles.BARMAN, Roles.INFORMER]
                                      and x.alive, self.players))) >= 1:
            informer_or_barmen = list(filter(
                lambda x: x.role in [Roles.BARMAN, Roles.INFORMER] and
                          x.alive, self.players))
        disconnecting_list = list(filter(
            lambda x: x.disconn, informer_or_barmen))
        return disconnecting_list if disconnecting_list else informer_or_barmen

    def get_player_role(self, player_role=Roles.SHERIFF):
        return list(filter(lambda x: x.role == player_role and x.alive,
                           self.conn_players()))

    def get_who_journalist_may_check(self) -> List[Player]:
        return list(
            filter(lambda x: x.role != Roles.JOURNALIST and Roles.JOURNALIST
                             not in x.abr and x.alive, self.players))

    def get_who_sheriff_may_check(self) -> List[Player]:
        return list(filter(lambda x: x.role !=
                                     Roles.SHERIFF and Roles.SHERIFF not in
                                     x.abr and x.alive, self.players))

    def get_who_lover_may_loving(self):
        possibly_disconnected = self.disconn_players if (
            self.disconn_players) else self.players
        return list(filter(lambda x: x.role not in
                                     [Roles.LOVER, Roles.TERRORIST,
                                      Roles.MAFIA]
                                     and x.alive, possibly_disconnected))

    def get_who_terrorist_may_boom(self):
        if self.is_killing_mafia:
            return list(filter(lambda x: x.role !=
                                         Roles.TERRORIST, self.get_who_mafia))
        return self.get_who_civs

    def get_who_doctor_may_health(self):
        if self.is_killing_mafia:
            who_health = [Roles.DOCTOR, Roles.INFORMER, Roles.BARMAN]
        else:
            who_health = CIVILIANS
        return list(filter(lambda x: x.role not in
                                     who_health and x.alive, self.players))

    def find_by_username(self, username: str) -> List[Player]:
        return [player for player in self.players if
                player.client.user.username == username and player.alive]

    async def join_to_room(self, account: Client):
        await account.join_room(self.room_id, PASSWORD)
        await asyncio.sleep(0.18)
        await account.create_player(self.room_id)

    @staticmethod
    async def create_client(email: str, password: str) -> Player:
        while True:
            client = Client()
            try:
                response = await client.sign_in(email, password)
                await asyncio.sleep(.01)
            except Exception as e:
                logging.error(f"создание клиента невозможно,"
                             f" удаляем клиент {e}")
                await client.disconnect()
                await asyncio.sleep(2)
                continue
            if not response:
                await client.disconnect()
                await asyncio.sleep(0.5)
                logging.error("no response")
                continue
            else:
                return Player(client, -1, email, password, [], True, False)

    async def rehost(self, skip_timer: bool = False) -> None:
        if not skip_timer:
            logging.info("\nПересоздаем. ждём 26 секунд\n")
        for player in self.conn_players():
            await player.client.disconnect()

        self.played = False
        self.rh = False
        if not skip_timer:
            time.sleep(26)
        else:
            time.sleep(2)
        logging.info('go')

    async def shuher(self, user_id: str = "user_57e6cce718056") -> Optional[
        bool]:
        result = await self.mafia_main.get_user(user_id)
        profile = result[PacketDataKeys.USER]
        if profile[PacketDataKeys.IS_ONLINE] == "true":
            return profile[PacketDataKeys.SERVER_LANGUAGE]
        return None

    def conn_players(self) -> List[Player]:
        return list(filter(lambda x: not x.disconn and x.alive, self.players))

    @property
    def disconn_players(self) -> List[Player]:
        return list(filter(lambda x: x.disconn and x.alive, self.players))

    def get_listener(self, current_listener: Client = None) -> None:
        listeners = self.get_who_mafia
        if self.is_killing_mafia:
            listeners = self.get_who_civs
        if current_listener:
            listeners = list(filter(
                lambda x: x.client.user_id != current_listener.user_id,
                listeners))
        return random.choice(list(
            filter(lambda x: not x.disconn, listeners))).client

    def get_host(self) -> Client:
        return self.mafia_main if not HOST else (
            list(filter(lambda x: x.email == HOST, self.players))[0].client)

    @staticmethod
    async def search_role(player: Player) -> int:
        try:
            data = await player.client.get_data(PacketDataKeys.ROLES)
            return data[PacketDataKeys.ROLES][0][PacketDataKeys.ROLE]
        except Exception as e:
            logging.error(f"error search role {e}")
            return -1

    async def start(self):
        number_of_games = 1
        logging.info(f'скрипт перезапустился. режим: {MODE}. аккаунт -'
                     f' {MAIN_ACCOUNT_DATA[0]}')
        self.rh = True
        shuhers = 0
        stopers = 0
        for _ in range (99999999):
            room_time = time.time()
            self.players: List[Player] = []
            for account in self.accounts:
                self.players.append(await self.create_client(account[0],
                                                            account[1]))
            self.mafia_main_data: Player = await self.create_client(
                MAIN_ACCOUNT_DATA[0], MAIN_ACCOUNT_DATA[1])
            self.mafia_main = self.mafia_main_data.client
            self.players.append(self.mafia_main_data)
            shuher_wowa = await self.shuher()
            client = Client()

            if SHUFFLE_ACCOUNTS is True:
                random.shuffle(ACCOUNTS)
            #def shuher_log(self): -> None
            #logging.info("! Шухер (wowa), но не на ru сервере,
            # " поэтому ждём 3 минуты")
            #await asyncio.sleep(shuher_time)
            #shuhers += 1
            if shuher_wowa:
                if shuher_wowa != "ru":
                    logging.info(f"! Шухер (wowa), но не на {shuher_wowa} "
                                 f"сервере,"
                                 " поэтому ждём 3 минуты")
                    await client.disconnect()
                    time.sleep(150)
                    shuhers += 1
                    continue
                else:
                    logging.info(f"! ШУХЕР (wowa) НА {shuher_wowa} "
                                 f"СЕРВЕРЕ !\n ждём 10 минут")
                    await client.disconnect()
                    time.sleep(600)
                    shuhers += 1
                    continue
            while True:
                try:
                    # rating = self.mafia_main.get_rating(
                    # RatingType.WINS)["rul"]
                    # self.mafia_main.select_language("en")
                    await asyncio.sleep(.2)
                    room = await self.get_host().create_room(ENABLED_ROLES,
                                                             TITLE,
                                                             max_players=
                                                             MAX_PLAYERS,
                                                             password=
                                                             PASSWORD,
                                                             min_level=
                                                             MIN_LEVEL,
                                                   vip_enabled = VIP_ENABLED)
                    break
                except Exception as e:
                    logging.info(f"произошла ошибочка, {e}")
                    await asyncio.sleep(.5)

            await asyncio.sleep(.1)
            logging.info("Создалась комната")
            self.svodka_text = (f"[👤] аккаунт: "
                                f"{self.mafia_main_data.get_nickname()}\n")
            self.room_id = room.room_id
            for index, account in enumerate(self.players):
                await self.join_to_room(account.client)
                await asyncio.sleep(2)

            logging.info("Все вошли")
            self.played = True
            last_empty_packet_time = 0
            day_gs = 0

            listener_account = self.mafia_main
            # if self.rh:
            # self.rehost()
            while self.played:
                try:
                    data = await listener_account.listen()
                    if data is None:
                        continue
                except Exception as e:
                    #data = {PacketDataKeys.TYPE: "empty"}
                    logging.error(f"ошибка при обработке данных: {e}")
                    continue
                data_type = data.get(PacketDataKeys.TYPE)
                if data_type == PacketDataKeys.GAME_STATUS:
                    game_type = data[PacketDataKeys.GAME_STATUS]
                    if game_type == 2:
                        logging.info("Игра началась")
                    elif game_type == 1:
                        logging.info("Ждём начала")
                    else:
                        logging.info("\n\n\n")
                elif (data_type == PacketDataKeys.PLAYERS_STAT and
                      self.players[0].role == -1):
                    for index, account in enumerate(self.players):
                        role = await self.search_role(account)
                        if role == -1:
                            logging.info('failed get role_id')
                            await self.rehost()
                            break
                        self.players[index].role = role
                        if account.client.user_id == self.mafia_main.user_id:
                            self.self_role = role

                            logging.info(f"Номер твоей роли"
                                         f" ({MAIN_ACCOUNT_DATA[0]}):"
                                         f" {self.self_role}")
                        else:
                            if (role in DISABLED_ROLES and
                                    account.client.user_id !=
                                    self.mafia_main.user_id):
                                await account.client.disconnect()
                                self.players[index].disconn = True
                                logging.info("отключаем:")
                            logging.info(f"у игрока {account.get_nickname()}"
                                         f" роль: {role}")
                    if MODE == 4 or (not FORCE and MODE in [1, 2]):
                        logging.info(f"Убиваем: "
                        f"{'МАФОВ' if self.is_killing_mafia else 'МИРОВ'}")

                    elif ((ROLE and self.self_role not in ROLE) or
                          (not ROLE and FORCE and MODE != 3 and (
                            (self.self_role in CIVILIANS and not
                            self.is_killing_mafia) or
                            (self.self_role in MAFIAS and
                             self.is_killing_mafia)))):
                        logging.info('unavailable role')
                        await self.rehost()
                        break
                    #listener_account = self.get_listener()

                elif data_type == PacketDataKeys.GAME_DAYTIME:
                    type_day = data[PacketDataKeys.DAYTIME]
                    if type_day == 2:
                        logging.info("Чатятся")
                elif data_type == PacketDataKeys.GAME_FINISHED:

                    work_time = time.time() - UPTIME
                    of_hours = ((number_of_games / work_time) * 60) * 60
                    of_days = int(of_hours * 24)
                    work_time_hours = int(work_time / 3600)
                    work_time_minutes = (work_time % 3600) // 60
                    all_wins = (self.mafia_main.user.wins_as_mafia +
                                self.mafia_main.user.wins_as_peaceful + 1)
                    logging.info(
                        f"[🏆] {number_of_games} игра закончилась\n[⏳]"
                        f" {int(time.time() - room_time)} секунд\n"
                        f"[👤] роль: {self.self_role}\n[🔎] +"
                            f"{data[PacketDataKeys.SILVER_COINS]} авторитета,"
                        f" +{data[PacketDataKeys.EXPERIENCE]} опыта\n"
                        f"[⏰] ~{of_days} за сутки\n[⏰] "
                        f"~{of_hours} за час\n"
                        f"всего побед ~{all_wins}\n"
                        f"[💼] скрипт работает {work_time_hours} "
                        f"часов {work_time_minutes} минут\n"
                        f"[👀] всего шухеров: {shuhers} "
                        f"({shuhers * 10} потерянных минут)\n[] "
                        f"всего сбоев: {stopers}")
                    await self.rehost(True)
                    self.rh = True
                    number_of_games += 1
                #elif data_type == PacketDataKeys.USER_DATA:
                #    data = data[PacketDataKeys.DATA]
                #    if len(data) > 3:
                #        boolean = True
                #        for packet in data:
                #            if packet.get(PacketDataKeys.ROLE) == "":
                #                boolean = False
                #            if not boolean:
                #                continue
                #        logging.info("закончилась сбойная игра, рехост")
                #        await self.rehost(True)
                #        self.rh = True
                #        number_of_games += 1
                elif (data_type == PacketDataKeys.MESSAGE or
                      data_type == PacketDataKeys.MESSAGES):

                    if data_type == PacketDataKeys.MESSAGES:
                        logging.debug(f"data: {data}")
                        message = data[PacketDataKeys.MESSAGE][-1]
                    else:
                        logging.debug(f"data: {data}")
                        logging.debug(f"data[PacketDataKeys.MESSAGE]: "
                                      f"{data.get(PacketDataKeys.MESSAGE)}")
                        message = data[PacketDataKeys.MESSAGE]
                    if message[PacketDataKeys.MESSAGE_TYPE] == 5:
                        logging.info("Мафия в чате")
                        try:
                            loving_list = self.get_who_lover_may_loving()
                            lover = self.get_player_role(Roles.LOVER)
                            if loving_list and lover:
                                loved = random.choice(loving_list)
                                await lover[0].client.role_action(
                                    loved.client.user_id, self.room_id)
                                logging.info(f"любовница на "
                                             f"{loved.get_nickname()}")
                        except Exception as e:
                            logging.error(f"\nОшибка при действии любовницы"
                                         f" {e} \n")
                            #raise
                    elif message[PacketDataKeys.MESSAGE_TYPE] in [3, 12]:
                        username = message[PacketDataKeys.TEXT]
                        logging.info(f"Убили {username}")
                        removed_player = self.find_by_username(username)
                        if not removed_player:
                            continue
                        for ind, player in enumerate(self.players):
                            if player.email == removed_player[0].email:
                                self.players[ind].alive = False
                        if REMOVE_FROM_SERVER_KILLED:
                            if (not removed_player[0].disconn and
                                    removed_player[0].client.user_id !=
                                    self.mafia_main.user_id):
                                await removed_player[0].client.disconnect()
                                logging.info("удаляем труп с сервера")
                            self.players.remove(removed_player[0])
                    elif message[PacketDataKeys.MESSAGE_TYPE] == 18:
                        username_boom = message[PacketDataKeys.TEXT]
                        boom = (message[PacketDataKeys.USER][
                            PacketDataKeys.USERNAME])
                        logging.info(f'{boom} взорвал {username_boom}')
                        for username in [username_boom, boom]:
                            removed_player = self.find_by_username(username)
                            if removed_player:
                                for ind, player in enumerate(self.players):
                                    if player.email == removed_player[0].email:
                                        self.players[ind].alive = False
                                if REMOVE_FROM_SERVER_KILLED:
                                    if (not removed_player[0].disconn and
                                            removed_player[0].client.user_id !=
                                            self.mafia_main.user_id):
                                        await (removed_player[0]
                                               .client.disconnect())
                                        logging.info("удаляем труп от терра с "
                                                     "сервера")
                                    self.players.remove(removed_player[0])
                    elif message[PacketDataKeys.MESSAGE_TYPE] in [9, 13]:
                        died_user = self.find_by_username(
                            message[PacketDataKeys.TEXT])[0]
                        killer_user = self.find_by_username(message.get(
                            PacketDataKeys.USER, {}).get(
                            PacketDataKeys.USERNAME))[0]
                        logging.info(f"{killer_user.get_nickname()} ударил в"
                                     f" {died_user.get_nickname()}")
                    elif message[PacketDataKeys.MESSAGE_TYPE] == 6:
                        logging.info("Мафия выбирает жертву")
                        try:
                            killing_list = self.get_who_mafia_may_kill()
                            killed = random.choice(killing_list)
                            for mafia in list(filter(lambda x: not x.disconn,
                                                     self.get_who_mafia)):
                                if (mafia.client.user_id ==
                                        killed.client.user_id):
                                    await (mafia.client.role_action
                                           (random.choice(self.get_who_civs)
                                            .client.user_id, self.room_id))
                                else:
                                    await (mafia.client.role_action
                                           (killed.client.user_id,
                                            self.room_id))
                        except Exception as e:
                            logging.error(f"Ошибка при убийстве?????? {e}")
                            #raise
                        try:
                            killing_list =\
                                self.get_who_journalist_may_check()[:2]
                            journalist = self.get_player_role(Roles.JOURNALIST)
                            if journalist and killing_list:
                                for checkering in killing_list:
                                    for ind, player in enumerate(self.players):
                                        if player.email == checkering.email:
                                            (self.players[ind].abr.append
                                             (Roles.JOURNALIST))

                                    await (journalist[0].client.
                                           role_action(
                                        checkering.client.user_id,
                                        self.room_id))
                        except Exception as e:
                            logging.error(f"!!! Ошибка при журе?????? {e}")
                            #raise
                        await asyncio.sleep(.2)
                        try:
                            checked_list = self.get_who_sheriff_may_check()
                            sheriff = self.get_player_role(Roles.SHERIFF)
                            if checked_list and sheriff:
                                checked = random.choice(checked_list)
                                for ind, player in enumerate(self.players):
                                    if player.email == checked.email:
                                        (self.players[ind].abr.append
                                         (Roles.SHERIFF))

                                await (sheriff[0].client.role_action
                                       (checked.client.user_id, self.room_id))
                                logging.info(f"Чекнул "
                                             f"{checked.get_nickname()}")
                        except Exception as e:
                            logging.error(f"!!! Ошибка при чеке?????? {e}")
                        try:
                            checked_list = self.get_who_doctor_may_health()
                            doctors = self.get_player_role(Roles.DOCTOR)
                            for doctor in doctors:
                                checked = random.choice(checked_list)
                                await (doctor.client.role_action
                                       (checked.client.user_id, self.room_id))
                                logging.info(f"Вылечил "
                                             f"{checked.get_nickname()}")
                        except Exception as e:
                            logging.error(f"!!! Ошибка при лечении?????? {e}")
                    elif message[PacketDataKeys.MESSAGE_TYPE] == 8:
                        day_gs += 1
                        if ((MODE == 2 and day_gs > 3) or
                                (MODE == 1 and day_gs > 6)):
                            logging.info("слишком много дневных гс, "
                                         "делаем рх")
                            await self.rehost()
                            stopers += 1
                            break
                        logging.info("Дневное гс")

                        terr = self.get_player_role(Roles.TERRORIST)
                        boomeds = self.get_who_terrorist_may_boom()
                        ignore = []
                        if terr and boomeds:
                            boomed = random.choice(boomeds)
                            ignore = [terr[0].client.user_id,
                                      boomed.client.user_id]
                            try:
                                await (terr[0].client.role_action
                                       (boomed.client.user_id, self.room_id))
                            except Exception as e:
                                terr[0].disconn = True
                                logging.info("терр откинулся", e)
                            await asyncio.sleep(.4)

                        who_may_killed = list(filter
                                              (lambda x: x.client.user_id
                                                         not in ignore,
                                               self.get_who_civ_may_kill()))
                        if who_may_killed:
                            who_killed = random.choice(who_may_killed)
                            for player in self.conn_players():
                                try:
                                    if (player.client.user_id ==
                                            who_killed.client.user_id):
                                        await player.client.role_action(
                                            random.choice
                                            (self.get_who_civ_may_kill
                                             (player.role)).client.user_id,
                                            self.room_id)
                                    else:
                                        await player.client.role_action(
                                            who_killed.client.user_id,
                                            self.room_id)
                                except Exception as e:
                                    logging.error({e})

                elif data_type == "empty":
                    if not last_empty_packet_time:
                        last_empty_packet_time = time.time()
                    else:
                        if (time.time() - last_empty_packet_time) > 5:
                            logging.error("ХАРД СБОЙ... скипаем")
                            # listener_ac
                            # count = self.get_listener(listener_account)
                            # for index, player in enumerate(self.players):
                            #    if player[0].user.username ==
                            #    listener_account.user.username:
                            #        try:
                            #            player[0].delete()
                            #        except:
                            #            logging.info("failed of end session"
                            #            , True)
                            #        resession = self.create_client
                            #        (player[2][0], player[2][1])
                            #        self.join_to_room(resession[0])
                            #        self.players[index][0] = resession[0]
                            #        listener_account = resession[0]
                            last_empty_packet_time = 0
                            stopers += 1
                            await self.rehost()
                elif not data_type:
                    last_empty_packet_time = 0
                    if (data.get(PacketDataKeys.MESSAGE_TYPE) and not
                    data[PacketDataKeys.MESSAGE_TYPE] % 10):
                        for index, player in enumerate(self.conn_players()):
                            try:
                                await player.client.send_message_room(
                                    secrets.token_hex(3), self.room_id)
                            except Exception as e:
                                logging.info(
                                    f"отвалился аккаунт"
                                    f" {player.get_nickname()}."
                                    f" удаляем его из списка игроков: {e}")
                                self.players[index].disconn = True
                                size_disabled_accounts = len(self.
                                                             disconn_players)
                                logging.info(f"{size_disabled_accounts}")
                                if size_disabled_accounts > 5:
                                    logging.info("отсоединилось больше "
                                                 "5 акков, делаем рехост")
                                    stopers += 1
                                    await self.rehost()
                        logging.info(f">> [⌚] "
                                f"{data.get(PacketDataKeys.MESSAGE_TYPE)}")


farm = Farm()
logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        datefmt="%H:%M:%S")
try:
    asyncio.run(farm.start())
except KeyboardInterrupt:
    pass
