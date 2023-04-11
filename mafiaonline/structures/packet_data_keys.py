from enum import StrEnum, Enum


class PacketDataKeys(StrEnum):
    ACCEPTED_KEY = "a"
    ACCEPT_MESSAGES_KEY = "ac"
    ACTIVE_KEY = "ac"
    ACTIVITY_KEY = "ac"
    ADD_CLIENT_TO_CHAT_KEY = "acc"
    ADD_CLIENT_TO_DASHBOARD_KEY = "acd"
    ADD_CLIENT_TO_FRIENDSHIP_LIST_KEY = "acfl"
    ADD_CLIENT_TO_PRIVATE_CHAT_KEY = "acpc"
    ADD_CLIENT_TO_ROOMS_LIST_KEY = "acrl"
    ADD_FRIEND_KEY = "af"
    ADD_KEY = "add"
    ADD_PLAYER_KEY = "ap"
    ADMIN_BLOCK_USER_KEY = "abu"
    ADMIN_CONTROL_USER_KEY = "acu"
    ADMIN_KEY = "adm"
    ADMIN_KICK_USER_KEY = "aku"
    ADMIN_UNBLOCK_USER_KEY = "auu"
    AFFECTED_BY_ROLES_KEY = "abr"
    ALIVE_KEY = "a"
    APP_LANGUAGE_KEY = "alc"
    ASPIRIN_KEY = "a"
    AUTHORITY_KEY = "a"
    BACKPACK_KEY = "bp"
    BILLING_APP_PACKAGE_KEY = "bapckg"
    BILLING_PRODUCT_ID_KEY = "bpid"
    BILLING_PURCHASE_PENDING_KEY = "bppndng"
    BILLING_PURCHASE_TOKEN_KEY = "bptkn"
    BLOCKED_USERS_KEY = "bus"
    BLOCK_DEVICE_KEY = "bdv"
    BLOCK_IP_KEY = "bi"
    BONUSES_ENABLED_KEY = "bns"
    BONUS_PRICE_KEY = "bp"
    BRIBE_KEY = "b"
    BUY_BILLING_MARKET_ITEM_KEY = "bbmrkti"
    BUY_BILLING_MARKET_SUCCESS_ITEM_KEY = "bbmrktis"
    BUY_MARKET_ITEM_KEY = "bmrkti"
    BUY_MARKET_ITEM_SUCCESS_KEY = "bmrktis"
    CHAT_MESSAGE_CREATE_KEY = "cmc"
    CHECK_PLAYER_IS_IN_ROOM_KEY = "cpir"
    CIVILIAN_ALIVE_KEY = "c"
    CIVILIAN_ALL_KEY = "ca"
    CLEAN_VOTES_HISTORY_KEY = "cv"
    CLOUD_MESSAGING_TOKEN_IS_SAVED_KEY = "cmts"
    COMPLAINTS_KEY = "cmps"
    COMPLAINT_KEY = "cmp"
    CONDOM_KEY = "cm"
    CONFESSION_KEY = "cn"
    CREATED_KEY = "c"
    CREATE_PLAYER_KEY = "cp"
    CREATOR_BLOCKED_KEY = "crb"
    DATA_KEY = "data"
    DAYTIME_KEY = "d"
    DESCRIPTION_KEY = "dsc"
    DEVICE_ID_KEY = "d"
    EMAIL_KEY = "e"
    EMAIL_NOT_VERIFIED_KEY = "env"
    EMAIL_NOT_VERIFIED_MESSAGE_CREATE_TIMEOUT_KEY = "envmct"
    ERROR_FLOOD_DETECTED_KEY = "erfd"
    ERROR_KEY = "e"
    ERROR_OCCUR_KEY = "ero"
    EXPERIENCE_KEY = "ex"
    FILE_KEY = "f"
    FIRST_AID_KIT_KEY = "f"
    FIRST_NAME_KEY = "fn"
    FRIENDSHIP_FLAG_KEY = "fpf"
    FRIENDSHIP_KEY = "fp"
    FRIENDSHIP_LIST_KEY = "frl"
    FRIENDSHIP_LIST_LIMIT = "fll"
    FRIENDSHIP_LIST_LIMIT_FOR_VIP = "fllfv"
    FRIENDSHIP_REQUESTS_KEY = "fr"
    FRIENDS_IN_INVITE_LIST_KEY = "fiil"
    FRIEND_IN_ROOM_KEY = "fir"
    FRIEND_IS_INVITED_KEY = "fiinvtd"
    FRIEND_KEY = "ff"
    FRIEND_USER_OBJECT_ID_KEY = "f"
    GAME_DAYTIME_KEY = "gd"
    GAME_FINISHED_KEY = "gf"
    GAME_STARTED_KEY = "gsd"
    GAME_STATUS_IN_ROOMS_LIST_KEY = "gsrl"
    GAME_STATUS_KEY = "gs"
    GET_BLOCKED_USERS_KEY = "gbus"
    GET_COMPLAINTS_KEY = "gcmps"
    GET_FRIENDS_IN_INVITE_LIST_KEY = "gfiil"
    GET_PLAYERS_KEY = "gp"
    GET_RATING_KEY = "gr"
    GET_SENT_FRIEND_REQUESTS_LIST_KEY = "gsfrl"
    GET_USER_PROFILE_KEY = "gup"
    GIFT_MARKET_ITEMS_KEY = "gmrkti"
    GOLD_KEY = "g"
    GOOGLE_SIGN_IN_KEY = "gsin"
    GOOGLE_TOKEN_KEY = "gt"
    GOOGLE_USER_ID_KEY = "gui"
    HIS_FRIENDSHIP_LIST_FULL = "hflf"
    INFO_MESSAGE_KEY = "imsg"
    INVITATION_SENDER_USERNAME_KEY = "isun"
    IP_ADDRESS_KEY = "ip"
    IS_BILLING_ITEM_KEY = "ibi"
    IS_DAY_ACTION_USED_KEY = "idau"
    IS_INVITED_KEY = "iinvtd"
    IS_NIGHT_ACTION_ALTERNATIVE_KEY = "inaa"
    IS_NIGHT_ACTION_USED_KEY = "inau"
    IS_ONLINE_KEY = "on"
    ITEM_PRICE_TEXT_KEY = "iprct"
    KICK_TIMER_KEY = "kt"
    KICK_USER_AUTHORITY_LESS_THAN_USER_KEY = "kualtu"
    KICK_USER_GAME_STARTED_KEY = "kugs"
    KICK_USER_KEY = "ku"
    KICK_USER_NOT_IN_ROOM_KEY = "kunir"
    KICK_USER_OBJECT_ID_KEY = "k"
    KICK_USER_PRICE = "kup"
    KICK_USER_RANK_KEY = "kur"
    KICK_USER_STARTED_KEY = "kus"
    KICK_USER_VOTE_KEY = "kuv"
    LAST_NAME_KEY = "ln"
    LEVEL_KEY = "l"
    LIE_DETECTOR_KEY = "l"
    MAFIA_ALIVE_KEY = "m"
    MAFIA_ALL_KEY = "ma"
    MAKE_COMPLAINT_KEY = "mc"
    MARKET_ITEMS_KEY = "mrkti"
    MAXIMUM_PLAYERS_KEY = "mxmp"
    MAX_PLAYERS_KEY = "mxp"
    MESSAGES_KEY = "ms"
    MESSAGE_KEY = "m"
    MESSAGE_STYLE_KEY = "mstl"
    MESSAGE_TYPE_KEY = "t"
    MIN_LEVEL_KEY = "mnl"
    MIN_PLAYERS_KEY = "mnp"
    MONEY_KEY = "mo"
    NEW_CLOUD_MESSAGING_TOKEN_KEY = "ncmt"
    NEW_MESSAGES_KEY = "nm"
    NEXT_LEVEL_EXPERIENCE_KEY = "nle"
    NOT_ENOUGH_AUTHORITY_ERROR_KEY = "neae"
    NO_CHANGES_KEY = "noch"
    NUM_KEY = "n"
    NUM_MAFIA_KEY = "m"
    NUM_PLAYERS_KEY = "p"
    OBJECT_ID_KEY = "o"
    PASSWORD_KEY = "pw"
    PHOTO_KEY = "ph"
    PLAYED_GAMES_KEY = "pg"
    PLAYERS_IN_ROOM_KEY = "pin"
    PLAYERS_KEY = "pls"
    PLAYERS_NUM_KEY = "pn"
    PLAYERS_STAT_KEY = "ps"
    PLAYER_KEY = "p"
    PLAYER_ROLE_STATISTICS_KEY = "prst"
    PREVIOUS_LEVEL_EXPERIENCE_KEY = "ple"
    PRICE_USERNAME_SET = "pus"
    PRIVATE_CHAT_MESSAGE_CREATE_KEY = "pmc"
    RANKS_KEY = "r"
    RATING_KEY = "rtg"
    RATING_MODE_KEY = "rmd"
    RATING_TYPE_KEY = "rt"
    RATING_USERS_LIST_KEY = "rul"
    RATING_VALUE_KEY = "rv"
    REASON_KEY = "r"
    REMOVE_COMPLAINT_KEY = "rcmp"
    REMOVE_FRIEND_KEY = "rf"
    REMOVE_INVITATION_TO_ROOM_KEY = "ritr"
    REMOVE_KEY = "rm"
    REMOVE_MESSAGES_KEY = "rmm"
    REMOVE_PHOTO_KEY = "rph"
    REMOVE_PLAYER_KEY = "rp"
    REMOVE_USER_KEY = "rmu"
    ROLES_KEY = "roles"
    ROLE_ACTION_KEY = "ra"
    ROLE_KEY = "r"
    ROOMS_KEY = "rs"
    ROOM_CREATED_KEY = "rcd"
    ROOM_CREATE_KEY = "rc"
    ROOM_ENTER_KEY = "re"
    ROOM_IN_LOBBY_STATE_KEY = "rils"
    ROOM_KEY = "rr"
    ROOM_MESSAGE_CREATE_KEY = "rmc"
    ROOM_OBJECT_ID_KEY = "ro"
    ROOM_PASSWORD_IS_WRONG_ERROR_KEY = "rpiw"
    ROOM_PASS_KEY = "psw"
    ROOM_STATUS_KEY = "rs"
    SCORE_KEY = "sc"
    SCREENSHOT_KEY = "sc"
    SEARCH_TEXT_KEY = "st"
    SEARCH_USER_KEY = "su"
    SELECTED_ROLES_KEY = "sr"
    SEND_FRIEND_INVITE_TO_ROOM_KEY = "sfitr"
    SERVER_CONFIG = "scfg"
    SERVER_LANGUAGE_CHANGE_TIME = "slct"
    SERVER_LANGUAGE_KEY = "slc"
    SET_ROOM_PASSWORD_MIN_AUTHORITY = "srpma"
    SET_SERVER_LANGUAGE_TIME_ERROR_KEY = "sslte"
    SEX_KEY = "s"
    SHOW_PASSWORD_ROOM_INFO_BUTTON = "sprib"
    SIGN_IN_ERROR_KEY = "siner"
    SIGN_IN_KEY = "sin"
    SIGN_OUT_USER_KEY = "soutu"
    STATUS_KEY = "s"
    TEAM_KEY = "t"
    TEXT_KEY = "tx"
    TIMER_KEY = "t"
    TIME_KEY = "t"
    TIME_SEC_REMAINING_KEY = "tsr"
    TIME_UNTIL_KEY = "tu"
    TITLE_KEY = "tt"
    TOKEN_KEY = "t"
    TYPE_ERROR_KEY = "err"
    TYPE_KEY = "ty"
    UPDATED_KEY = "up"
    UPLOAD_PHOTO_KEY = "upp"
    UPLOAD_SCREENSHOT_KEY = "ups"
    USED_LAST_MESSAGE_KEY = "um"
    USERNAME_HAS_WRONG_SYMBOLS_KEY = "unws"
    USERNAME_IS_EMPTY_KEY = "unie"
    USERNAME_IS_EXISTS_KEY = "unex"
    USERNAME_IS_OUT_OF_BOUNDS_KEY = "unob"
    USERNAME_KEY = "u"
    USERNAME_SET_KEY = "uns"
    USERNAME_TRANSLIT_KEY = "ut"
    USERS_KEY = "u"
    USER_BLOCKED_KEY = "ublk"
    USER_CHANGE_SEX_KEY = "ucs"
    USER_DASHBOARD_KEY = "uud"
    USER_DATA_KEY = "ud"
    USER_INACTIVE_BLOCKED_KEY = "uib"
    USER_IN_ANOTHER_ROOM_KEY = "uiar"
    USER_IN_A_ROOM_KEY = "uir"
    USER_IS_NOT_VIP_KEY = "uinv"
    USER_IS_NOT_VIP_TO_INVITE_FRIENDS_IN_ROOM_KEY = "uinvtifr"
    USER_KEY = "uu"
    USER_KICKED_KEY = "ukd"
    USER_LEVEL_NOT_ENOUGH_KEY = "ulne"
    USER_NOT_IN_A_ROOM_KEY = "unir"
    USER_OBJECT_ID_KEY = "uo"
    USER_PROFILE_KEY = "uup"
    USER_RANK_FOR_KICK_KEY = "ur"
    USER_RANK_KEY = "r"
    USER_RECEIVER_KEY = "ur"
    USER_ROLE_ERROR_KEY = "ure"
    USER_SENDER_KEY = "us"
    USER_SENDER_OBJECT_ID_KEY = "uso"
    USER_SET_SERVER_LANGUAGE_KEY = "usls"
    USER_SET_USERNAME_ERROR_KEY = "ueue"
    USER_SIGN_IN_KEY = "usi"
    USER_USING_DOUBLE_ACCOUNT_KEY = "uuda"
    VEST_KEY = "v"
    VIP_ENABLED_KEY = "venb"
    VIP_KEY = "v"
    VIP_UPDATED_KEY = "vupd"
    VOTES_KEY = "v"
    VOTE_KEY = "v"
    WHO_WON_KEY = "w"
    WINS_AS_KILLER_KEY = "wik"
    WINS_AS_MAFIA_KEY = "wim"
    WINS_AS_PEACEFUL_KEY = "wip"
    WRONG_FILE_SIZE_KEY = "wfs"
    WRONG_FILE_TYPE_KEY = "wft"
    YOUR_FRIENDSHIP_LIST_FULL = "yflf"
    ID_KEY = "i"


