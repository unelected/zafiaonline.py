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

from zafiaonline.structures.packet_data_keys import PacketDataKeys, HttpsApiKeys, ZafiaApiKeys, Endpoints, ZafiaEndpoints, Renaming
from zafiaonline.structures.enums import (
    Sex, Roles, Languages, RatingMode, RatingType,
    ActivityType, RoomModelType, FriendInRoomType, ProfilePhotoType,
    MessageType, MessageStyles, MafiaLanguages, MethodGetFavourites
)
from zafiaonline.structures.models import (
    ModelUser, ModelOtherUser, ModelServerConfig, ModelRoom,
    ModelShortUser, ModelFriend, ModelMessage, ModelGUI
)

__all__: tuple[str, ...] = (
    # Constants
    "PacketDataKeys",
    "HttpsApiKeys",
    "ZafiaApiKeys",
    "Endpoints",
    "ZafiaEndpoints",
    "Renaming",

    # Enums
    "Sex",
    "Languages",
    "Roles",
    "RatingMode",
    "RatingType",
    "ActivityType",
    "RoomModelType",
    "ProfilePhotoType",
    "FriendInRoomType",
    "MessageType",
    "MessageStyles",
    "MafiaLanguages",
    "MethodGetFavourites",

    # Models
    "ModelUser",
    "ModelOtherUser",
    "ModelServerConfig",
    "ModelRoom",
    "ModelShortUser",
    "ModelFriend",
    "ModelMessage",
    "ModelGUI",
)
