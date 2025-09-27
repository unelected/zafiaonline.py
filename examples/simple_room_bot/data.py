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

import os

from typing import Optional
from dotenv import load_dotenv

from zafiaonline.structures.enums import Roles
from zafiaonline.structures.enums import MessageStyles


load_dotenv("data.env")
class BotData:
    nickname: str = os.getenv("NICKNAME") or "email"
    password: str = os.getenv("PASSWORD") or "password"

class RoomData:
    # TODO: @unelected - json
    selected_roles: list[Roles | int | None] = []
    title: str = os.getenv("TITLE") or "title"
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
    style: MessageStyles = MessageStyles.NO_COLOR
