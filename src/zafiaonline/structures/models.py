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

"""
Data models used across the Zafia Online game.

This module defines the core structured data types used for player profiles,
rooms, server configuration, chat messages, GUI settings, and more. These
models are built using `msgspec.Struct` for efficient (de)serialization
of network packets and are tied to backend field renaming constants.

Typical usage example:

    from zafiaonline.structures.models import ModelUser, ModelRoom

    user = ModelUser(username="Player123", password="21242424")
    room = ModelRoom(room_id="ru_96180a0e-57bd-4f4f-bf72-3e0978351761", max_players=12)
"""
from msgspec import Struct
from typing import List

from zafiaonline.structures.packet_data_keys import Renaming
from zafiaonline.structures.enums import Sex, Languages, Roles


class ModelUser(Struct, rename = Renaming.USER):
    """
    Represents a user profile in the Zafia Online game.

    This model contains detailed information about a user, such as their
    experience, level, VIP status, game statistics, and authentication token.
    It is used for both client display and backend communication.

    Attributes:
        user_id (str | None): Unique identifier of the user.
        updated (int | None): Timestamp of the last profile update.
        username (str | None): Username of the player.
        photo (int | str | None): Profile photo identifier or URL.
        experience (int | None): Total experience points.
        next_level_experience (int | None): Experience needed for next level.
        previous_level_experience (int | None): Experience required for previous level.
        level (int | None): Current level of the user.
        is_vip (int | None): Whether the user is a VIP (1) or not (0).
        vip_updated (int | None): Timestamp of the last VIP update.
        played_games (int | None): Total number of games played.
        match_making_score (int | None): MMR or matchmaking rating.
        sex (Sex): Gender of the user (default: Sex.MEN).
        player_role_statistics (dict[str, int] | None): Roles played and frequency.
        wins_as_killer (int | None): Number of wins as killer.
        wins_as_mafia (int | None): Number of wins as mafia.
        wins_as_peaceful (int | None): Number of wins as peaceful player.
        token (str | None): Authentication or session token.
        role (int | None): Role ID in the current game, if any.
        online (int | None): Whether the user is online (1) or offline (0).
        selected_language (Languages): Selected game language.
    """
    user_id: str | None = None
    updated: int | None = None
    username: str | None = None
    photo: int | str | None = None
    experience: int | None = None
    next_level_experience: int | None = None
    previous_level_experience: int | None = None
    level: int | None = None
    is_vip: int | None = None
    vip_updated: int | None = None
    played_games: int | None = None
    match_making_score: int | None = None
    sex: Sex = Sex.MEN
    player_role_statistics: dict[str, int] | None = None
    wins_as_killer: int | None = None
    wins_as_mafia: int | None = None
    wins_as_peaceful: int | None = None
    token: str | None = None
    role: int | None = None
    online: int | None = None
    selected_language: Languages = Languages.RUSSIAN


class ModelOtherUser(Struct, rename = Renaming.USER_NEW_API):
    """
    Represents another user's profile in the new API format of Zafia Online.

    This model is used for representing external or public-facing user data,
    typically in API responses where reduced or modified fields are used
    compared to the main `ModelUser` structure.

    Attributes:
        user_id (str | None): Unique identifier of the user.
        updated (int | None): Timestamp of the last profile update.
        username (str | None): Display name of the user.
        photo (str | None): URL or identifier of the profile photo.
        experience (int | None): Accumulated experience points.
        next_level_experience (int | None): Experience required for next level.
        previous_level_experience (int | None): Experience required for previous level.
        level (int | None): Current user level.
        is_vip (bool | None): Whether the user has VIP status.
        played_games (int | None): Total number of games played.
        match_making_score (int | None): Matchmaking rating (MMR).
        sex (Sex): Gender of the user (default: Sex.MEN).
        player_role_statistics (dict[str, int] | None): Mapping of role names to games played.
        wins_as_mafia (int | None): Number of wins while playing as mafia.
        wins_as_peaceful (int | None): Number of wins while playing as peaceful.
        token (str | None): Optional authentication or session token.
        online (bool | None): Online status (True if online).
        selected_language (Languages): Selected language for interface/messages.
        user_account_coins (dict[str, int] | None): Coin balances per currency type.
        decorations (dict | None): Information about visual customizations or cosmetic items.
    """
    user_id: str | None = None
    updated: int | None = None
    username: str | None = None
    photo: str | None = None
    experience: int | None = None
    next_level_experience: int | None = None
    previous_level_experience: int | None = None
    level: int | None = None
    is_vip: bool | None = None
    played_games: int | None = None
    match_making_score: int | None = None
    sex: Sex = Sex.MEN
    player_role_statistics: dict[str, int] | None = None
    wins_as_mafia: int | None = None
    wins_as_peaceful: int | None = None
    token: str | None = None
    online: bool | None = None
    selected_language: Languages = Languages.RUSSIAN
    user_account_coins: dict[str, int] | None = None
    decorations: dict | None = None


