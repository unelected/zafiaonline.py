import asyncio
import sys
import os
import traceback

from typing import Optional

from zafiaonline.structures import PacketDataKeys, MessageType

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from configs.utils.utils import *


class Farm:
    mafia_main_data: Player

    def __init__(self):
        self.room_roles: list = []
        self.unavailable_hosts: list = []
        self.host = None
        self.give_up_start_flag: bool |None = None
        self.gs_time_flag: bool | None = None
        self.played: bool |None = None
        self.accounts = []
        self.players = []
        self.self_role: int | Roles = 0
        self.count: int = 0
        self.room_id: str | None = ""
        self.room_password: str | None = None
        self.minimal_level: int | None = None
        self.mafia_main: Client | None = None
        self.listener_account: Client | None = None
        self.from_file()
        self.cautiously_flag: bool | None = None
        self.continue_flag: bool | None = None
        self.give_up_flag: bool | None = None
        self.action_time_flag: bool | None = None
        self.server = None
        self.state: dict[str, int] = {
            "number_of_games": 1,
            "cautions": 0,
            "stoppers": 0,
        }

    async def start(self):
        callbacks = await self.prepare_start_farm()
        await self.farm_action(callbacks)

    async def farm_action(self, callbacks):
        while True:
            result = await self.prepare_playing(callbacks)
            if result is False:
                continue

            cautions, number_of_games, room_time, stoppers, day_gs, days = (
                result)

            await self.start_playing(callbacks, cautions, day_gs, days,
                                     number_of_games, room_time, stoppers)

    async def prepare_playing(self, callbacks):
        cautions, number_of_games, room_time, stoppers = \
            await self.prepare_data()

        if await self.handle_cautiously(callbacks):
            callbacks.get("cautiously", lambda: None)()
            return False

        room = await self.create_and_prepare_room(callbacks)
        if not room:
            callbacks.get("stopper", lambda: None)()
            return False

        day_gs, days = await self.prepare_game_data()
        return cautions, number_of_games, room_time, stoppers, day_gs, days

    async def start_playing(self, callbacks, cautions, day_gs, days,
                            number_of_games, room_time, stoppers):
        while self.played:
            data = await self.get_data_action(callbacks)
            if data is None:
                break

            try:
                await self.handle_data(data, number_of_games, room_time,
                                       cautions, stoppers, day_gs, days,
                                       callbacks)
            except StopIteration:
                pass


    async def prepare_start_farm(self):
        logging.info(f'скрипт перезапустился. режим: {MODE}. аккаунт -'
                     f' {MAIN_ACCOUNT_DATA[0]}')
        callbacks = self.create_callbacks()
        await self.check_cautiously_and_prepare_players(callbacks)
        await self.check_max_games()
        if VIP_ENABLED:
            await self.buy_vip_for_farm()
        return callbacks

    async def check_cautiously_and_prepare_players(self, callbacks):
        if await self.prepare_players(callbacks) == "cautiously":
            callbacks.get("cautiously", lambda: None)()

    async def get_data_action(self, callbacks):
        data = await self.get_data_handle(callbacks)
        if data is not None:
            return data
        return None

    async def get_data_handle(self, callbacks):
        try:
            if not self.listener_account:
                raise AttributeError("No listener acccount")
            data = await self.listener_account.listen()
        except TimeoutError:
            await self.stop_farm_action(callbacks)
            return None
        except Exception as e:
            await self.exception_data_action(callbacks, e)
            raise
        if data is None:
            await self.no_data_action(callbacks)
            return None
        return data

    async def no_data_action(self, callbacks):
        callbacks.get("stopper", lambda: None)()
        await self.recreate_room(callbacks=callbacks)

    async def exception_data_action(self, callbacks, e):
        logging.info(f"неизвестная ошибка: {e}", exc_info=True)
        await self.stop_farm_action(callbacks)

    async def stop_farm_action(self, callbacks):
        await self.remove_accounts_from_server()
        callbacks.get("stopper", lambda: None)()

    async def prepare_game_data(self):
        self.played = True
        self.listener_account = self.mafia_main
        day_gs = 0
        days = 0
        return day_gs, days

    async def prepare_data(self):
        room_time = time.time()
        cautions = self.state["cautions"]
        number_of_games = self.state["number_of_games"]
        stoppers = self.state["stoppers"]
        return cautions, number_of_games, room_time, stoppers

    async def buy_vip_for_farm(self):
        await self.get_players_who_can_buy_vip()
        await self.players_buy_vip()

    async def players_buy_vip(self):
        for player in self.players:
            if (player.client.user.is_vip == 0 and
                    player.client.user.authority >= 20000):
                await self.buy_vip_action(player)

    async def get_players_who_can_buy_vip(self):
        for player in self.players:
            if (player.client.user.is_vip == 0 and
                    player.client.user.authority <
                    20000):
                await self.users_is_have_no_vip_action()

    @staticmethod
    async def buy_vip_action(player):
        await player.client.buy_vip()
        logging.info(f"куплен вип у {player.client.user.username}")
        await asyncio.sleep(1)

    @staticmethod
    async def users_is_have_no_vip_action():
        logging.info("невозможно сделать полноценный вип фарм, "
                     "не у всех есть возможность приобрести вип")
        sys.exit()

    def create_callbacks(self):
        def add_game():
            self.state["number_of_games"] += 1

        def cautiously():
            self.state["cautions"] += 1

        def stopper():
            self.state["stoppers"] += 1
            return

        def break_loop():
            return

        return {
            "add_game": add_game,
            "cautiously": cautiously,
            "stopper": stopper,
            "break_loop": break_loop,
        }

    async def check_games(self):
        """Проверяет лимиты игр как для всех, так и для отдельных игроков."""
        await self.check_total_games()
        await self.check_players_games()

    async def check_total_games(self):
        """Проверяет, достигнут ли общий лимит игр."""
        if MAX_GAMES and self.mafia_main:
            games = self.mafia_main.user.played_games + 1
            message = "Игры равны нужному количеству, фарм завершен."
            await self.check_games_limit(games, MAX_GAMES, message)

    async def check_players_games(self):
        """Проверяет, достигнут ли лимит игр для каждого игрока."""
        if MAX_ACCOUNTS_GAMES:
            for player in self.players:
                games = player.client.user.played_games + 1
                message = (
                    f"У {player.client.user.username} игры равны нужному "
                    f"количеству, фарм завершен.")
                await self.check_games_limit(games, MAX_ACCOUNTS_GAMES, 
                                             message)

    async def check_wins(self):
        """Проверяет, достигнуто ли максимальное количество побед."""
        if not MAX_WINS:
            return

        games = await self.get_wins_count()
        if not games:
            logging.error(
                "Не удалось определить MAX_WINS_MODE, проверь конфиг.")
            sys.exit()

        message = "Игры равны нужному количеству, фарм завершен."
        await self.check_games_limit(games, MAX_GAMES, message)

    async def get_wins_count(self):
        """Определяет количество побед в зависимости от режима."""
        return await self.get_wins_with_attributes() or await self.get_wins()
    
    async def get_wins(self):
        if MODE == 1 and self.mafia_main:
            return self.mafia_main.user.wins_as_mafia + 1
        elif MODE == 2 and self.mafia_main:
            return self.mafia_main.user.wins_as_peaceful + 1
        return None

    async def get_wins_with_attributes(self):
        if MAX_WINS_MODE and MODE not in {1, 2}:
            if MAX_WINS_MODE == "mafia" and self.mafia_main:
                return self.mafia_main.user.wins_as_mafia + 1
            elif MAX_WINS_MODE == "civilian" and self.mafia_main:
                return self.mafia_main.user.wins_as_peaceful + 1
        return None

    @staticmethod
    async def check_games_limit(current_games, max_games, message):
        if current_games >= max_games:
            logging.info(message)
            sys.exit()

    async def check_max_games(self):
        """Проверка, не превышено ли максимальное количество игр."""
        await self.check_total_games_limit()
        await self.check_players_games_limit()

    async def check_total_games_limit(self):
        """Проверяет, не превышено ли общее количество игр."""
        if MAX_GAMES and self.mafia_main:
            games = self.mafia_main.user.played_games
            message = "Количество игр достигло лимита, завершаем."
            await self.check_games_limit(games, MAX_GAMES, message)

    async def check_players_games_limit(self):
        """Проверяет, не превышено ли количество игр у отдельных игроков."""
        if MAX_ACCOUNTS_GAMES:
            for player in self.players:
                games = player.client.user.played_games
                message = (f"Количество игр у {player.client.user.username} "
                           f"достигло лимита, завершаем.")
                await self.check_games_limit(games, MAX_ACCOUNTS_GAMES, 
                                             message)

    async def handle_cautiously(self, callbacks):
        """Обработка ситуации, если был 'шухер'."""
        actions = [
                   await self.cautiously_wowa(callbacks),
                   await self.cautiously_gercog(callbacks, True),
                   #await self.cautiously_billy(callbacks, True)
                  ]

        for action in actions:
            try:
                action
            except Exception as e:
                return await self.get_moderators_profile_error_response(e)
            if self.cautiously_flag:
                self.cautiously_flag = False
                return True

        return False

    async def get_moderators_profile_error_response(self, e):
        logging.error(f"не удалось получить профиль "
                      f"администрации\nПересоздаем: {e}")
        await self.remove_accounts_from_server(False)
        return True

    async def create_and_prepare_room(self, callbacks):
        """Создаёт комнату и добавляет в неё игроков."""
        try:
            room = await self.create_the_room(callbacks)
            if room:
                self.room_id = room.room_id
            else:
                await self.create_room_error_response(callbacks)
                return None
            await self.room_creation_response(callbacks, room)
            return room
        except SystemExit:
            await self.remove_accounts_from_server()
            sys.exit()
        except Exception as e:
            logging.error(f"Ошибка при создании комнаты: {e}", exc_info=True)
            return None

    async def room_creation_response(self, callbacks, room):
        if not self.host:
            raise AttributeError("No hosts")
        logging.info(f"{self.host.user.username} создал-(а) комнату с "
                     f"названием {room.title}")
        await self.join_all_players_to_room(callbacks)

    async def create_room_error_response(self, callbacks):
        await self.recreate_room(callbacks = callbacks)
        logging.error("ошибка при создании комнаты")

    async def handle_data(self, data, number_of_games, room_time, cautions,
                          stoppers, day_gs, days, callbacks):
        """обрабатывает события на основе типа данных."""
        data_type = data.get(PacketDataKeys.TYPE)

        # обработка статуса игры
        if data_type == PacketDataKeys.GAME_STATUS:
            await self.check_game_type(data, callbacks)

        # обработка статистики игроков
        elif self.should_process_players_stat(data_type):
            await self.get_roles(callbacks)

        # обработка дневного времени
        elif data_type == PacketDataKeys.GAME_DAYTIME:
            await self.get_type_day(data, days, callbacks)

        # обработка завершения игры
        elif data_type == PacketDataKeys.GAME_FINISHED:
            await self.on_game_end(number_of_games, room_time, cautions, data,
                              stoppers, callbacks)
            await self.check_stop_farm_actions()

        # обработка сообщений
        elif data_type in (PacketDataKeys.MESSAGE, PacketDataKeys.MESSAGES):
            await self.messages_handle(data_type, data, day_gs, callbacks)

        # дополнительная проверка при отсутствии типа данных
        elif not data_type and data.get(PacketDataKeys.TIME):
            await self.handle_mafia_time(data, callbacks)

    def should_process_players_stat(self, data_type):
        return data_type == PacketDataKeys.PLAYERS_STAT and self.players[
            0].role == -1

    async def check_stop_farm_actions(self):
        await self.check_wins()
        await self.check_games()

    async def handle_mafia_time(self, data, callbacks):
        """Обрабатывает время мафии."""
        mafia_time = data.get(PacketDataKeys.TIME)
        await self.recheck_roles_on_time(callbacks, mafia_time)
        await self.print_time(mafia_time)
        await self.cautiously_on_time(callbacks, mafia_time)

    async def recheck_roles_on_time(self, callbacks, mafia_time):
        if not mafia_time % 33 and not self.self_role:
            await self.recheck_roles(callbacks)

    async def print_time(self, mafia_time):
        if not mafia_time % 10:
            # await self.check_accounts_for_active(callbacks)
            self.time_checker(mafia_time)

    async def cautiously_on_time(self, callbacks, mafia_time):
        likely_bug_time = {1, 33, 34}
        if self.cautiously_should_proceed(mafia_time, likely_bug_time):
            await self.slow_cautiously(callbacks)

    def cautiously_should_proceed(self, mafia_time, likely_bug_time):
        return (not mafia_time % 1 and not self.action_time_flag
                and not self.gs_time_flag and mafia_time
                not in likely_bug_time and not self.give_up_start_flag
                and not self.give_up_flag)

    async def slow_cautiously(self, callbacks):
        cautions = [self.cautiously_wowa(callbacks),
        #self.cautiously_billy(callbacks),
        self.cautiously_gercog(callbacks)]

        for cautiously in cautions:
            await cautiously
            if cautiously != cautions[-1]:
                await asyncio.sleep(.25)

    async def get_type_day(self, data, days, callbacks) -> None:
        """Обрабатывает тип дня и выполняет соответствующие действия."""
        if data.get(PacketDataKeys.DAYTIME) != 2:
            return  # Если не дневное время, выходим

        await self.give_up_action()
        if self.give_up_flag:
            return

        self.action_time_flag = False
        logging.info("Дневной чат")
        days += 1

        await self.check_days(days, callbacks)

    """async def check_accounts_for_active(self, callbacks):
        for index, player in enumerate(self.conn_players):
            try:
                await player.client.send_message_room(
                    " ", self.room_id)
            except Exception as e:
                await self.disconnected_account_response(callbacks, e, index,
                                                         player)

    async def disconnected_account_response(self, callbacks, e, index, player):
        size_disabled_accounts = await (
            self.inactive_account_response(e, index, player))
        if size_disabled_accounts > 5:
            await self.more_inactive_accounts_response(callbacks)

    async def more_inactive_accounts_response(self, callbacks):
        logging.error("отсоединилось больше "
                      "5 аккаунтов\nПересоздаем")
        callbacks.get("stopper", lambda: None)()
        await self.recreate_room(False, callbacks=callbacks)

    async def inactive_account_response(self, e, index, player):
        logging.error(f"отвалился аккаунт {player.get_nickname()}."
            f" удаляем его из списка игроков: {e}")
        self.players[index].disconn = True
        size_disabled_accounts = len(self.disconn_players)
        logging.debug(f"size disabled accounts{size_disabled_accounts}")
        return size_disabled_accounts"""

    @staticmethod
    def time_checker(mafia_time):
        logging.info(f">> [⌚] {mafia_time}")

    async def messages_handle(self, data_type, data, day_gs, callbacks):
        if data_type == PacketDataKeys.MESSAGES:
            message = data[PacketDataKeys.MESSAGE][-1]
        else:
            self.log_data(data)
            message = data.get(PacketDataKeys.MESSAGE)
        await self.process_message_type(message, day_gs, callbacks)

    async def process_message_type(self, message, day_gs, callbacks):
        message_type = message.get(PacketDataKeys.MESSAGE_TYPE)
        if message_type == MessageType.NIGHT_COME_MAFIA_IN_CHAT :
            await self.handle_mafia_in_chat()

        elif message_type in [MessageType.USER_HAS_LEFT, MessageType.PLAYER_KILLED]:
            await self.get_killed_player(message)

        elif message_type == MessageType.TERRORIST_BOMBED:
            await self.terrorist_action_info(message)

        elif message_type in [MessageType.VOTES_FOR, MessageType.VOTES_FOR13]:
            self.vote_info(message)

        elif message_type == MessageType.NIGHT_MAFIA_CHOOSE_VICTIM:
            await self.handle_mafia_victim_selection()

        elif message_type == MessageType.DAY_CIVILIANS_VOTING:
            await self.handle_daytime_voting(day_gs, callbacks)

    @staticmethod
    def log_data(data):
        logging.debug(f"data: {data}")
        logging.debug(f"data[PacketDataKeys.MESSAGE]: "
                      f"{data.get(PacketDataKeys.MESSAGE)}")

    async def handle_mafia_victim_selection(self):
        logging.info("Мафия выбирает жертву")
        self.action_time_flag = True
        await self.night_actions()

    async def handle_mafia_in_chat(self):
        logging.info("Мафия в чате")
        self.gs_time_flag = False
        await self.mafia_in_chat_actions()

    async def handle_daytime_voting(self, day_gs, callbacks):
        await self.prepare_daytime_voting(callbacks, day_gs)
        await self.terrorist_action()
        await self.remove_lover_action()

    async def prepare_daytime_voting(self, callbacks, day_gs):
        await self.check_for_errors_gs(day_gs, callbacks)
        logging.info("Дневное гс")
        self.gs_time_flag = True

    async def remove_lover_action(self):
        for player in self.players:
            if Roles.LOVER in player.affected_by_roles:
                player.affected_by_roles.remove(Roles.LOVER)

    """async def connect_players(self, callbacks):
        if self.mafia_main:
            await self.mafia_main.create_connection()
            if await self.handle_cautiously(callbacks):
                return "cautiously"
        self.shuffle_players()
        for player in self.players:
            if player.client.user_id != self.mafia_main.user_id:
                await player.client.create_connection()"""

    async def prepare_players(self, callbacks):
        """
        Создаёт игроков из аккаунтов, перемешивает их (если включено в
        конфиге), кроме первого.
        """
        self.players: List = []

        # Создаём основного игрока
        await self.create_main_player()
        if not self.mafia_main:
            raise AttributeError("No main account")
        self.server = self.mafia_main.user.selected_language

        if await self.handle_cautiously(callbacks):
            return "cautiously"

        # Создаём дополнительных игроков
        await self.create_additional_players()

        # Добавляем основного игрока в список
        self.players.append(self.mafia_main_data)

        # Перемешиваем игроков, если включено в конфиге
        self.shuffle_players()
        return None

    async def create_main_player(self):
        """Создаёт основного игрока."""
        self.mafia_main_data: Player = await self.create_client(
            MAIN_ACCOUNT_DATA[0], MAIN_ACCOUNT_DATA[1]
        )
        self.mafia_main = self.mafia_main_data.client

    async def create_additional_players(self):
        """Создаёт игроков из дополнительных аккаунтов."""
        self.players = [
            await self.create_client(account[0], account[1])
            for account in self.accounts
        ]
        for player in self.players:
            if player.client.user.selected_language != self.server:
                await player.client.select_language(self.server)

    def shuffle_players(self):
        """Перемешивает список игроков, если включено в конфиге."""
        if SHUFFLE_ACCOUNTS and len(self.players) > 1:
            secrets.SystemRandom().shuffle(self.players)

    def from_file(self):
        """Загружает аккаунты из списка ACCOUNTS (формат: 'email:password')."""
        if not ACCOUNTS:
            return

        for account in ACCOUNTS:
            data = account.strip().split(":")
            if len(data) == 2:  # Проверяем, что есть и email, и пароль
                self.accounts.append([data[0], data[1]])
            else:
                logging.warning(f"Некорректный формат аккаунта: {account}")

    @property
    def is_killing_mafia(self) -> bool:
        """
        Определяет, должны ли гражданские убивать мафию в текущем режиме.

        :return: True, если цель — мафия, False, если цель — мирные.
        """
        if MODE == 3:
            return self.self_role in CIVILIANS
        if MODE == 4:
            return self.self_role not in CIVILIANS
        return bool(MODE - 1)

    def get_player_team(self, team: list):
        """
        Возвращает список живых игроков, принадлежащих заданной команде.

        :param team: Список ролей, входящих в команду.
        :return: Список игроков, чья роль входит в указанный список и кто
        ещё жив.
        """
        return list(filter(lambda player: player.role in team and player.alive,
                           self.players))

    def get_who_civ_may_kill(self, role: int = 0):
        """
        Определяет, кого могут убить мирные жители в зависимости от роли игрока
        и флага убийства мафии.

        :param role: Роль игрока, по которой определяется цель убийства.
        :return: Список игроков, которых можно убить.
        """
        if role in CIVILIANS or self.is_killing_mafia:
            return self.get_player_team(MAFIAS)
        return self.get_player_team(CIVILIANS)

    def get_who_mafia_may_kill(self):
        """
        Определяет, кого может убить мафия.

        :return: Список возможных целей для убийства.
        """
        potential_targets = self.get_potential_targets()

        disconnecting_players, disconnecting_players_without_lover \
            = self.get_disconnected_players(potential_targets)

        active_disconnecting_players, active_players_without_lover \
            = self.get_active_disconnected_players(disconnecting_players)

        return (active_players_without_lover
                or disconnecting_players_without_lover
                or active_disconnecting_players
                or disconnecting_players
                or potential_targets)

    def get_active_disconnected_players(self, disconnecting_players):
        active_disconnecting_players = self.get_disconnected_active_roles(
            disconnecting_players)
        active_players_without_lover = (
            self.get_without_lover_disconnected_players(
                active_disconnecting_players))
        return active_disconnecting_players, active_players_without_lover

    def get_disconnected_players(self, potential_targets):
        disconnecting_players = self.get_disconnected_player(potential_targets)
        disconnecting_players_without_lover = (
            self.get_without_lover_disconnected_players(disconnecting_players))
        return disconnecting_players, disconnecting_players_without_lover

    def get_potential_targets(self):
        potential_targets = self.get_alive_civilians()
        if self.is_killing_mafia and self.mafia_roles_who_can_be_killed():
            potential_targets = self.get_mafias_for_kill()
        return potential_targets

    def mafia_roles_who_can_be_killed(self):
        return any(player.role in {Roles.BARMAN, Roles.INFORMER} for player in
                   self.players if player.alive)

    @staticmethod
    def get_disconnected_active_roles(disconnecting_players):
        return [player for player in
                disconnecting_players if player.role in
                ACTIVE_ROLES]

    def get_mafias_for_kill(self):
        return [player for player in self.players if
                player.role in {Roles.BARMAN,
                                Roles.INFORMER} and player.alive]

    def get_alive_civilians(self):
        return [player for player in self.players
                if player.role not in MAFIAS and player.alive]

    async def who_can_give_up(self):
        """Определяет, кто может сдаться."""
        last_alive_count = 1

        if MAX_PLAYERS in range(5, 8):
            return None

        return await self.get_last_player(last_alive_count)

    async def get_last_player(self, last_alive_count):
        for team in (CIVILIANS, MAFIAS):
            alive_team = self.get_player_team(team)
            if (len(alive_team) == last_alive_count and len(team)
                    != last_alive_count):
                return alive_team[0]
        return None

    def get_player_role(self, player_role = Roles.SHERIFF):
        if CONNECT_DISABLED_ROLES:
            result = self.role_player_not_affected(player_role)
        else:
            result = self.connected_not_affected_player(player_role)
        return result if result else []

    def connected_not_affected_player(self, player_role):
        return [player for player in self.conn_players if
                player.role == player_role and player.alive and
                Roles.LOVER not in player.affected_by_roles]

    def role_player_not_affected(self, player_role):
        return [player for player in self.players if
                player.role == player_role and player.alive and
                Roles.LOVER not in player.affected_by_roles]

    def get_who_journalist_may_check(self) -> List[Player]:
        return list(
            filter(lambda player: player.role != Roles.JOURNALIST
                    and Roles.JOURNALIST not in
                    player.affected_by_roles and player.alive, self.players))

    def get_who_sheriff_may_check(self) -> List[Player]:
        return list(filter(lambda player: player.role !=
                    Roles.SHERIFF and Roles.SHERIFF not in
                    player.affected_by_roles and player.alive, self.players))

    def get_who_lover_may_love(self):
        who_lover_cant_love = [Roles.LOVER, Roles.TERRORIST, Roles.MAFIA]
        possibly_disconnected = self.disconn_players if self.disconn_players\
            else self.players
        return list(filter(lambda player: player.role not in
                            who_lover_cant_love
                            and player.alive, possibly_disconnected))

    async def get_who_terrorist_may_boom(self):
        if await self.get_mafia_for_terrorist():
            return await self.get_mafia_for_terrorist()
        else:
            return await self.get_civilians_for_terrorist()

    async def get_civilians_for_terrorist(self):
        civilian_players = self.get_player_team(CIVILIANS)
        disconnected_civilian_players, without_lover_disconnected_players\
            = self.get_disconnected_players(civilian_players)
        dead_civilians = self.get_dead_mafia(civilian_players)
        return (dead_civilians or
                without_lover_disconnected_players or
                disconnected_civilian_players or
                civilian_players)

    async def get_mafia_for_terrorist(self):
        if self.is_killing_mafia:
            mafia_players = self.get_mafia_players()

            disconnected_civilian_players = (
                self.get_disconnected_civilian_players(mafia_players))

            dead_mafia = self.get_dead_mafia(mafia_players)
            return dead_mafia or disconnected_civilian_players or mafia_players
        return None

    @staticmethod
    def get_without_lover_disconnected_players(disconnected_civilian_players):
        return [player for player in
                disconnected_civilian_players if Roles.LOVER not in
                player.affected_by_roles]

    @staticmethod
    def get_disconnected_player(players):
        return [player for player in players if player.disconn]

    @staticmethod
    def get_dead_mafia(mafia_players):
        return [player for player in mafia_players if
                not player.alive]

    def get_mafia_players(self):
        return [player for player in self.get_player_team(MAFIAS)
                if player.role != Roles.TERRORIST]

    @staticmethod
    def get_disconnected_civilian_players(mafia_players):
        return [player for player in
                mafia_players if player.disconn and Roles.LOVER
                not in player.affected_by_roles]

    def get_who_doctor_may_health(self):
        if self.is_killing_mafia:
            who_cant_health = self.who_doctor_cant_health()
        else:
            who_cant_health = CIVILIANS
        return list(filter(lambda player: player.role not in
                            who_cant_health and player.alive, self.players))

    @staticmethod
    def who_doctor_cant_health():
        return [Roles.INFORMER, Roles.BARMAN, Roles.DOCTOR]

    @staticmethod
    async def create_client(email: str, password: str) -> Player:
        client = Client()
        while True:
            try:
                response = await client.sign_in(email, password)
            except Exception as e:
                await Farm.create_client_error(client, e)
                continue
            if not response:
                await Farm.no_response_error(client)
                continue
            else:
                return Player(client, -1, email, password, [], True, False)

    @staticmethod
    async def no_response_error(client):
        await client.disconnect()
        await asyncio.sleep(0.5)
        logging.error("no response")

    @staticmethod
    async def create_client_error(client, e):
        logging.error(f"создание клиента невозможно,"
                      f" удаляем клиент {e}")
        await client.disconnect()
        await asyncio.sleep(2)

    async def remove_accounts_from_server(self, game_finished: bool = False):
        self.unset_flags()
        players = await self.get_players_who_can_disconnect()
        await self.disconnect_players(game_finished, players)
        self.room_id = None

    async def disconnect_players(self, game_finished, players):
        if not game_finished:
            if self.room_id:
                await self.in_room_disconnect(players)
            else:
                await self.players_disconnect(players)
        else:
            await self.connected_players_disconnect(players)

    async def get_players_who_can_disconnect(self):
        return self.conn_players or [player[0] for player in self.players]

    @staticmethod
    async def connected_players_disconnect(players):
        for player in players:
            await player.client.disconnect()

    async def players_disconnect(self, players):
        if players:
            await self.player_disconnect(players)
        else:
            await self.main_account_disconnect()

    async def main_account_disconnect(self):
        await asyncio.sleep(.05)
        if self.mafia_main:
            await self.mafia_main.disconnect()

    @staticmethod
    async def player_disconnect(players):
        for player in players:
            await asyncio.sleep(.05)
            await player.client.disconnect()

    async def in_room_disconnect(self, players):
        for player in players:
            await player.client.remove_player(self.room_id)
        await self.player_disconnect(players)

    async def recreate_room(self, game_finished:bool = False,
                            callbacks = None) -> None:
        if not game_finished:
            await self.remove_accounts_from_server()
            if HOST:
                await self.selected_host_action()
            else:
                await self.delete_useless_hosts()
        else:
            await self.game_finished_action()

        if await self.prepare_players(callbacks) == "cautiously":
            if not callbacks:
                #raise AttributeError("No callbacks")
                return
            callbacks.get("cautiously", lambda: None)()
            return
        logging.info('go')
        return

    async def game_finished_action(self):
        self.unavailable_hosts.clear()
        await self.remove_accounts_from_server(True)

    async def delete_useless_hosts(self):
        authority_threshold, players_threshold, unavailable_count = \
            await self.prepare_hosts_data()
        if await self.check_for_count_useless_hosts(authority_threshold,
                                    players_threshold, unavailable_count):
            self.unavailable_hosts.pop(0)

        elif await self.too_many_unavailable_hosts(authority_threshold,
                                    players_threshold, unavailable_count):
            del self.unavailable_hosts[:3]
        logging.info("Пересоздаем.")
        self.count -= 1

    @staticmethod
    async def too_many_unavailable_hosts(authority_threshold,
                                         players_threshold, unavailable_count):
        return (unavailable_count > authority_threshold or
                unavailable_count == players_threshold)

    @staticmethod
    async def check_for_count_useless_hosts(authority_threshold,
                                            players_threshold,
                                            unavailable_count):
        return (unavailable_count == players_threshold or
                unavailable_count == authority_threshold)

    async def prepare_hosts_data(self):
        authority_players = await self.get_authority_players()
        unavailable_count = len(self.unavailable_hosts)
        authority_threshold = len(authority_players) - 2
        players_threshold = len(self.players) - 2
        return authority_threshold, players_threshold, unavailable_count

    async def get_authority_players(self):
        return [player for player in self.players if
                player.client.user.played_games >= 40]

    @staticmethod
    async def selected_host_action():
        logging.info("Пересоздаем\nЖдём 11 секунд для сброса кд "
                     "комнаты ведь ее создает только 1 игрок")
        await asyncio.sleep(10.5)

    @property
    def conn_players(self) -> List[Player]:
        return list(filter(lambda x: not x.disconn and x.alive, self.players))

    @property
    def disconn_players(self) -> List[Player]:
        return list(filter(lambda x: x.disconn and x.alive, self.players))

    """async def get_listener(self, current_listener: Client = None) -> None:
        listeners = self.get_player_team(MAFIAS)
        listeners = await self.get_civilian_listener(listeners)
        return await self.get_current_listener(current_listener, listeners)

    @staticmethod
    async def get_current_listener(current_listener, listeners):
        if current_listener:
            listeners = list(filter(
                lambda x: x.client.user_id != current_listener.user_id, 
                listeners))
        return secrets.choice(list(
            filter(lambda x: not x.disconn, listeners))).client

    async def get_civilian_listener(self, listeners):
        if self.is_killing_mafia:
            listeners = self.get_player_team(CIVILIANS)
        return listeners"""

    async def get_host(self) -> Optional[Client]:
        if not HOST:
            authority_players = await self.get_authority_players()
            if authority_players:
                valid_players = await self.get_valid_hosts(authority_players)

            else:
                valid_players = await self.get_valid_hosts(self.players)
            host_player = secrets.choice(valid_players)
            self.players.remove(host_player)
            self.players.insert(0, host_player)
            return host_player.client
        else:
            host_player = next((x for x in self.players if x.email == HOST),
                               None)
            if host_player:
                self.players.remove(host_player)
                self.players.insert(0, host_player)
                return host_player.client
            else:
                logging.info("Хост не получен")
                self.unavailable_hosts.clear()
                host_player = await self.get_host()
                if host_player:
                    logging.info("Снова получили хоста")
                    await asyncio.sleep(10.5)
                    return host_player.client
                self.unavailable_hosts.clear()
        return None

    async def get_valid_hosts(self, players):
        return [player for player in players if
                player.client.user.username not in self.unavailable_hosts]

    async def disconnect_disabled_roles(self, role, account, index):
        if role in DISABLED_ROLES:
            if not self.is_listener(account):
                elegant_remove = asyncio.create_task(
                    self.elegant_remove_player(account))
                self.players[index].disconn = True
                logging.debug("отключаем:")
                await elegant_remove

    async def elegant_remove_player(self, account):
        await account.client.remove_player(self.room_id)
        await asyncio.sleep(.1)
        await account.client.disconnect()

    async def check_game_type(self, data, callbacks):
        game_type = data[PacketDataKeys.GAME_STATUS][PacketDataKeys.STATUS]
        if game_type == 2:
            logging.info("Игра началась")
        elif game_type == 1:
            logging.info("Ждём начала")
            if self.players[
            0].role == -1:
                try:
                    await self.get_roles(callbacks)
                except Exception as e:
                    logging.debug(f"ошибка {e}")
                    pass
        else:
            logging.info("\n\n\n")

    def unset_flags(self):
        flags = [
            "played", "action_time_flag", "cautiously_flag", "give_up_flag",
            "continue_flag",
            "self_role", "gs_time_flag", "host",
            "room_roles"
        ]
        for flag in flags:
            if getattr(self, flag):  # если флаг True
                setattr(self, flag, False)  # сбрасываем флаг в False

    async def on_game_end(self, number_of_games, room_time, cautions, data,
                            stoppers, callbacks):
        try:
            self.game_results(number_of_games, room_time, cautions, data,
                              stoppers)
        except Exception as e:
            logging.info(f"результаты игры не обнаружены, {e}")
            callbacks.get("stopper", lambda: None)()
            raise
        await self.recreate_room(True, callbacks = callbacks)
        callbacks.get("add_game", lambda: None)()
        return

    async def cautiously(self, user_id, callbacks) -> Optional[
        bool]:
        listener = self.mafia_main
        if not listener:
            raise AttributeError("No listener")
        try:
            result = await listener.get_user(user_id)
        except Exception as e:
            logging.error("не получен юзер", e)
            await self.stop_farm_action(callbacks)
            return None
        try:
            if result:
                profile = result.get(PacketDataKeys.USER_PROFILE)[PacketDataKeys.PROFILE_USER_DATA]
            else:
                await self.stop_farm_action(callbacks)
                return None
        except Exception as e:
            logging.error(f"не получен профиль "
                          f"{listener.user.username} ", e)
            await self.stop_farm_action(callbacks)
            return None
        if profile[PacketDataKeys.IS_ONLINE] == True:
            return profile[PacketDataKeys.SERVER_LANGUAGE]
        return None

    """def get_listener_player(self):
        if self.conn_players:
            listener = secrets.choice(self.conn_players).client
        else:
            listener = self.mafia_main
        return listener"""

    async def cautiously_wowa(self, callbacks):
        #TODO fix bag with false caution and up caution
        cautiously_wowa = await self.cautiously(ModeratorsIDs.wow1one_id,
                                                callbacks)
        if not self.mafia_main:
            raise AttributeError("No main account")
        if cautiously_wowa:
            user_language = self.mafia_main.user.selected_language.value
            if cautiously_wowa != user_language:
                logging.warning(f"! Шухер (wowa), но не на {user_language} "
                             f"сервере,"
                             " поэтому ждём 3 минуты")
                await self.remove_accounts_from_server()
                await asyncio.sleep(180)
            else:
                logging.warning(f"! ШУХЕР (wowa) НА {user_language} "
                             f"СЕРВЕРЕ !\nждём 5 минут")
                await self.remove_accounts_from_server()
                await asyncio.sleep(300)
            if not self.cautiously_flag:
                self.cautiously_flag = True

    async def cautiously_gercog(self, callbacks, warn = False):
        cautiously_gercog = await self.cautiously(ModeratorsIDs.gercog_id,
                                                  callbacks)
        if not self.mafia_main:
            raise AttributeError("No main account")
        if cautiously_gercog:
            user_language = self.mafia_main.user.selected_language.value
            if cautiously_gercog != user_language and warn:
                logging.warning(f"! Шухер (gercog), но не на {user_language} "
                             f"сервере,"
                             " поэтому игнорируем")
                return
            else:
                logging.warning(f"! ШУХЕР (gercog) НА {user_language} "
                             f"СЕРВЕРЕ !\nждём 3 минуты")
                await self.remove_accounts_from_server()
                await asyncio.sleep(180)
            if not self.cautiously_flag:
                self.cautiously_flag = True

    """async def cautiously_billy(self, callbacks, warn = False):
        cautiously_billy = await self.cautiously(ModeratorsIDs.billy_id,
                                                 callbacks)
        if cautiously_billy:
            user_language = self.mafia_main.user.selected_language.value
            if cautiously_billy != user_language and warn:
                logging.warning(f"! Шухер (billy), но не на {user_language} "
                             f"сервере,"
                             " поэтому игнорируем")
            else:
                logging.warning(f"! ШУХЕР (billy) НА {user_language} "
                             f"СЕРВЕРЕ !\nждём 3 минуты")
                await self.remove_accounts_from_server()
                await asyncio.sleep(180)
            if not self.cautiously_flag:
                self.cautiously_flag = True"""

    async def create_the_room(self, callbacks):
        while True:
            TITLE, selected_roles = self.get_room_settings()
            self.room_roles = selected_roles
            if not TITLE:
                logging.error("ошибка в получении настроек комнаты")
                return None
            try:
                self.host = await self.get_host()
            except Exception as e:
                logging.error(f"Произошла ошибка в определении хоста, {e}")
                return None
            if not self.host:
                logging.error("Нет хоста.")
                return None
            try:
                if not self.mafia_main:
                    raise AttributeError("No main account")
                if VIP_ENABLED and not self.mafia_main.user.is_vip:
                    logging.info("у игрока нет випа")
                    sys.exit()
                self.unavailable_hosts.append(self.host.user.username)
                min_players = await self.get_min_players()
                room = await self.host.create_room(
                    selected_roles = selected_roles, title = TITLE,
                    min_players = min_players,
                    max_players= MAX_PLAYERS,
                    password = self.room_password, min_level =
                    self.minimal_level,
                    vip_enabled = VIP_ENABLED)
            except Exception as e:
                logging.error("не получилось создать комнату", e)
                await self.stop_farm_action(callbacks)
                return None
            return room

    @staticmethod
    async def get_min_players():
        if MAX_PLAYERS > 8:
            min_players = random.randint(5, (MAX_PLAYERS - 3))
        else:
            min_players = 5
        return min_players

    def get_room_settings(self):
        useless_roles = [Roles.TERRORIST, Roles.BODYGUARD]  # Все возможные
        # роли

        not_enabled_roles = self.get_not_enabled_roles()

        random_not_enabled_roles, random_useless_roles = self.random_roles(
            not_enabled_roles, useless_roles)

        selected_roles = ENABLED_ROLES[:]

        selected_roles = self.add_useless_roles(random_not_enabled_roles,
                                                random_useless_roles,
                                                selected_roles)

        self.minimal_level = secrets.choice(range(1, MIN_LEVEL + 1, 2))
        room_password = self.get_password()

        TITLE = self.get_title(room_password)
        return TITLE, selected_roles

    def get_title(self, room_password):
        if MODE == 2 and not VIP_ENABLED:
            TITLE = self.not_vip_civilian_title(room_password)

        elif MODE == 2 and VIP_ENABLED:
            TITLE = self.vip_civilian_title()

        elif MODE == 1:
            TITLE = self.mafia_title(room_password)

        else:
            TITLE: str = config.get('room_title',
                                    '')
        return TITLE

    @staticmethod
    def mafia_title(room_password):
        mafias_farm_title = get_random_mafofarm_title()
        title = generate_title(mafias_farm_title, room_password)
        TITLE: str = config.get('room_title', title)
        return TITLE

    def vip_civilian_title(self):
        if not self.count:
            raise AttributeError("No count")
        title, VIP_TITLES = get_vip_farm_title(count=self.count)
        self.count += 1
        if self.count >= len(VIP_TITLES):
            random.shuffle(VIP_TITLES)
            self.count = 0
        TITLE: str = config.get('room_title', title)
        return TITLE

    @staticmethod
    def not_vip_civilian_title(room_password):
        farm_title = get_random_farm_title()
        title = generate_title(farm_title, room_password)
        TITLE: str = config.get('room_title', title)
        return TITLE

    @staticmethod
    def add_useless_roles(random_not_enabled_roles, random_useless_roles,
                          selected_roles):
        if MAX_PLAYERS < 11:
            selected_roles += random_useless_roles
            selected_roles += random_not_enabled_roles
        return selected_roles

    @staticmethod
    def random_roles(not_enabled_roles, useless_roles):
        random_useless_roles = random.sample(useless_roles,
                                             k=random.randint(0,
                                             len(useless_roles)))  #
        # Выбираем 0, 1 или 2 роли
        random_not_enabled_roles = random.sample(not_enabled_roles,
                                                 k=random.randint(0,
                                                 len(not_enabled_roles)))
        return random_not_enabled_roles, random_useless_roles

    @staticmethod
    def get_not_enabled_roles():
        if VIP_ENABLED or MODE != 2:
            not_enabled_roles = [role for role in Roles if role not in
                                 ENABLED_ROLES and role not in
                                 [Roles.BARMAN, Roles.TERRORIST,
                                  Roles.BODYGUARD, Roles.INFORMER]]
        else:
            not_enabled_roles = [role for role in Roles if role not in
                                 ENABLED_ROLES and role not in
                                 [Roles.BARMAN, Roles.TERRORIST,
                                  Roles.BODYGUARD, Roles.INFORMER,
                                  Roles.DOCTOR]]
        return not_enabled_roles

    def get_password(self):
        if not PASSWORD:
            room_password = get_hard_shadow_password()
            self.room_password = room_password
        else:
            room_password = get_shadow_password()
            self.room_password = PASSWORD
        return room_password

    async def join_all_players_to_room(self, callbacks):
        try:
            for index, account in enumerate(self.players):
                host = index < 1
                await self.join_to_room(account.client, host, callbacks
                = callbacks)
                await self.wait_time_for_join()
                    
        except Exception as e:
            await self.remove_accounts_from_server()
            logging.info(f"неизвестная ошибка {e}")
            callbacks.get("stopper", lambda: None)()
            raise
        logging.debug("Все вошли")

    @staticmethod
    async def wait_time_for_join():
        if 8 <= MAX_PLAYERS < 11:
            await asyncio.sleep(.15)
        elif MAX_PLAYERS >= 11:
            await asyncio.sleep(1)

    async def join_to_room(self, account: Client, host:bool = False,
                           callbacks = None):
        if host:
            await self.host_join(account, callbacks)
        else:
            try:
                await self.player_join(account, callbacks)
            except SystemExit:
                await self.remove_accounts_from_server()
                sys.exit()

    async def host_join(self, account, callbacks):
        try:
            await account.create_player(self.room_id)  # host can join
        # without join_room
        except Exception as e:
            logging.error("ошибка при входе хоста", e)
            await self.stop_farm_action(callbacks)
            raise
        return

    async def player_join(self, account, callbacks):
        try:
            await account.join_room(self.room_id, self.room_password)
            await asyncio.sleep(.25)
            await account.create_player(self.room_id)

        except SystemExit:
            await self.remove_accounts_from_server()
            sys.exit()

        except Exception as e:
            logging.error(f"ошибка при входе игрока "
                          f"{account.client.user.username}, %s", e)
            await self.stop_farm_action(callbacks)
            raise
        return

    async def get_roles(self, callbacks):
        self.replace_main_account_to_top()
        for index, account in enumerate(self.players):
            role = await self.search_role(account)
            if await self.check_role(role, callbacks):
                return
            self.players[index].role = role

            if not self.mafia_main:
                raise AttributeError("No main account")
            if account.client.user_id == self.mafia_main.user_id:
                if await self.main_account_role_actions(role, account,
                                                        index, callbacks):
                    return

            else:
                await self.not_main_account_actions(role,account,index)

        if ROLE_ACCOUNTS:
            await self.role_account_actions(callbacks)

    async def role_account_actions(self, callbacks):
        players = [self.find_by_username(account)[0] for account in
                   ROLE_ACCOUNTS]
        if not any(player.role in ROLES_FOR_ROLE_ACCOUNTS for
                   player in players):
            logging.info(f"у игроков нет подходящих роли")
            await self.recreate_room(False,
                                     callbacks=callbacks)
            callbacks.get("break_loop", lambda: None)()

    def replace_main_account_to_top(self):
        self.players.remove(self.mafia_main_data)
        self.players.insert(0, self.mafia_main_data)

    @staticmethod
    async def search_role(player: Player) -> int:
        """Ищет роль игрока и возвращает её, иначе -1 при ошибке."""
        try:
            data = await player.client.get_data(PacketDataKeys.ROLES)
            return data.get(PacketDataKeys.ROLES, [{}])[0].get(
                PacketDataKeys.ROLE, -1)
        except Exception as e:
            logging.error(f"Ошибка при поиске роли: {e}", exc_info=True)
            return -1

    async def main_account_role_actions(self, role, account, index, callbacks):
        self.self_role = role

        if self.unavailable_role():
            await self.unavailable_role_actions(callbacks)
            return "unavailable role"

        elif MODE == 4 or MODE == 3:
            logging.info(f"Убиваем: "
                         f"{'МАФОВ' if self.is_killing_mafia else 'МИРОВ'}")

        if not self.mafia_main or not self.listener_account:
            raise AttributeError("No main or listener account")
        if self.mafia_main.user_id != self.listener_account.user_id:
            await self.disconnect_disabled_roles(role, account, index)
        await self.log_main_account_role()
        return None

    async def unavailable_role_actions(self, callbacks):
        logging.info('unavailable role')
        await self.recreate_room(False, callbacks=callbacks)
        callbacks.get("break_loop", lambda: None)()

    async def log_main_account_role(self):
        logging.info(f"Твоя роль"
                     f" {MAIN_ACCOUNT_DATA[0]}:"
                     f" {Roles(self.self_role).name}")

    def unavailable_role(self):
        return ((ROLE and self.self_role not in ROLE) or
                (not ROLE and FORCE and MODE != 3 and ((self.self_role
                in CIVILIANS and not self.is_killing_mafia) or
                (self.self_role in MAFIAS and self.is_killing_mafia))))

    async def not_main_account_actions(self, role, account, index):
        await self.disconnect_disabled_roles(role, account, index)
        logging.info(f"у игрока {account.get_nickname()}"
                     f" роль: {Roles(role).name}")


    async def check_role(self, role, callbacks):
        if role == -1:
            logging.error('failed get role_id')
            await self.recreate_room(False, callbacks = callbacks)
            callbacks.get("stopper", lambda: None)()
            return True
        return None

    async def mafia_in_chat_actions(self):
        asyncio.create_task(self.lover_action())
        await self.give_up_action()

    def calculate_game_statistics(self, number_of_games, cautions):
        """Вычисляет статистику по играм и времени работы."""
        work_time, work_time_hours, work_time_minutes = self.get_time_info()
        all_games, games_per_day, games_per_hour = self.get_games_info(
            number_of_games, work_time)
        all_wins = self.get_all_wins()
        cautiously_time = 3
        cautiously_time_lost = cautions * cautiously_time

        return {
            "work_time": work_time,
            "games_per_hour": games_per_hour,
            "games_per_day": games_per_day,
            "work_time_hours": work_time_hours,
            "work_time_minutes": work_time_minutes,
            "all_wins": all_wins,
            "all_games": all_games,
            "cautiously_time_lost": cautiously_time_lost
        }

    def get_all_wins(self):
        if not self.mafia_main:
            raise AttributeError("No main account")
        return (self.mafia_main.user.wins_as_mafia +
                self.mafia_main.user.wins_as_peaceful + 1)

    @staticmethod
    def get_time_info():
        work_time = time.time() - UPTIME
        work_time_hours = int(work_time / 3600)
        work_time_minutes = (work_time % 3600) // 60
        return work_time, work_time_hours, work_time_minutes

    def get_games_info(self, number_of_games, work_time):
        if not self.mafia_main:
            raise AttributeError("No main account")
        games_per_hour = ((number_of_games / work_time) * 60) * 60
        games_per_day = int(games_per_hour * 24)
        all_games = (self.mafia_main.user.played_games + 1)
        return all_games, games_per_day, games_per_hour

    def format_game_results(self, number_of_games, room_time, cautions, data,
                            stoppers, stats):
        """Форматирует данные для логирования."""
        authority = data[PacketDataKeys.SILVER_COINS]
        experience = data[PacketDataKeys.EXPERIENCE]

        if authority > 0:
            authority = f"+{authority}"
            experience = f"+{experience}"

        return (
            f"[🏆] {number_of_games} игра закончилась\n"
            f"[⏳] игра длилась: {int(time.time() - room_time)} секунд\n"
            f"[👤] роль: {self.self_role}\n"
            f"[🔎] получено: {authority} авторитета, {experience} опыта\n"
            f"[⏰] количество игр за сутки: ~{stats['games_per_day']}\n"
            f"[⏰] количество игр за час: ~{stats['games_per_hour']:.2f}\n"
            f"[🏅] всего побед: {stats['all_wins']}\n"
            f"[🎮] всего игр: {stats['all_games']}\n"
            f"[💼] скрипт работает: {stats['work_time_hours']} часов"
            f" {stats['work_time_minutes']} минут\n"
            f"[👀] всего шухеров: {cautions} (потеряно"
            f" {stats['cautiously_time_lost']} минут)\n"
            f"[⚠️] всего сбоев: {stoppers}"
        )

    def game_results(self, number_of_games, room_time, cautions, data,
                     stoppers):
        """Основной метод, объединяющий вычисления, форматирование и
        логирование."""
        stats = self.calculate_game_statistics(number_of_games, cautions)
        log_message = self.format_game_results(number_of_games, room_time,
                                               cautions, data, stoppers, stats)
        self.log_game_results(log_message)

    @staticmethod
    def log_game_results(log_message):
        """Записывает результаты в лог."""
        logging.info(log_message)

    async def lover_action(self):
        #TODO up lover
        try:
            loving_list = self.get_who_lover_may_love()
            lover = self.get_player_role(Roles.LOVER)
            if lover[0]:
                await self.create_player_in_room(lover[0])
            active_roles_list = [player for player in loving_list if
                    player.role in ACTIVE_ROLES and player.alive == True]
            if not loving_list or not lover:
                logging.debug("Нет целей для проверки или любовницы в игре.")
                return
            if DISABLED_ROLES and active_roles_list:
                # Если шериф отключен и есть в списке, выбираем только среди них
                target_list = active_roles_list
            else:
                # В остальных случаях выбираем среди всех
                target_list = loving_list

            loved = random.choice(target_list)
            await lover[0].client.role_action(
                loved.client.user_id, self.room_id)
            loved.affected_by_roles.append(Roles.LOVER)
            logging.info(f"любовница на "
                          f"{loved.get_nickname()}")
            if lover[0]:
                await self.disconnect_player_in_room(lover[0])
        except Exception as e:
            logging.debug(f"\nОшибка при выполнении действия любовницы:"
                         f" {e} \n")

    async def disconnect_player_in_room(self, player):
        if player.disconn and CONNECT_DISABLED_ROLES and not self.is_listener(
                player):
            await player.client.remove_player(self.room_id)
            await asyncio.sleep(.01)
            await player.client.disconnect()

    async def create_player_in_room(self, player):
        if player.disconn and CONNECT_DISABLED_ROLES:
            await player.client.create_connection()
            await asyncio.sleep(.1)
            await player.client.join_room(self.room_id)
            await asyncio.sleep(.3)
            await player.client.create_player(self.room_id)

    async def sheriff_action(self):
        try:
            checked_list = self.get_who_sheriff_may_check()
            sheriff = next(iter(self.get_player_role(Roles.SHERIFF)), None)

            if not checked_list or not sheriff:
                logging.debug("Шериф или список для проверки отсутствуют.")
                return
            await self.create_player_in_room(sheriff)
            checked = random.choice(checked_list)
            player = next(
                (player for player in self.players if player.email ==
                 checked.email), None)
            if player:
                player.affected_by_roles.append(Roles.SHERIFF)

                await (sheriff.client.role_action
                       (checked.client.user_id, self.room_id))
                if sheriff:
                    await self.disconnect_player_in_room(sheriff)
                logging.info(f"Шериф проверил игрока "
                             f"{checked.get_nickname()}")
        except Exception as e:
            logging.debug(f"!!! Ошибка при чеке?????? {e}")

    async def journalist_action(self):
        try:
            journalist = next(iter(self.get_player_role(Roles.JOURNALIST)),
                              None)  # Берём первого журналиста или None
            if not journalist or journalist not in self.conn_players:
                logging.debug("Журналист отсутствует.")
                return
            checking_list = self.get_who_journalist_may_check()[:2]
            # получаем список максимум из 2 игроков, которых может проверить
            # журналист
            if not checking_list:
                logging.debug("Список для проверки журналистом отсутствует.")
                return
            for checked_player in checking_list:
                # Находим игрока по email
                player = next((player for player in self.players if
                               player.email == checked_player.email), None)
                if player:
                    player.affected_by_roles.append(Roles.JOURNALIST)
                await journalist.client.role_action(checked_player.client.
                                                    user_id, self.room_id)
            logging.info(
                f"Журналист проверил: "
                f"{', '.join(p.get_nickname() for p in checking_list)}")
        except Exception as e:
            logging.debug(
                f"Ошибка при действии журналиста{e}")

    async def mafia_action(self):
        try:
            killing_list = self.get_who_mafia_may_kill()
            killed = random.choice(killing_list)
            if not killed:
                logging.info("Некого убить")
            for mafia in list(filter(lambda mafias: not mafias.disconn,
                                     self.get_player_team(MAFIAS))):
                target_id = (
                    random.choice(self.get_player_team(CIVILIANS)).client.
                    user_id
                    if mafia.client.user_id == killed.client.user_id
                    else killed.client.user_id)

                await mafia.client.role_action(target_id, self.room_id)
        except Exception as e:
            logging.error(f"Ошибка при убийстве?????? {e}"
                          f"\n{traceback.format_exc()}")

    async def doctor_action(self):
        try:
            doctors = self.get_player_role(Roles.DOCTOR)
            if not doctors:
                logging.debug("докторов нет")
                return
            health_list = self.get_who_doctor_may_health()
            if not health_list:
                logging.debug("лечить некого")
                return
            for doctor in doctors:
                await self.create_player_in_room(doctor)
                checked = random.choice(health_list)
                await (doctor.client.role_action
                       (checked.client.user_id, self.room_id))
                await self.disconnect_player_in_room(doctor)
                logging.info(f"Вылечил "
                             f"{checked.get_nickname()}")
        except Exception as e:
            logging.debug(f"!!! Ошибка при лечении?????? {e}")

    async def give_up_action(self):
        """Обрабатывает сдачу игрока, если это возможно."""
        self.give_up_start_flag = True
        surrendered = await self.who_can_give_up()

        if not surrendered:
            self.give_up_start_flag = False
            return  # Если нет игрока для сдачи, просто выходим

        await self.create_player_in_room(surrendered)
        await surrendered.client.give_up(self.room_id)

        self.give_up_flag = True
        logging.info(f"{surrendered.client.user.username} сдался-(ась)")
        await self.disconnect_player_in_room(surrendered)
        self.give_up_start_flag = False

    async def night_actions(self):
        """Выполняет ночные действия всех доступных ролей."""
        for action in self.get_night_actions():
            await action()

    def get_night_actions(self):
        """Возвращает список функций для выполнения ночью."""
        return [
            self.mafia_action,
            self.journalist_action,
            self.sheriff_action,
            self.doctor_action,
        ]

    def find_by_username(self, username: str) -> List[Player]:
        """Ищет живых игроков по имени пользователя."""
        return [
            player for player in self.players
            if player.client.user.username == username and player.alive
        ]

    async def terrorist_action_info(self, message):
        """Обрабатывает информацию о террористическом взрыве."""
        terrorist, victim = self.extract_terrorist_and_victim(message)
        self.log_terrorist_attack(terrorist, victim)

        await self.process_terrorist_casualties(terrorist, victim)

    @staticmethod
    def extract_terrorist_and_victim(message):
        """Извлекает террориста и его жертву из сообщения."""
        victim = message[PacketDataKeys.TEXT]
        terrorist = message[PacketDataKeys.USER][PacketDataKeys.USERNAME]
        return terrorist, victim

    @staticmethod
    def log_terrorist_attack(terrorist, victim):
        """Записывает в лог информацию о террористическом акте."""
        logging.info(f'{terrorist} взорвал {victim}')

    async def process_terrorist_casualties(self, *usernames):
        """Удаляет террориста и его жертву из игры."""
        for username in usernames:
            removed_player = self.find_by_username(username)
            if removed_player:
                await self.disconnect_killed(removed_player[0])

    async def get_killed_player(self, message):
        """Обрабатывает убийство игрока."""
        username = self.extract_killed_username(message)
        logging.info(f"Убили {username}")

        removed_player = self.find_by_username(username)
        if not removed_player:
            self.continue_flag = True
            return

        await self.disconnect_killed(removed_player[0])

    @staticmethod
    def extract_killed_username(message):
        """Извлекает имя убитого игрока из сообщения."""
        return message[PacketDataKeys.TEXT]

    async def disconnect_killed(self, removed_player):
        """Обрабатывает удаление убитого игрока."""
        self.disable_removed_player(removed_player)

        if REMOVE_FROM_SERVER_KILLED:
            await self.disconnect_from_server(removed_player)
        else:
            await self.disconnect_removed_player(removed_player)

    def disable_removed_player(self, player):
        """Делает игрока неактивным в списке."""
        for ind, p in enumerate(self.players):
            if p.client.user_id == player.client.user_id:
                self.players[ind].alive = False

    async def disconnect_from_server(self, player):
        """Удаляет игрока с сервера, если он не отключен и не является
        слушателем."""
        if not player.disconn and not self.is_listener(player):
            elegant_remove_player = asyncio.create_task(
                self.elegant_remove_player(player))
            logging.debug("Убитый игрок удален с сервера")
            await elegant_remove_player
        self.players.remove(player)

    async def disconnect_removed_player(self, player):
        """Удаляет игрока, если он не является слушателем."""
        if not self.is_listener(player) and not player.disconn:
            await player.client.remove_player(self.room_id)

    def is_listener(self, player):
        """Проверяет, является ли игрок слушателем."""
        if not self.listener_account:
            raise AttributeError("No listener account")
        return (player.client.user.username ==
                self.listener_account.user.username)

    def vote_info(self, message):
        """Записывает в лог информацию о голосовании: кто кого ударил."""
        died_user = self.get_victim(message)
        killer_user = self.get_killer(message)

        if killer_user:
            self.log_vote(killer_user, died_user)

    def get_victim(self, message):
        """Возвращает жертву голосования."""
        return self.find_by_username(message[PacketDataKeys.TEXT])[0]

    def get_killer(self, message):
        """Возвращает голосующего, если он есть в данных."""
        killer_username = message.get(PacketDataKeys.USER, {}).get(
            PacketDataKeys.USERNAME)
        return self.find_by_username(killer_username)[
            0] if killer_username else None

    @staticmethod
    def log_vote(killer, victim):
        """Записывает в лог информацию об голосе."""
        logging.info(
            f"{killer.get_nickname()} ударил в {victim.get_nickname()}")

    async def vote_to_killed(self, ignore):
        """Организует голосование за убийство."""
        candidates = self.get_candidates_for_kill(ignore)
        if not candidates:
            return

        victim = self.choose_victim(candidates)
        await self.execute_votes(victim)

    def get_candidates_for_kill(self, ignore):
        """Возвращает список возможных жертв, исключая переданных в ignore."""
        return self.who_may_killed(ignore)

    @staticmethod
    def choose_victim(candidates):
        """Выбирает случайную жертву из списка кандидатов."""
        return random.choice(candidates)

    async def execute_votes(self, victim):
        """Выполняет голосование, заставляя игроков голосовать за жертву."""
        for player in self.players:
            try:
                target_id = self.get_vote_target(player, victim)

                if self.played and player in self.conn_players:
                    await player.client.role_action(target_id, self.room_id)

                elif (self.played and player not in self.conn_players and
                      CONNECT_DISABLED_ROLES and player.alive):
                    await self.disconnected_role_action(player, target_id)
            except Exception as e:
                logging.error(f"Ошибка при голосовании: {e}", exc_info=True)
                raise

    async def disconnected_role_action(self, player, target_id):
        await self.create_player_in_room(player)
        await player.client.role_action(target_id, self.room_id)
        await self.disconnect_player_in_room(player)

    def get_vote_target(self, player, victim):
        """Определяет, за кого проголосует игрок."""
        if player.client.user_id == victim.client.user_id:
            return random.choice(
                self.get_who_civ_may_kill(player.role)).client.user_id
        return victim.client.user_id

    def who_may_killed(self, ignore):
        """Возвращает список игроков, которых можно убить, исключая тех,
        кто в списке ignore."""
        players = self.get_who_civ_may_kill()
        dead_players = self.get_dead_mafia(players)
        active_role_players = self.get_disconnected_active_roles(
            players)
        disconnected = self.get_disconnected_player(
            players)
        active_disconnected = self.get_disconnected_player(
            active_role_players)

        return [player for player in
                (dead_players or active_disconnected or disconnected or
                active_role_players or players)
                if player.client.user_id not in ignore]

    async def check_for_errors_gs(self, day_gs, callbacks):
        """Проверяет количество дневных голосований и перезапускает комнату
        при превышении лимита."""
        day_gs += 1
        max_day_gs = 1 if MODE == 2 else 2  # Лимит дневных ГС зависит от
        # режима

        if day_gs > max_day_gs:
            logging.error(
                "Слишком много дневных голосований.\nПересоздаем комнату.")
            await self.recreate_room(False, callbacks = callbacks)
            callbacks.get("stopper", lambda: None)()

    async def terrorist_action(self):
        """Действие террориста: выбор жертвы и подрыв."""
        terrorist = self.get_terrorist()
        if terrorist:
            await self.create_player_in_room(terrorist)

        booms = await self.get_who_terrorist_may_boom()
        if await self.validate_terrorist_action(terrorist, booms):
            return

        await self.execute_terrorist_attack(terrorist, booms)
        if terrorist:
            await self.disconnect_player_in_room(terrorist)

    def get_terrorist(self):
        """Возвращает террориста, если он есть в игре."""
        return next(iter(self.get_player_role(Roles.TERRORIST)), None)

    async def validate_terrorist_action(self, terrorist, booms):
        """Проверяет, может ли террорист действовать, и голосует за
        исключение, если нет."""
        ignore = []
        return await self.check_terrs(terrorist, booms, ignore)

    async def execute_terrorist_attack(self, terrorist, booms):
        """Выбирает жертву и выполняет подрыв."""
        boomed = random.choice(booms)
        ignore = [terrorist.client.user_id, boomed.client.user_id]

        try:
            await terrorist.client.role_action(boomed.client.user_id, self.room_id)
        except Exception as e:
            terrorist.disconn = True
            logging.debug(f"Террорист отключился: {e}", exc_info=True)
            await asyncio.sleep(0.4)

        await self.vote_to_killed(ignore)

    async def check_terrs(self, terrorist, booms, ignore):
        """Проверяет наличие террориста и целей для подрыва, иначе голосует
        за исключение."""
        if not (terrorist and booms):
            logging.debug(
                "Нет террориста или целей для подрыва. Голосуем за "
                "исключение.")
            await self.vote_to_killed(ignore)
            return True
        return None

    async def recheck_roles(self, callbacks):
        """Проверяет, не сбились ли роли, и пересоздаёт комнату при
        необходимости."""

        logging.error("Слетел чек ролей, пересоздаём комнату.")
        await self.recreate_room(callbacks = callbacks)
        callbacks.get("stopper", lambda: None)()
        return True

    async def check_days(self, days, callbacks):
        """Проверяет количество дней и пересоздаёт комнату, если условий
        слишком много."""
        if (
                (MAX_PLAYERS, MODE) == (8, 2)
                and days > 1
                and Roles.INFORMER in self.room_roles
                and Roles.MAFIA not in DISABLED_ROLES
        ):
            logging.error("Слишком много дней, пересоздаём комнату.")
            await self.recreate_room(callbacks = callbacks)
            callbacks.get("stopper", lambda: None)()

if __name__ == "__main__":
    farm = Farm()
    async def main():
        try:
            await farm.start()
        except asyncio.CancelledError:
            logging.info("Фарм закончен выходом из программы.")
        finally:
            await farm.remove_accounts_from_server()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Фарм прерван вручную.")
