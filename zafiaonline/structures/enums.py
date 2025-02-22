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
    WOMEN = 0
    MEN = 1

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
        UNKNOWN (int): Default value when the role is not assigned (0).
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
    UNKNOWN = 0       # Role not assigned
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

from enum import Enum

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



from enum import Enum

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



from enum import IntEnum

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

class ProfilePhotoType(IntEnum):
    """
    Enumeration representing the profile photo status of a user.

    This enum is used to determine whether a user has uploaded a profile photo.

    Attributes:
        NO_PHOTO (int): The user has not uploaded a profile photo (value = 0).
        PHOTO_ADDED (int): The user has uploaded a profile photo (value = 1).

    Usage example:
        >>> photo_status = ProfilePhotoType.PHOTO_ADDED
        >>> print(photo_status)
        ProfilePhotoType.PHOTO_ADDED
        >>> print(photo_status.value)
        1
    """
    NO_PHOTO = 0      # No profile photo uploaded
    PHOTO_ADDED = 1   # Profile photo has been added



from enum import IntEnum

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



