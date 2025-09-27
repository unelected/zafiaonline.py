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

from typing import Any

from zafiaonline.api_client.user_methods import UserMethods, AuthService
from zafiaonline.api_client.player_methods import PlayersMethods
from zafiaonline.api_client.global_chat_methods import GlobalChatMethods
from zafiaonline.api_client.room_methods import RoomMethods, MatchMakingMethods
from zafiaonline.api_client.https_api import HttpsApiMethods
from zafiaonline.api_client.zafia_api import ZafiaApiMethods


class Client:
    auth: AuthService
    user: UserMethods
    players: PlayersMethods
    global_chat: GlobalChatMethods
    room: RoomMethods
    matchmaking: MatchMakingMethods
    https: HttpsApiMethods
    zafia: ZafiaApiMethods

    def __init__(self, proxy: str | None = None) -> None: ...
    def __getattr__(self, name: str) -> object: ...
    def _import_submodule(
        self,
        attr: str,
        module_name: str,
        class_name: str,
        *args: Any,
        **kwargs: Any
    ) -> object: ...
