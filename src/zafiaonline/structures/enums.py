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
Enumerations for the Mafia game server.

This module defines various enums used throughout the Mafia game backend.
These enums represent things like player roles, user settings, game events,
chat message types, and rating systems.

Typical usage example:

    from mafia.enums import Roles, RatingMode

    if user.role == Roles.SHERIFF:
        investigate(user)

    if leaderboard.mode == RatingMode.TODAY:
        print(f"Today's rating is {leaderboard}")
"""
from enum import IntEnum, Enum


class Sex(IntEnum):
    """
    Enumeration representing the biological sex of a user.

    Attributes:
        MEN: Represents a male user (value = 0).
        WOMEN: Represents a female user (value = 1).
    """
    MEN = 0
    WOMEN = 1


class Languages(str, Enum):
    """
    Enumeration representing supported languages.

    Attributes:
        UNSELECTED: Default value when no language is selected (value = "").
        RUSSIAN: Represents the Russian language (value = "ru").
        ENGLISH: Represents the English language (value = "en").
    """
    UNSELECTED = ""
    RUSSIAN = "ru"
    ENGLISH = "en"


class Roles(IntEnum):
    """
    Enumeration representing different roles in the game.

    Each role has a unique integer identifier, defining a player's function
    or abilities within the game.

    Attributes:
        CIVILIAN: A regular player with no special abilities (1).
        DOCTOR: Can heal other players to protect them from elimination (2).
        SHERIFF: Can investigate other players to determine their roles (3).
        MAFIA: Works with the mafia team to eliminate civilians (4).
        LOVER: Forms a bond with another player; their fate is linked (5).
        TERRORIST: Can sacrifice themselves to eliminate another player (6).
        JOURNALIST: Can reveal a player's role to the public (7).
        BODYGUARD: Protects a chosen player from attacks (8).
        BARMAN: Can disable another player’s abilities for a turn (9).
        SPY: Can gather information about other players’ actions (10).
        INFORMER: Can manipulate information or provide false leads (11).
    """
    CIVILIAN = 1
    DOCTOR = 2
    SHERIFF = 3
    MAFIA = 4
    LOVER = 5
    TERRORIST = 6
    JOURNALIST = 7
    BODYGUARD = 8
    BARMAN = 9
    SPY = 10
    INFORMER = 11


class RatingMode(str, Enum):
    """
    Enumeration representing different rating modes for leaderboard rankings.

    This enum defines the time frame for which player ratings are calculated
    and displayed on the leaderboard.

    Attributes:
        ALL_TIME: Rankings based on all-time performance.
        TODAY: Rankings based on performance for the current day.
        YESTERDAY: Rankings based on performance for the previous day.
    """
    ALL_TIME = "all_time"
    TODAY = "today"
    YESTERDAY = "yesterday"


class RatingType(str, Enum):
    """
    Enumeration representing different types of rating categories for player rankings.

    This enum defines the various metrics used to rank players in leaderboards.

    Attributes:
        GAMES: Ranking based on the total number of games played.
        EXPERIENCE: Ranking based on the player's accumulated experience points.
        AUTHORITY: Ranking based on the player's authority level.
        WINS: Ranking based on the total number of wins achieved.
    """
    GAMES = "games"
    EXPERIENCE = "experience"
    AUTHORITY = "authority"
    WINS = "wins"


class ActivityType(IntEnum):
    """
    Enumeration representing the activity status of a user.

    This enum is used to indicate whether a user is currently online or offline.

    Attributes:
        OFFLINE: Represents a user who is not currently active.
        ONLINE: Represents a user who is currently active and online.
    """
    OFFLINE = 0
    ONLINE = 1


class RoomModelType(IntEnum):
    """
    Enumeration representing different types of room models in the game.

    This enum is used to distinguish between standard rooms and
    matchmaking-enabled rooms.

    Attributes:
        NOT_MATCHMAKING_MODE: Represents a regular game room without matchmaking.
        MATCHMAKING_MODE: Represents a room that uses a matchmaking system to pair players.
    """
    NOT_MATCHMAKING_MODE = 0
    MATCHMAKING_MODE = 1


class ProfilePhotoType(str, Enum):
    """
    Enumeration representing the profile photo status of a user.

    This enum is used to determine whether a user has uploaded a profile photo.

    Attributes:
        NO_PHOTO: The user has not uploaded a profile photo.
        PHOTO_ADDED: The user has uploaded a profile photo.
    """
    NO_PHOTO = "0"
    PHOTO_ADDED = "1"


class FriendInRoomType(IntEnum):
    """
    Enumeration representing the presence of a friend in a room.

    This enum is used to indicate whether a user's friend is currently in
    the same room.

    Attributes:
        NO_FRIEND_IN_ROOM: No friends are present in the room.
        FRIEND_IN_ROOM: At least one friend is present in the room.
    """
    NO_FRIEND_IN_ROOM = 0
    FRIEND_IN_ROOM = 1


class MessageType(IntEnum):
    """
    Enumeration of message types for the Mafia game chat.

    Message types define the structure, color, and context of chat messages
    used during gameplay.

    Attributes:
        MAIN_TEXT: General game message.
        USER_HAS_ENTERED: A user has entered the room.
        USER_HAS_LEFT: A user has left the room.
        GAME_HAS_STARTED: Game start notification.
        NIGHT_COME_MAFIA_IN_CHAT: Night phase begins, mafia chat opens.
        NIGHT_MAFIA_CHOOSE_VICTIM: Mafia selects a victim.
        DAY_COME_EVERYONE_IN_CHAT: Day phase begins, all players chat.
        DAY_CIVILIANS_VOTING: Civilians begin voting.
        VOTES_FOR: A vote has been cast.
        MAIN_TEXT10: Duplicate main text (unused).
        KILLED_PLAYER_MESSAGE: Message about a killed player.
        PLAYER_KILLED: Announcement of player killed.
        VOTES_FOR13: Duplicate voting message (unused).
        NOBODY_KILLED: No player was killed.
        GAME_FINISHED_CIVILIANS_WON: Game end, civilians win.
        GAME_FINISHED_MAFIA_WON: Game end, mafia win.
        KILLED_USER_MESSAGE: User has been killed.
        TERRORIST_BOMBED: Terrorist has exploded.
        BREAKING_NEWS_PLAYING_THE_SAME_TEAM: Breaking news, same team.
        BREAKING_NEWS_PLAYING_DIFFERENT_TEAMS: Breaking news, different teams.
        TERRORIST_BOMBED_USER_WAS_UNDER_GUARDIAN: Bomb blocked by guardian.
        GAME_FINISHED_IN_DRAW: Game ended in a draw.
        STARTED_VOTING_TO_KICK_USER: Kick vote initiated.
        KICK_VOTING_HAS_FINISHED: Kick vote concluded.
        MAIN_TEXT25: Duplicate main text (unused).
        VOTES_FOR26: Duplicate voting message (unused).
        GIVE_UP: Player has surrendered.
    """
    MAIN_TEXT = 1
    USER_HAS_ENTERED = 2
    USER_HAS_LEFT = 3
    GAME_HAS_STARTED = 4
    NIGHT_COME_MAFIA_IN_CHAT = 5
    NIGHT_MAFIA_CHOOSE_VICTIM = 6
    DAY_COME_EVERYONE_IN_CHAT = 7
    DAY_CIVILIANS_VOTING = 8
    VOTES_FOR = 9
    MAIN_TEXT10 = 10
    KILLED_PLAYER_MESSAGE = 11
    PLAYER_KILLED = 12
    VOTES_FOR13 = 13
    NOBODY_KILLED = 14
    GAME_FINISHED_CIVILIANS_WON = 15
    GAME_FINISHED_MAFIA_WON = 16
    KILLED_USER_MESSAGE = 17
    TERRORIST_BOMBED = 18
    BREAKING_NEWS_PLAYING_THE_SAME_TEAM = 19
    BREAKING_NEWS_PLAYING_DIFFERENT_TEAMS = 20
    TERRORIST_BOMBED_USER_WAS_UNDER_GUARDIAN = 21
    GAME_FINISHED_IN_DRAW = 22
    STARTED_VOTING_TO_KICK_USER = 23
    KICK_VOTING_HAS_FINISHED = 24
    MAIN_TEXT25 = 25
    VOTES_FOR26 = 26
    GIVE_UP = 27


class MessageStyles(IntEnum):
    """
    Enumeration of color styles for chat messages in the Mafia game.

    These styles define the appearance of chat messages based on their type.
    Values correspond to predefined color codes in the game’s client UI.

    Attributes:
        NO_COLOR: No color applied.
        GREY_COLOR: Grey color style.
        BLUE_COLOR: Blue color style.
        RED_COLOR: Red color style.
        GREEN_COLOR: Green color style.
        PURPLE_COLOR: Purple color style.
        YELLOW_COLOR: Yellow color style.
        PINK_COLOR: Pink color style.
    """
    NO_COLOR = 0
    GREY_COLOR = 1
    BLUE_COLOR = 2
    RED_COLOR = 3
    GREEN_COLOR = 4
    PURPLE_COLOR = 5
    YELLOW_COLOR = 6
    PINK_COLOR = 7


class MafiaLanguages(str, Enum):
    """
    Enumeration of supported language codes in the Mafia game.

    These codes are used for localizing game content and messages.

    Attributes:
        Russian: Russian language.
        English: English language.
    """
    Russian = "RUS"
    English = "ENG"


class MethodGetFavourites(IntEnum):
    """
    Enumeration for methods of retrieving favourite players in the Mafia game.

    Used to specify the source of a player's favourites when making a request.

    Attributes:
        FriendMethod: Retrieve favourites from the friend list.
        InviteMethod: Retrieve favourites from the invite list.
    """
    FriendMethod = 0
    InviteMethod = 1
