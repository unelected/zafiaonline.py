import os
import secrets
import string
import json
import logging
import random
import sys
import time
import pyfiglet

from typing import List, Union
from dataclasses import dataclass, field
from pathlib import Path
from zafiaonline.structures.models import Roles
from zafiaonline.main import Client

@dataclass
class Player:
    client: Client
    role: Union["Roles", int] = -1
    email: str = ""
    password: str = ""
    affected_by_roles: List = field(default_factory=lambda: [])
    alive: bool = False
    disconn: bool = False

    def get_nickname(self):
        return f"{self.client.user.username}"

class ModeratorsIDs:
    gercog_id: str = "d0770692-a843-4350-931f-37251d44a95d"
    billy_id: str = "user_5c7eb85c1694f002982wet"
    wow1one_id: str = "user_57e6cce718056"

UPTIME: int = int(time.time())

logging.basicConfig(level = logging.INFO,
                        format = "%(asctime)s - %(levelname)s - %(message)s",
                        datefmt = "%H:%M:%S")

ascii_banner = pyfiglet.figlet_format("autofarm", font = "slant")
print(ascii_banner)

while True:
    try:
        config = input('config << ')
    except KeyboardInterrupt:
        print("")
        sys.exit()
    if not config:
        config = 'default'
    try:
        # Создаём абсолютный путь
        config_path = Path('./configs') / f'{config}.json'
        config_path = config_path.resolve()
        with (open(config_path, 'r', encoding = 'utf-8-sig')
              as cfg):
            config = json.load(cfg)
    except FileNotFoundError:
        logging.error("Ошибка в пути файла.\nПопробуй еще раз.")
        time.sleep(.1)
    except json.JSONDecodeError:
        logging.error("Ошибка: некорректный JSON.")
        sys.exit(1)

    else:
        if os.name == 'nt':
            os.system('cls')
        elif os.getenv('TERM'):
            os.system('clear')
        else:
            print("\n" * 100)
        break

HOST: str = config.get('host', '')
ROLE: list[int] = config.get('role', [])
REMOVE_FROM_SERVER_KILLED: bool = config.get('remove_from_server_killed', True)
MIN_LEVEL: int = config.get('min_level', 1)
VIP_ENABLED: bool = config.get('vip_enabled', False)
SHUFFLE_ACCOUNTS: bool = config.get('shuffle_accounts', True)
PASSWORD: str = config.get('room_password', '')
MAX_WINS_MODE: str = config.get('max_wins_mode')
MAX_WINS: int = config.get('max_wins')
CONNECT_DISABLED_ROLES: bool = config.get('connect_disabled_roles')

MAX_ACCOUNTS_GAMES: int = config.get('max_accounts_games', 0)
MAX_GAMES: int = config.get('max_games', 0)


"""
    MODE
        - 1 -- победа отдается только мафиям
        - 2 -- победа отдается только мирным
        - 3 -- победа отдается в зависимости от роли основного аккаунта
        - 4 -- основной аккаунт всегда будет проигрывать
"""
MODE = int(config.get('mode'))
"""
    FORCE
        - true - победа зависит от основного аккаунта
        - false - победа не зависит от основного аккаунта
"""
"""
    дока сгенерена через чатгпт кста
"""
FORCE = config.get('force')
MAX_PLAYERS = int(config.get('max_players'))
ACCOUNTS = config.get('accounts')[str(MAX_PLAYERS)]
ROLE_ACCOUNTS = config.get('role_accounts', None)
ROLES_FOR_ROLE_ACCOUNTS = config.get('roles_for_role_accounts', None)
MAIN_ACCOUNT_DATA: Union[str, List[str]] = config.get('main')
DISABLED_ROLES: List[int] = []

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

ACTIVE_ROLES = [
    Roles.DOCTOR,
    Roles.SHERIFF,
    Roles.MAFIA,
    Roles.INFORMER,
    Roles.JOURNALIST,
    Roles.BARMAN,
    Roles.TERRORIST
]

ENABLED_ROLES: List[Roles] = [Roles.BARMAN, Roles.SPY,
                              Roles.LOVER, Roles.DOCTOR,
                              Roles.JOURNALIST
                              ]

if MODE == 1 and MAX_PLAYERS < 11:
    ENABLED_ROLES: List[Roles] = [Roles.BARMAN]
