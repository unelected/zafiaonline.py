from enum import IntEnum, Enum

class Sex(IntEnum):
    """
        Enumeration representing the biological sex of a user.

        Attributes:
            WOMEN (int): Represents a female user, assigned the value `0`.
            MEN (int): Represents a male user, assigned the value `1`.

        Usage example:
            >>> user_sex = Sex.WOMEN
            >>> print(user_sex)
            Sex.WOMEN
            >>> print(user_sex.value)
            0
        """
    MEN = 0
    WOMEN = 1

class Languages(str, Enum):
    """
    Enumeration representing supported languages.

    Attributes:
        UNSELECTED (str): Default value when no language is selected,
        represented as an empty string (`""`).
        RUSSIAN (str): Represents the Russian language, using the code `"ru"`.
        ENGLISH (str): Represents the English language, using the code `"en"`.

    Usage example:
        >>> user_language = Languages.RUSSIAN
        >>> print(user_language)
        Languages.RUSSIAN
        >>> print(user_language.value)
        'ru'
    """
    UNSELECTED = ""  # No language selected
    RUSSIAN = "ru"   # Russian language
    ENGLISH = "en"   # English language

class Roles(IntEnum):
    """
    Enumeration representing different roles in the game.

    Each role has a unique integer identifier, which is used to define
    a player's function or abilities within the game.

    Attributes:
        CIVILIAN (int): A regular player with no special abilities (1).
        DOCTOR (int): Can heal other players to protect them from
        "elimination" (2).
        SHERIFF (int): Can investigate other players to determine their
        "roles" (3).
        MAFIA (int): Works with the mafia team to eliminate civilians (4).
        LOVER (int): Forms a bond with another player; their fate is linked
        (5).
        TERRORIST (int): Can sacrifice themselves to eliminate another
        "player" (6).
        JOURNALIST (int): Can reveal a player's role to the public (7).
        BODYGUARD (int): Protects a chosen player from attacks (8).
        BARMAN (int): Can disable another player’s abilities for a turn (9).
        SPY (int): Can gather information about other players’ actions (10).
        INFORMER (int): Can manipulate information or provide false leads (11).

    Usage example:
        >>> player_role = Roles.SHERIFF
        >>> print(player_role)
        Roles.SHERIFF
        >>> print(player_role.value)
        3
    """
    CIVILIAN = 1      # Regular player with no special abilities
    DOCTOR = 2        # Can heal players
    SHERIFF = 3       # Can investigate roles
    MAFIA = 4         # Part of the mafia team
    LOVER = 5         # Forms a linked bond with another player
    TERRORIST = 6     # Can sacrifice themselves for an attack
    JOURNALIST = 7    # Reveals player roles
    BODYGUARD = 8     # Protects a chosen player
    BARMAN = 9        # Disables player abilities for a turn
    SPY = 10          # Gathers information about players
    INFORMER = 11     # Manipulates information or misleads

class RatingMode(str, Enum):
    """
    Enumeration representing different rating modes for leaderboard rankings.

    This enum defines the time frame for which player ratings are calculated
    and displayed on the leaderboard.

    Attributes:
        ALL_TIME (str): Displays rankings based on all-time performance.
        TODAY (str): Displays rankings based on performance for the current
        day.
        YESTERDAY (str): Displays rankings based on performance for the
        previous day.

    Usage example:
        >>> current_mode = RatingMode.TODAY
        >>> print(current_mode)
        RatingMode.TODAY
        >>> print(current_mode.value)
        'today'
    """
    ALL_TIME = "all_time"   # Leaderboard for all-time rankings
    TODAY = "today"         # Leaderboard for today's performance
    YESTERDAY = "yesterday" # Leaderboard for yesterday's performance

class RatingType(str, Enum):
    """
    Enumeration representing different types of rating categories for
    player rankings.

    This enum defines the various metrics used to rank players in leaderboards.

    Attributes:
        GAMES (str): Ranking based on the total number of games played.
        EXPERIENCE (str): Ranking based on the player's accumulated
        experience points.
        AUTHORITY (str): Ranking based on the player's authority level.
        WINS (str): Ranking based on the total number of wins achieved.

    Usage example:
        >>> rating_category = RatingType.EXPERIENCE
        >>> print(rating_category)
        RatingType.EXPERIENCE
        >>> print(rating_category.value)
        'experience'
    """
    GAMES = "games"         # Rank based on the number of games played
    EXPERIENCE = "experience" # Rank based on total experience points
    AUTHORITY = "authority" # Rank based on authority level
    WINS = "wins"           # Rank based on total wins

class ActivityType(IntEnum):
    """
    Enumeration representing the activity status of a user.

    This enum is used to indicate whether a user is currently online or
    offline.

    Attributes:
        OFFLINE (int): Represents a user who is not currently active (value
        = 0).
        ONLINE (int): Represents a user who is currently active and online (
        value = 1).

    Usage example:
        >>> status = ActivityType.ONLINE
        >>> print(status)
        ActivityType.ONLINE
        >>> print(status.value)
        1
    """
    OFFLINE = 0  # User is not active
    ONLINE = 1   # User is currently online

class RoomModelType(IntEnum):
    """
    Enumeration representing different types of room models in the game.

    This enum is used to distinguish between standard rooms and
    matchmaking-enabled rooms.

    Attributes:
        NOT_MATCHMAKING_MODE (int): Represents a regular game room without
        "matchmaking" (value = 0).
        MATCHMAKING_MODE (int): Represents a room that uses a matchmaking
        system to pair players (value = 1).

    Usage example:
        >>> room_type = RoomModelType.MATCHMAKING_MODE
        >>> print(room_type)
        RoomModelType.MATCHMAKING_MODE
        >>> print(room_type.value)
        1
    """
    NOT_MATCHMAKING_MODE = 0  # Regular room without matchmaking
    MATCHMAKING_MODE = 1      # Room with matchmaking enabled

