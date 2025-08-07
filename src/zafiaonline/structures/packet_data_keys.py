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
Enums and renaming dictionaries for networking and API communication.

This module contains enum classes and key renaming mappings used for encoding
and decoding messages between clients and servers in Mafia Online and Zafia Online.

Typical usage example:

    from mafia.enums_and_keys import PacketDataKeys, Renaming

    value = PacketDataKeys.USERNAME
    renamed_dict = rename_payload(data, rename_map=Renaming.USER)
"""
from enum import Enum
from typing import Any


class PacketDataKeys(str, Enum):
    """
    Enumeration of packet data keys for client-server communication.

    This class defines short string identifiers used in network packets
    exchanged between client and server. These compact keys help reduce
    payload size and improve communication efficiency.

    Each enum member maps a semantic constant name to a short code, often
    a single letter or abbreviation, which identifies a specific action,
    status, user attribute, or system message in the protocol.
    """
    ACCEPTED = "a"
    ACCEPT_MESSAGES = "ac"
    ACTIVE = "ac"
    ACTIVITY = "ac"
    ADD_CLIENT_TO_CHAT = "acc"
    ADD_CLIENT_TO_DASHBOARD = "acd"
    ADD_CLIENT_TO_FRIENDSHIP_LIST = "acfl"
    ADD_CLIENT_TO_PRIVATE_CHAT = "acpc"
    ADD_CLIENT_TO_ROOMS_LIST = "acrl"
    ADD_FRIEND = "af"
    ADD = "add"
    ADD_PLAYER = "ap"
    ADMIN_BLOCK_USER = "abu"
    ADMIN_CONTROL_USER = "acu"
    ADMIN = "adm"
    ADMIN_KICK_USER = "aku"
    ADMIN_UNBLOCK_USER = "auu"
    AFFECTED_BY_ROLES = "abr"
    ALIVE = "a"
    APP_LANGUAGE = "alc"
    ASPIRIN = "a"
    BACKPACK = "bp"
    BILLING_APP_PACKAGE = "bapckg"
    BILLING_PRODUCT_ID = "bpid"
    BILLING_PURCHASE_PENDING = "bppndng"
    BILLING_PURCHASE_TOKEN = "bptkn"
    BLOCKED_USERS = "bus"
    BLOCK_DEVICE = "bdv"
    BLOCK_IP = "bi"
    BONUSES_ENABLED = "bns"
    BONUS_PRICE = "bp"
    BRIBE = "b"
    BUY_BILLING_MARKET_ITEM = "mrktgg"
    BUY_BILLING_MARKET_SUCCESS_ITEM = "bbmrktis"
    BUY_MARKET_ITEM = "bmrkti"
    BUY_MARKET_ITEM_SUCCESS = "bmrktis"
    CHAT_MESSAGE_CREATE = "cmc"
    CHECK_PLAYER_IS_IN_ROOM = "cpir"
    CIVILIAN_ALIVE = "c"
    CIVILIAN_ALL = "ca"
    CLEAN_VOTES_HISTORY = "cv"
    CLOUD_MESSAGING_TOKEN_IS_SAVED = "cmts"
    COMPLAINTS = "cmps"
    COMPLAINT = "cmp"
    CONDOM = "cm"
    CONFESSION = "cn"
    CONNECTION_CHECKER_PERIOD = "ccp"
    CONNECTION_INACTIVE_TIMEOUT = "cit"
    CREATED = "c"
    CREATE_PLAYER = "cp"
    CREATOR_BLOCKED = "crb"
    DATA = "data"
    DAYTIME = "d"
    DESCRIPTION = "dsc"
    DEVICE_ID = "d"
    EMAIL = "e"
    EMAIL_NOT_VERIFIED = "env"
    EMAIL_NOT_VERIFIED_MESSAGE_CREATE_TIMEOUT = "envmct"
    ERROR_FLOOD_DETECTED = "erfd"
    ERROR = "e"
    ERROR_OCCUR = "ero"
    EXPERIENCE = "ex"
    FILE = "f"
    FIRST_AID_KIT = "f"
    FIRST_NAME = "fn"
    FRIENDSHIP_FLAG = "fpf"
    FRIENDSHIP = "fp"
    FRIENDSHIP_LIST = "frl"
    FRIENDSHIP_LIST_LIMIT = "fll"
    FRIENDSHIP_LIST_LIMIT_FOR_VIP = "fllfv"
    FRIENDSHIP_REQUESTS = "fr"
    FRIENDS_IN_INVITE_LIST = "fiil"
    FRIEND_IN_ROOM = "fir"
    FRIEND_IS_INVITED = "fiinvtd"
    FRIEND = "ff"
    FRIEND_USER_OBJECT_ID = "f"
    GAME_DAYTIME = "gd"
    GAME_FINISHED = "gf"
    GAME_STARTED = "gsd"
    GAME_STATUS_IN_ROOMS_LIST = "gsrl"
    GAME_STATUS = "gs"
    GET_BLOCKED_USERS = "gbus"
    GET_COMPLAINTS = "gcmps"
    GET_FRIENDS_IN_INVITE_LIST = "gfiil"
    GET_PLAYERS = "gp"
    GET_RATING = "gr"
    GET_SENT_FRIEND_REQUESTS_LIST = "gsfrl"
    GET_USER_PROFILE = "gup"
    GET_MATCH_MAKING_USERS_IN_QUEUE_INTERVAL = "mmguiabk"
    GIVE_UP = "agu"
    GIFT_MARKET_ITEMS = "gmrkti"
    GOLD = "g"
    GOOGLE_SIGN_IN = "gsin"
    GOOGLE_TOKEN = "gt"
    GOOGLE_USER_ID = "gui"
    HIS_FRIENDSHIP_LIST_FULL = "hflf"
    INFO_MESSAGE = "imsg"
    INVITATION_SENDER_USERNAME = "isun"
    IP_ADDRESS = "ip"
    IS_BILLING_ITEM = "ibi"
    IS_DAY_ACTION_USED = "idau"
    IS_INVITED = "iinvtd"
    IS_NIGHT_ACTION_ALTERNATIVE = "inaa"
    IS_NIGHT_ACTION_USED = "inau"
    IS_ONLINE = "on"
    ITEM_PRICE_TEXT = "iprct"
    KICK_TIMER = "kt"
    KICK_USER_AUTHORITY_LESS_THAN_USER = "kualtu"
    KICK_USER_GAME_STARTED = "kugs"
    KICK_USER = "ku"
    KICK_USER_NOT_IN_ROOM = "kunir"
    KICK_USER_OBJECT_ID = "k"
    KICK_USER_PRICE = "kup"
    KICK_USER_RANK = "kur"
    KICK_USER_STARTED = "kus"
    KICK_USER_VOTE = "kuv"
    LAST_NAME = "ln"
    LEVEL = "l"
    LIE_DETECTOR = "l"
    MAFIA_ALIVE = "m"
    MAFIA_ALL = "ma"
    MAKE_COMPLAINT = "mc"
    MATCH_MAKING_MATCH_STATUS = "mmms"
    MATCH_MAKING_BASE_PLAYERS_AMOUNT = "mmbpa"
    MATCH_MAKING_GET_STATUS = "mmgsk"
    MATH_MAKING_ADD_USER = "mmauk"
    MARKET_ITEMS = "mrkti"
    MAXIMUM_PLAYERS = "mxmp"
    MAX_PLAYERS = "mxp"
    MESSAGES = "ms"
    MESSAGE = "m"
    MESSAGE_STYLE = "mstl"
    MESSAGE_TYPE = "t"
    MESSAGE_STICKER = "mstk"
    MIN_LEVEL = "mnl"
    MIN_PLAYERS = "mnp"
    MONEY = "mo"
    NEW_CLOUD_MESSAGING_TOKEN = "ncmt"
    NEW_MESSAGES = "nm"
    NEXT_LEVEL_EXPERIENCE = "nle"
    NOT_ENOUGH_AUTHORITY_ERROR = "neae"
    NO_CHANGES = "noch"
    NUM = "n"
    NUM_MAFIA = "m"
    NUM_PLAYERS = "p"
    OBJECT_ID = "o"
    PASSWORD = "pw"
    PHOTO = "ph"
    PLAYED_GAMES = "pg"
    PLAYERS_IN_ROOM = "pin"
    PLAYERS = "pls"
    PLAYERS_NUM = "pn"
    PLAYERS_STAT = "ps"
    PLAYER = "p"
    PLAYER_ROLE_STATISTICS = "prst"
    PREVIOUS_LEVEL_EXPERIENCE = "ple"
    PRICE_USERNAME_SET = "pus"
    PRIVATE_CHAT_MESSAGE_CREATE = "pmc"
    RANKS = "r"
    RATING = "rtg"
    RATING_MODE = "rmd"
    RATING_TYPE = "rt"
    RATING_USERS_LIST = "rul"
    RATING_VALUE = "rv"
    REASON = "r"
    REMOVE_COMPLAINT = "rcmp"
    REMOVE_FRIEND = "rf"
    REMOVE_INVITATION_TO_ROOM = "ritr"
    REMOVE = "rm"
    REMOVE_MESSAGES = "rmm"
    REMOVE_PHOTO = "rph"
    REMOVE_PLAYER = "rp"
    REMOVE_USER = "rmu"
    ROLES = "roles"
    ROLE_ACTION = "ra"
    ROLE = "r"
    ROOMS = "rs"
    ROOM_CREATED = "rcd"
    ROOM_CREATE = "rc"
    ROOM_ENTER = "re"
    ROOM_MODEL_TYPE = "rmt"
    ROOM_STATISTICS = "rst"
    ROOM_IN_LOBBY_STATE = "rils"
    ROOM = "rr"
    ROOM_MESSAGE_CREATE = "rmc"
    ROOM_OBJECT_ID = "ro"
    ROOM_PASSWORD_IS_WRONG_ERROR = "rpiw"
    ROOM_PASS = "psw"
    ROOM_STATUS = "rs"
    SCORE = "sc"
    SCREENSHOT = "sc"
    SEARCH_TEXT = "st"
    SEARCH_USER = "su"
    SELECTED_ROLES = "sr"
    SEND_FRIEND_INVITE_TO_ROOM = "sfitr"
    SERVER_CONFIG = "scfg"
    SERVER_LANGUAGE_CHANGE_TIME = "slct"
    SERVER_LANGUAGE = "slc"
    SERVER_ROOM_TITLE_MINIMAL_LEVEL = "srtml"
    SERVER_ROOM_PASSWORD_MINIMAL_LEVEL = "srpml"
    SET_ROOM_PASSWORD_MIN_AUTHORITY = "srpma"
    SET_PROFILE_PHOTO_MINIMAL_LEVEL = "sppml"
    SET_SERVER_LANGUAGE_TIME_ERROR = "sslte"
    SEX = "s"
    SHOW_PASSWORD_ROOM_INFO_BUTTON = "sprib"
    SIGN_IN_ERROR = "siner"
    SIGN_IN = "sin"
    SIGN_OUT_USER = "soutu"
    STATUS = "s"
    TEAM = "t"
    TEXT = "tx"
    TIMER = "t"
    TIME = "t"
    TIME_SEC_REMAINING = "tsr"
    TIME_UNTIL = "tu"
    TITLE = "tt"
    TOKEN = "t"
    TYPE_ERROR = "err"
    TYPE = "ty"
    UPDATED = "up"
    UPLOAD_PHOTO = "upp"
    UPLOAD_SCREENSHOT = "ups"
    USED_LAST_MESSAGE = "um"
    USERNAME_HAS_WRONG_SYMBOLS = "unws"
    USERNAME_IS_EMPTY = "unie"
    USERNAME_IS_EXISTS = "unex"
    USERNAME_IS_OUT_OF_BOUNDS = "unob"
    USERNAME = "u"
    USERNAME_SET = "uns"
    USERNAME_TRANSLIT = "ut"
    USERS = "u"
    USER_BLOCKED = "ublk"
    USER_CHANGE_SEX = "ucs"
    USER_DASHBOARD = "uud"
    USER_DATA = "ud"
    USER_INACTIVE_BLOCKED = "uib"
    USER_IN_ANOTHER_ROOM = "uiar"
    USER_IN_A_ROOM = "uir"
    USER_IS_NOT_VIP = "uinv"
    USER_IS_NOT_VIP_TO_INVITE_FRIENDS_IN_ROOM = "uinvtifr"
    USER = "uu"
    USER_KICKED = "ukd"
    USER_LEVEL_NOT_ENOUGH = "ulne"
    USER_NOT_IN_A_ROOM = "unir"
    USER_OBJECT_ID = "uo"
    USER_PROFILE = "uup"
    USER_RANK_FOR_KICK = "ur"
    USER_RANK = "r"
    USER_RECEIVER = "ur"
    USER_ROLE_ERROR = "ure"
    USER_SENDER = "us"
    USER_SENDER_OBJECT_ID = "uso"
    USER_SET_SERVER_LANGUAGE = "usls"
    USER_SET_USERNAME_ERROR = "ueue"
    USER_ENERGY = "ue"
    USER_SIGN_IN = "usi"
    USER_USING_DOUBLE_ACCOUNT = "uuda"
    VEST = "v"
    VIP_ENABLED = "venb"
    VIP = "v"
    VIP_ACCOUNT = "vip_account"
    VIP_UPDATED = "vupd"
    VOTES = "v"
    VOTE = "v"
    WHO_WON = "w"
    WINS_AS_KILLER = "wik"
    WINS_AS_MAFIA = "wim"
    WINS_AS_PEACEFUL = "wip"
    WRONG_FILE_SIZE = "wfs"
    WRONG_FILE_TYPE = "wft"
    YOUR_FRIENDSHIP_LIST_FULL = "yflf"
    ID = "i"
    MATCH_MAKING_SCORE = "mmscr"
    MATCH_MAKING_ADD_USER = "mmauk"
    MATCH_MAKING_REMOVE_USER = "mmruk"
    MATCH_MAKING_LIST_KEY = "mmblk"
    MATCH_MAKING_USER_IN_ROOM = "mmuir"
    MATCH_MAKING_BUCKET_RESPONSE_PLAYERS_AMOUNT = "mmbpa"
    VOTE_PLAYER_LIST = "vpl"
    PRIVATE_CHAT_LIST_MESSAGES = "pclms"
    PROFILE_USER_DATA = "pud"
    USER_ACCOUNT_COINS = "uac"
    SILVER_COINS = "scns"
    GOLD_COINS = "gcns"
    DECORATIONS = "dcrs"
    SAME_ROOM = "isr"
    BLOCKED_USER_INFO = "bui"
    DECORATION_ID = "did"
    DECORATION_TYPE = "dt"
    DECORAION_PARARAMETER = "dp"
    USER_CURRENET_ENERGY_AMOUNT = "ucea"
    USER_MAX_FREE_ENERGY_AMOUNT = "umfea"
    USER_ENERGY_AMOUNT_FIRST_TIMER = "ueaft"
    USER_ENERGY_AMOUNT_NEXT_TIMERS = "ueant"
    CREATOR_OBJECT_ID = "rco"



    # MARKET
    UNKNOWN1 = "mbt"
    UNKNOWN2 = "mrktgg"
    UNKNOWN3 = "mrktg"



class HttpsApiKeys(str, Enum):
    """Enumeration of standard HTTP API parameter keys.

    This enum defines the string constants used as keys in HTTPS API requests.
    These keys are used to identify values such as credentials, language settings,
    and device identifiers during HTTP communication with the server.

    Attributes:
        LANGUAGE (str): Key for specifying the language.
        NEW_EMAIL (str): Key for submitting a new email address.
        DEVICE_ID (str): Key for identifying the user's device.
        USER_OBJECT_ID (str): Key for the user's object ID.
        EMAIL (str): Key for the user's email address.
        USERNAME (str): Key for the user's username.
        PASSWORD (str): Key for the user's password.
        CURRENT_PASSWORD (str): Key for the user's current password.
        VERIFICATION_CODE (str): Key for email or account verification code.
    """
    LANGUAGE = "lang"
    NEW_EMAIL = "newEmail"
    DEVICE_ID = "deviceId"
    USER_OBJECT_ID = "userObjectId"
    EMAIL = "email"
    USERNAME = "username"
    PASSWORD = "password"
    CURRENT_PASSWORD = "currentPassword"
    VERIFICATION_CODE = "verificationCode"


class ZafiaApiKeys(str, Enum):
    """
    Enumeration of API parameter keys used in Zafia API requests.

    This enum defines string constants representing keys commonly used
    in requests to the Zafia API. These keys identify user-related data,
    request parameters, and device information.

    Attributes:
        USER_ID (str): Key for specifying the user identifier.
        FAVORITE_ID (str): Key for specifying the favorite item identifier.
        SHOW (str): Key for controlling visibility or display options.
        FROM_TYPE (str): Key indicating the source or type of a request.
        CHECK_ID (str): Key for an ID to be checked or verified.
        USER_NICKNAME (str): Key for the user's nickname.
        CHECK_NICKNAME (str): Key for a nickname to be checked.
        TYPE (str): Key for specifying the type or category.
        VERSION (str): Key for the API or client version.
        DEVICE_ID (str): Key for identifying the user's device.
    """
    USER_ID = "userId"
    FAVORITE_ID = "favoriteId"
    SHOW = "show"
    FROM_TYPE = "fromType"
    CHECK_ID = "checkId"
    USER_NICKNAME = "userNickname"
    CHECK_NICKNAME = "checkNickname"
    TYPE = "type"
    VERSION = "version"
    DEVICE_ID = "deviceId"


class Endpoints(str, Enum):
    """
    Enumeration of API endpoint paths for Mafia Online backend.

    This enum defines the string constants for various HTTP API endpoints
    used by the Mafia Online client to interact with the backend services.

    Attributes:
        REMOVE_ACCOUNT (str): Endpoint for deleting a user account.
        PROFILE_PHOTO (str): Endpoint to fetch a user's profile photo by user ID.
        CLIENT_CONFIG (str): Endpoint for retrieving client configuration with version.
        CLIENT_FEATURE_CONFIG (str): Endpoint for fetching feature configuration.
        USER_SIGN_OUT (str): Endpoint for signing out the user.
        USER_SIGN_UP (str): Endpoint for registering a new user.
        USER_EMAIL_VERIFY (str): Endpoint to verify a user's email.
        USER_CHANGE_EMAIL (str): Endpoint for changing the user's email address.
        USER_EMAIL_VERIFICATION (str): Endpoint to request email verification code.
        USER_GET (str): Endpoint to retrieve user profile data.
        BACKPACK_GET (str): Endpoint to get the contents of a user's backpack.
        BACKPACK_GET_BONUS_PRICES (str): Endpoint to fetch bonus item prices in the backpack.
    """
    REMOVE_ACCOUNT = "user/remove"
    PROFILE_PHOTO = "mafia/profile_photo/{user_id}.jpg"
    CLIENT_CONFIG = "mafia/clientConfig{version}.txt"
    CLIENT_FEATURE_CONFIG = "client_feature_config"
    USER_SIGN_OUT = "user/sign_out"
    USER_SIGN_UP = "user/sign_up"
    USER_EMAIL_VERIFY = "user/email/verify"
    USER_CHANGE_EMAIL = "user/change/email"
    USER_EMAIL_VERIFICATION = "user/email/verification"
    USER_GET = "user/get"
    BACKPACK_GET = "backpack/get"
    BACKPACK_GET_BONUS_PRICES = "backpack/get_bonus_prices"


class ZafiaEndpoints(str, Enum):
    """
    API endpoints for Zafia Online.

    This enum contains shorthand identifiers used in Zafia Online's
    internal API routing. Each value corresponds to a specific backend
    action that the client can trigger.

    Attributes:
        CHANGE_FAVORITE_STATUS: Change the favorite status of a user.
        CHANGE_VISIBLE_TOP: Change a user's visibility in the top list.
        CHECK_PROFILE: Retrieve another user's profile data.
        GET_FAVORITES_LIST: Get the current user's list of favorites.
        GET_TOP: Retrieve the top-ranking users.
        GET_VERIFICATIONS: Get verification-related data.
    """
    CHANGE_FAVORITE_STATUS = "cfs"
    CHANGE_VISIBLE_TOP = "cvt"
    CHECK_PROFILE = "cpr"
    GET_FAVORITES_LIST = "gfl"
    GET_TOP = "gt"
    GET_VERIFICATIONS = "vf"


    def format(self, *args: Any, **kwargs: Any) -> str:
        """
        Formats the enum value as a string using provided keyword arguments.

        This method uses the underlying enum string (self.value) as a format
        string and substitutes any named placeholders with values from kwargs.

        Args:
            *args: Unused. Present for compatibility.
            **kwargs: Keyword arguments to format the string.

        Returns:
            str: Formatted string with placeholders replaced by keyword values.
        """
        return self.value.format(**kwargs)


class Renaming(dict, Enum):
    """
    Field name mappings for different object types used in the API.

    This enum stores dictionaries that map verbose field names to their
    shortened versions used in serialization, API responses, or internal
    communication. Each attribute represents a context-specific renaming
    schema (e.g., user data, room settings, server config).

    Attributes:
        USER: Mapping for user-related fields.
        USER_NEW_API: Mapping for extended user fields in new API version.
        SERVER_CONFIG: Mapping for server configuration fields.
        ROOM: Mapping for basic room-related fields.
        ROOM_IN_LOBBY: Mapping for room fields shown in lobby context.
        ROOM_IN_LOBBY_STATE: Mapping for additional room lobby state fields.
        SHORT_USER: Mapping for minimal user representations.
        FRIEND: Mapping for friend list entries.
        FRIENDSHIP: Mapping for friendship relationship data.
        MESSAGE: Mapping for messaging system fields.
        GUI: Mapping for GUI-specific identifiers.
        DECORATIONS: Mapping for decoration item types.
        DECORATIONS_PARAMETERS: Mapping for parameters of decorations.
    """
    USER = {
        "user_id": "o", "username": "u",
        "updated": "up", "photo": "ph", "experience": "ex",
        "next_level_experience": "nle",
        "previous_level_experience": "ple", "level": "l",
        "gold": "g", "money": "mo",
        "is_vip": "v", "vip_updated": "vupd",
        "played_games": "pg", "score": "sc",
        "sex": "s", "wins_as_killer": "wik",
        "wins_as_mafia": "wim", "wins_as_peaceful": "wip",
        "token": "t", "accept_messages": "ac",
        "rank": "r", "selected_language": "slc",
        "online": "on", "player_role_statistics": "prst",
        "match_making_score": "mmscr"
        }

    USER_NEW_API = {
        "user_id": "o", "username": "u",
        "updated": "up", "photo": "ph", "experience": "ex",
        "next_level_experience": "nle",
        "previous_level_experience": "ple", "level": "l", 
        "gold": "g", "money": "mo",
        "is_vip": "v", "vip_updated": "vupd",
        "played_games": "pg", "score": "sc",
        "sex": "s", "wins_as_killer": "wik",
        "wins_as_mafia": "wim", "wins_as_peaceful": "wip",
        "token": "t", "accept_messages": "ac",
        "selected_language": "slc", "user_account_coins": "uac",
        "decorations": "dcrs", "silver_coins": "scns",
        "online": "on", "player_role_statistics": "prst",
        "match_making_score": "mmscr"
        }

    SERVER_CONFIG = {
        "kick_user_price": "kup",
        "set_room_password_min_authority": "srpma",
        "price_username_set": "pus",
        "server_language_change_time": "slct",
        "show_password_room_info_button": "sprib",
        "set_photo_minimal_level": "sppml", 
        "room_title_minimal_level": "srtml",
        "room_password_minimal_level": "srpml",
        "match_making_users_in_queue": "mmguiqik",
        "connection_inactive_timeout": "cit",
        "connection_checker_period": "ccp",
        }

    ROOM = {
        "room_id": "o", "min_players": "mnp",
        "max_players": "mxp", "min_level": "mnl",
        "vip_enabled": "venb", "status": "s",
        "selected_roles": "sr", "title": "tt",
        "password": "pw"
        }

    ROOM_IN_LOBBY = {
        "room_id": "o", "min_players": "mnp",
        "max_players": "mxp", "min_level": "mnl",
        "vip_enabled": "venb", "status": "s",
        "selected_roles": "sr", "title": "tt",
        "password": "pw", "creator_id": "rco", 
        "game_status": "s", "room_status": "rs",
        "friend_in_room": "fir", "players": "pls",
        "players_number": "pn",
        "invited_in_room": "iinvtd",
        "invitation_sender_username": "isun",
        "friend_in_room": "fir",
    }

    ROOM_IN_LOBBY_STATE = {
        "invitation_sender_username": "isun",
        "friend_in_room": "fir",
        "players_in_room": "pin",
        "invited_in_room": "iinvtd",
        "room_id": "ro"
    }

    SHORT_USER = {
        "user_id": "o", "username": "u",
        "updated": "up", "photo": "ph", "online": "on",
        "sex": "s", "is_vip": "v", "vip_updated": "vupd"
        }

    FRIEND = {
        "friend_id": "o", "updated": "up",
        "user": "uu", "new_messages": "nm",
        "user_id": "uo"
        }

    FRIENDSHIP = {
        # friendship response
        "accepted": "a", "currenet_room": "rr",
        "friend_data": "ff", "friend_id": "f", 
        "user_data": "uu"
        }

    MESSAGE = {
        "user_id": "uo", "friend_id": "fp",
        "created": "c", "text": "tx", "message_style": "mstl",
        "accepted": "a", "message_type": "t"
            }

    GUI = {
        "count_authority_for_swap_icon":"r"
        }

    DECORATIONS = {
        "photo_border": "8", "photo_border_animation": "7",
        "profile_animation": "4", "profile_background": "6",
        "profile_main_color": "5", "username_animation": "0",
        "username_background": "1", "username_shadow": "2",
        "username_text": "3"
    }

    DECORATIONS_PARAMETERS = {
        "alpha": "0", "value": "1",
        "file": "2", "speed": "3"
    }
