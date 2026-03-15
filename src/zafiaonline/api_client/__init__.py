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

from zafiaonline.api_client.api_decorators import ApiDecorators
from zafiaonline.api_client.global_chat_methods import GlobalChatMethods
from zafiaonline.api_client.player_methods import PlayersMethods
from zafiaonline.api_client.room_methods import RoomMethods, MatchMakingMethods
from zafiaonline.api_client.user_methods import AuthService, UserMethods
from zafiaonline.api_client.https_api.https_api import HttpsApiMethods

__all__: tuple[str, ...] = (
    # Decorators
    "ApiDecorators",
    # Chat
    "GlobalChatMethods",
    # Players
    "PlayersMethods",
    "AuthService",
    "UserMethods",
    # RoomType
    "RoomMethods",
    "MatchMakingMethods",
    # HttpTraffic
    "HttpsApiMethods",
)