class Renamers(dict, Enum):
    USER = {"user_id": "o", "username": "u", "updated": "up", "photo": "ph", "experience": "ex",
            "next_level_experience": "nle", "previous_level_experience": "ple", "level": "l",
            "authority": "a", "gold": "g", "money": "mo", "is_vip": "v", "vip_updated": "vupd",
            "played_games": "pg", "score": "sc", "sex": "s", "wins_as_killer": "wik",
            "wins_as_mafia": "wim", "wins_as_peaceful": "wip", "token": "t", "accept_messages": "ac",
            "rank": "r", "selected_language": "slc", "online": "on", "player_role_statistics": "prst"}
    SERVER_CONFIG = {"kick_user_price": "kup", "set_room_password_min_authority": "srpma",
                     "price_username_set": "pus", "server_language_change_time": "slct",
                     "show_password_room_info_button": "sprib"}
    ROOM = {"room_id": "o", "min_players": "mnp", "max_players": "mxp", "min_level": "mnl",
            "vip_enabled": "venb", "status": "s", "selected_roles": "sr", "title": "tt",
            "password": "pw"}
    SHORT_USER = {"user_id": "o", "username": "u", "updated": "up", "photo": "ph", "online": "on",
                  "sex": "s", "is_vip": "v", "vip_updated": "vupd"}
    FRIEND = {"friend_id": "o", "updated": "up", "user": "uu", "new_messages": "nm"}
    MESSAGE = {"user_id": "uo", "friend_id": "fp", "created": "c", "text": "tx", "message_style": "mstl",
               "accepted": "a", "message_type": "t"}