elif MODE == 2 and MAX_PLAYERS < 11:
    ENABLED_ROLES: List[Roles] = [Roles.INFORMER]
elif MODE == 1 and MAX_PLAYERS >= 11:
    ENABLED_ROLES: List[Roles] = [Roles.BARMAN, Roles.TERRORIST, Roles.DOCTOR,
                                  Roles.LOVER, Roles.JOURNALIST,
                                  Roles.SPY, Roles.BODYGUARD]
elif MODE == 2 and MAX_PLAYERS >= 11:
    ENABLED_ROLES: List[Roles] = [Roles.INFORMER, Roles.TERRORIST]
elif MODE in {3,4} and MAX_PLAYERS >= 11:
    ENABLED_ROLES: List[Roles] = [Roles.BARMAN, Roles.TERRORIST, Roles.SPY,
                              Roles.LOVER, Roles.DOCTOR,
                              Roles.JOURNALIST, Roles.BODYGUARD
                              ]

DISABLED_ROLES = []

if MAX_PLAYERS == 8:
    for all_roles in Roles:
        if all_roles not in MAFIAS and all_roles not in [Roles.SHERIFF,
                                                         Roles.DOCTOR,
                                                         Roles.LOVER]:
            DISABLED_ROLES.append(all_roles)
elif MAX_PLAYERS == 9 and MODE == 1 and Roles.LOVER in ENABLED_ROLES:
    DISABLED_ROLES = [Roles.SHERIFF]
elif MAX_PLAYERS == 9 and MODE == 1 and Roles.LOVER not in ENABLED_ROLES:
    DISABLED_ROLES = [Roles.CIVILIAN]
elif MAX_PLAYERS == 11 and MODE == 1:
    DISABLED_ROLES = [Roles.BODYGUARD, Roles.SPY,
                      Roles.DOCTOR, Roles.CIVILIAN]
elif MAX_PLAYERS == 12 and MODE == 2:
    DISABLED_ROLES = [Roles.SPY, Roles.BODYGUARD]
    #if Roles.LOVER in ENABLED_ROLES:
    #    DISABLED_ROLES.append(Roles.SHERIFF)

def get_non_vip_titles(is_mafofarm: bool = False):
    config_path = Path('./configs') / 'utils/room_titles.json'
    config_path = config_path.resolve()
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if is_mafofarm:
        mafofarm_titles = data["MAFOFARM_TITLES"]
        return mafofarm_titles
    farm_titles = data["FARM_TITLES"]
    return farm_titles

def get_vip_titles():
    config_path = Path('./configs') / 'utils/vip_titles.json'
    config_path = config_path.resolve()
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # здесь должны были быть песни, но не судьба

    list_1 = data["list_1"]
    list_2 = data["list_2"]
    list_3 = data["list_3"]
    list_4 = data["list_4"]
    list_5 = data["list_5"]
    list_6 = data["list_6"]

    vip_titles = [list_1, list_2, list_3, list_4,
                list_5, list_6]
    random.shuffle(vip_titles)
    return vip_titles

def get_hard_shadow_password():
    return secrets.choice(string.ascii_letters + string.digits)

def get_shadow_password():
    return secrets.choice(string.ascii_lowercase + string.digits)

def get_random_farm_title():
    """Возвращает одно случайное название миро-фарм комнаты."""
    farm_titles = get_non_vip_titles(is_mafofarm = False)
    return secrets.choice(farm_titles)

def get_random_mafofarm_title():
    """Возвращает одно случайное название мафо-фарм комнаты."""
    mafofarm_titles = get_non_vip_titles(is_mafofarm = True)
    return secrets.choice(mafofarm_titles)

def get_vip_farm_title(count):
    vip_titles = get_vip_titles()
    VIP_TITLES = vip_titles
    return vip_titles[0][count], VIP_TITLES


def generate_title(title: str, room_password: str) -> str:
    parentheses_title = f'{title} ({room_password})'
    square_title = f'{title} [{room_password}]'
    curly_title = f'{title} {{{room_password}}}'
    unbracketed_title = f'{title} {room_password}'

    titles = [
        parentheses_title,
        square_title,
        curly_title,
        unbracketed_title
    ]

    return random.choice(titles)
