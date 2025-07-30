import os

from typing import Optional, List
from dotenv import load_dotenv

from zafiaonline.structures.enums import Roles
from zafiaonline.structures.enums import MessageStyles


load_dotenv("data.env")
class BotData:
    nickname: str = os.getenv("NICKNAME") or "email" 
    password: str = os.getenv("PASSWORD") or "password"

class RoomData:
    # TODO: @unelected - json
    selected_roles: Optional[List[Roles]] = None
    title: str | None = os.getenv("TITLE") or "title"
    max_players: int = int(os.getenv("MAX_PLAYERS") or 31)
    min_players: int = int(os.getenv("MIN_PLAYERS") or 18)
    password: Optional[str] = os.getenv("ROOM_PASSWORD") or None
    min_level: int = int(os.getenv("MIN_LEVEL") or 5)
    vip_enabled: bool = bool(os.getenv("VIP_ENABLED") or False)
    quantity_players_for_leave: int = int(os.getenv("QUANTITY_PLAYERS_FOR_LEAVE") or 3) # ENG: the number of players to be subtracted from ‘min_players’ and at this number of players the room will be reset
                                                                                        # RU: количество игроков которое будет отниматься от ‘min_players’ и при этом количестве игроков будет сбрасываться комната

class MutedPlayersData:
    # TODO: @unelected - json
    muted_list: list[str] = [
        #"nickaname",
    ]

class MessageStyleData:
    # TODO: @unelected - json
    style: Optional[MessageStyles] = None
