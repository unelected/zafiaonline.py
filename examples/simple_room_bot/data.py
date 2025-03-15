from typing import Optional, List

from zafiaonline.structures.enums import Roles
from zafiaonline.structures.enums import MessageStyles


class BotData:
    nickname = "nickname"
    password = "password"

class RoomData:
    selected_roles: Optional[List[Roles]] = None
    title: str = "title"
    max_players: int = 21
    min_players: int = 18
    password: Optional[str] = None
    min_level: int = 5
    vip_enabled: bool = False

    quantity_players_for_leave: int = 3 # ENG: the number of players to be subtracted from ‘min_players’ and at this number of players the room will be reset
                                        # RU: количество игроков которое будет отниматься от ‘min_players’ и при этом количестве игроков будет сбрасываться комната

class MutedPlayersData:
    muted_list = [
        #"nickaname",
    ]

class MessageStyleData:
    style = MessageStyles.NO_COLOR