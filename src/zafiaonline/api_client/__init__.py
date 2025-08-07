# Copyright (C) 2025 unelected
#
# This file is part of the zafiaonline project.
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU Lesser General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>.

from zafiaonline.api_client.api_decorators import ApiDecorators
from zafiaonline.api_client.global_chat_methods import GlobalChat
from zafiaonline.api_client.player_methods import Players
from zafiaonline.api_client.room_methods import Room, MatchMaking
from zafiaonline.api_client.user_methods import Auth, User
from zafiaonline.api_client.https_api import HttpsApi
from zafiaonline.api_client.zafia_api import ZafiaApi

__all__: tuple[str, ...] = (
    #Decorators
    "ApiDecorators",

    #Chat
    "GlobalChat",

    #Players
    "Players",
    "Auth",
    "User",

    #Room
    "Room",
    "MatchMaking",

    #Other
    "HttpsApi",
    "ZafiaApi",
)
