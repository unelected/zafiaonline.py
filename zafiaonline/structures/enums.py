from enum import IntEnum, Enum

class Sex(IntEnum):
    WOMEN = 0
    MEN = 1


class Languages(str, Enum):
    UNSELECTED = ""
    RUSSIAN = "ru"
    ENGLISH = "en"


class Roles(IntEnum):
    UNKNOWN = 0
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
    ALL_TIME = "all_time"
    TODAY = "today"
    YESTERDAY = "yesterday"


class RatingType(str, Enum):
    GAMES = "games"
    EXPERIENCE = "experience"
    AUTHORITY = "authority"
    WINS = "wins"


class ActivityType(IntEnum):
    OFFLINE = 0
    ONLINE = 1


class RoomModelType(IntEnum):
    NOT_MATCHMAKING_MODE = 0
    MATCHMAKING_MODE = 1


class ProfilePhotoType(IntEnum):
    NO_PHOTO = 0
    PHOTO_ADDED = 1


class FriendInRoomType(IntEnum):
    NO_FRIEND_IN_ROOM = 0
    FRIEND_IN_ROOM = 1