class ModelServerConfig(Struct, rename = Renaming.SERVER_CONFIG):
    """
    Configuration model for server-level game settings in Zafia Online.

    This model defines server-side parameters that affect game behavior,
    pricing, and UI visibility for all users.

    Attributes:
        kick_user_price (int | None): Cost to kick a user from a room.
        set_room_password_min_authority (int | None): Minimum authority level required to set a room password.
        price_username_set (int | None): Price to change the user's display name.
        server_language_change_time (int | None): Minimum time between server language changes (in seconds).
        show_password_room_info_button (bool | None): Whether the password visibility toggle is shown in room info.
    """
    kick_user_price: int | None = None
    set_room_password_min_authority: int | None = None
    price_username_set: int | None = None
    server_language_change_time: int| None  = None
    show_password_room_info_button: bool | None = None


class ModelRoom(Struct, rename = Renaming.ROOM):
    """
    Model representing a game room in Zafia Online.

    This structure contains metadata and settings for a multiplayer room
    where players gather before starting a game.

    Attributes:
        room_id (str | None): Unique identifier of the room.
        min_players (int | None): Minimum number of players required to start the game.
        max_players (int | None): Maximum number of players allowed in the room.
        min_level (int | None): Minimum player level required to join the room.
        vip_enabled (bool | None): Whether the room is restricted to VIP players.
        status (int | None): Current status of the room (e.g., waiting, in-game).
        selected_roles (List[Roles] | None): Roles selected to be used in the game.
        title (str | None): User-defined title or name of the room.
        password (str | None): Optional password required to join the room.
    """
    room_id: str | None = None
    min_players: int | None = None
    max_players: int | None = None
    min_level: int | None = None
    vip_enabled: bool | None = None
    status: int | None = None
    selected_roles: List[Roles] | None = None
    title: str | None = None
    password: str | None = None


class ModelShortUser(Struct, rename = Renaming.SHORT_USER):
    """
    Lightweight user model for displaying minimal profile information.

    Used in friend lists, search results, and other areas where full user 
    data is unnecessary.

    Attributes:
        user_id (str | None): Unique identifier of the user.
        username (str | None): Display name of the user.
        updated (int | None): Unix timestamp of the last user data update.
        photo (str | None): URL or ID of the user's avatar image.
        online (int | None): Online status flag (e.g., 1 for online, 0 for offline).
        is_vip (int | None): VIP status flag (1 if VIP, 0 if not).
        vip_updated (int | None): Unix timestamp when VIP status was last updated.
        sex (Sex): User's sex or gender (default is Sex.MEN).
    """
    user_id: str | None = None
    username: str | None = None
    updated: int | None = None
    photo: str | None = None
    online: int | None = None
    is_vip: int | None = None
    vip_updated: int | None = None
    sex: Sex = Sex.MEN


class ModelFriend(Struct, rename = Renaming.FRIEND):
    """
    Model representing a friend relationship and related metadata.

    Used for managing a player's friends list and unread message tracking.

    Attributes:
        friend_id (str | None): Unique identifier of the friend relationship.
        updated (int | None): Unix timestamp of the last update to this relationship.
        user (ModelShortUser | None): Short user model representing the friend.
        new_messages (int | None): Number of unread messages from this friend.
    """
    friend_id: str | None = None
    updated: int | None = None
    user: ModelShortUser | None = None
    new_messages: int | None = None


class ModelMessage(Struct, rename = Renaming.MESSAGE):
    """
    Model representing a chat message exchanged between users.

    Used for storing or transmitting messages in the in-game chat system.

    Attributes:
        user_id (str | None): ID of the user who sent the message.
        friend_id (str | None): ID of the recipient friend.
        created (int | None): Unix timestamp indicating when the message was created.
        text (str | None): Text content of the message.
        message_style (int | None): Style/type indicator for rendering the message (e.g., font, color).
        accepted (int | None): Indicates whether the message was accepted/acknowledged.
        message_type (int | None): Type of message (e.g., system, player, notification).
    """
    user_id: str | None = None
    friend_id: str | None = None
    created: int | None = None
    text: str | None = None
    message_style: int | None = None
    accepted: int | None = None
    message_type: int | None = None


class ModelGUI(Struct, rename = Renaming.GUI):
    """
    Model representing GUI-related configuration and thresholds.

    This structure holds data used by the client to render or enable
    graphical interface elements based on certain authority levels.

    Attributes:
        count_authority_for_swap_icon (dict | None): A mapping of authority levels
            to the number of times a user can swap icons or similar GUI actions.
    """
    count_authority_for_swap_icon: dict | None = None