class ProfilePhotoType(int, Enum):
    """
    Enumeration representing the profile photo status of a user.

    This enum is used to determine whether a user has uploaded a profile photo.

    Attributes:
        NO_PHOTO (int): The user has not uploaded a profile photo (value = "").
        PHOTO_ADDED (int): The user has uploaded a profile photo (value = 1).

    Usage example:
        >>> photo_status = ProfilePhotoType.PHOTO_ADDED
        >>> print(photo_status)
        ProfilePhotoType.PHOTO_ADDED
        >>> print(photo_status.value)
        1
    """
    NO_PHOTO = "0"      # No profile photo uploaded
    PHOTO_ADDED = "1"   # Profile photo has been added

class FriendInRoomType(IntEnum):
    """
    Enumeration representing the presence of a friend in a room.

    This enum is used to indicate whether a user's friend is currently in
    the same room.

    Attributes:
        NO_FRIEND_IN_ROOM (int): No friends are present in the room
        (value = 0).
        FRIEND_IN_ROOM (int): At least one friend is present in the room (
        value = 1).

    Usage example:
        >>> friend_status = FriendInRoomType.FRIEND_IN_ROOM
        >>> print(friend_status)
        FriendInRoomType.FRIEND_IN_ROOM
        >>> print(friend_status.value)
        1
    """
    NO_FRIEND_IN_ROOM = 0  # No friends present in the room
    FRIEND_IN_ROOM = 1     # At least one friend is in the room

class MessageType(IntEnum):
    """
    A class containing message type constants for the Mafia game chat.

    Message Types:
        MAIN_TEXT: 1 — "%s", color: main_text (dark in mafia, white in zafia)
        USER_HAS_ENTERED: 2 — "%s %s %s", color: green
        USER_HAS_LEFT: 3 — "%s %s %s", color: red
        GAME_HAS_STARTED: 4 — "%s", color: main_text
        NIGHT_COME_MAFIA_IN_CHAT: 5 — "%s", color: blue
        NIGHT_MAFIA_CHOOSE_VICTIM: 6 — "%s", color: blue
        DAY_COME_EVERYONE_IN_CHAT: 7 — "%s", color: orange
        DAY_CIVILIANS_VOTING: 8 — "%s", color: orange
        VOTES_FOR: 9 — "%s [%s]", color: green
        MAIN_TEXT10: 10 — "%s", color: main_text, useless
        KILLED_PLAYER_MESSAGE: 11 — "%s", color: gray
        PLAYER_KILLED: 12 — "%s [%s] %s", color: red
        VOTES_FOR13: 13 — "%s [%s]", color: green, useless
        NOBODY_KILLED: 14 — "%s", color: green
        GAME_FINISHED_CIVILIANS_WON: 15 — "%s", color: green
        GAME_FINISHED_MAFIA_WON: 16 — "%s", color: green
        KILLED_USER_MESSAGE: 17 — "%s", color: gray (#ff6d6a96)
        TERRORIST_BOMBED: 18 — "%s [%s]", color: red
        BREAKING_NEWS_PLAYING_THE_SAME_TEAM: 19 — split("[#][=][#]"), "%s [%s] %s [%s] %s", color: red
        BREAKING_NEWS_PLAYING_DIFFERENT_TEAMS: 20 — split("[#][=][#]"), "%s [%s] %s [%s] %s", color: red
        TERRORIST_BOMBED_USER_WAS_UNDER_GUARDIAN: 21 — "%s [%s], %s" "%s", color: red
        GAME_FINISHED_IN_DRAW: 22 — "%s", color: green
        STARTED_VOTING_TO_KICK_USER: 23 — split("[#][=][#]"), "[%s] %s [%s] %s", color: blue
            First part is the nickname of the initiator, second is the target.
        KICK_VOTING_HAS_FINISHED: 24 — split("[|]"), "%s\n%s:\n%s: %s\n%s: %s", color: blue
        MAIN_TEXT25: 25 — "%s", color: main_text, useless
        VOTES_FOR26: 26 — "%s [%s]", color: green, useless
        GIVE_UP: 27 — "%s", color: red

    Notes:
        Format strings are indicated in comments for each message type.
        The color defines how the message should appear in the game interface.
        Do not modify the numeric values as they are fixed by the external API.
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
    Enum for message color styles used in the Mafia game chat.

    Values:
        NO_COLOR (int): 0 — No color applied.
        GREY_COLOR (int): 1 — Grey color style.
        BLUE_COLOR (int): 2 — Blue color style.
        RED_COLOR (int): 3 — Red color style.
        GREEN_COLOR (int): 4 — Green color style.
        PURPLE_COLOR (int): 5 — Purple color style.
        YELLOW_COLOR (int): 6 — Yellow color style.
        PINK_COLOR (int): 7 — Pink color style.

    Notes:
        These styles define the appearance of chat messages based on their type.
        Values correspond to predefined color codes in the game’s client UI.
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
    Enum for supported language codes in the Mafia game.

    Values:
        Russian (str): "RUS" — Russian language.
        English (str): "ENG" — English language.

    Notes:
        These codes are used for localizing game content and messages.
    """
    Russian = "RUS"
    English = "ENG"

class MethodGetFavourites(IntEnum):
    """
    Enum for methods of retrieving favourite players in the Mafia game.

    Values:
        FriendMethod (int): 0 — Retrieve favourites from the friend list.
        InviteMethod (int): 1 — Retrieve favourites from the invite list.

    Notes:
        Used to specify the source of a player's favourites when making a request.
    """
    FriendMethod = 0
    InviteMethod = 1
