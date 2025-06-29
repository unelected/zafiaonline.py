from msgspec import Struct
from typing import List

from zafiaonline.structures.packet_data_keys import Renaming
from zafiaonline.structures.enums import Sex, Languages, Roles

class ModelUser(Struct, rename = Renaming.USER):
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
    kick_user_price: int | None = None
    set_room_password_min_authority: int | None = None
    price_username_set: int | None = None
    server_language_change_time: int| None  = None
    show_password_room_info_button: bool | None = None


class ModelRoom(Struct, rename = Renaming.ROOM):
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
    user_id: str | None = None
    username: str | None = None
    updated: int | None = None
    photo: str | None = None
    online: int | None = None
    is_vip: int | None = None
    vip_updated: int | None = None
    sex: Sex = Sex.MEN


class ModelFriend(Struct, rename = Renaming.FRIEND):
    friend_id: str | None = None
    updated: int | None = None
    user: ModelShortUser | None = None
    new_messages: int | None = None


class ModelMessage(Struct, rename = Renaming.MESSAGE):
    user_id: str | None = None
    friend_id: str | None = None
    created: int | None = None
    text: str | None = None
    message_style: int | None = None
    accepted: int | None = None
    message_type: int | None = None


class ModelGUI(Struct, rename = Renaming.GUI):
    count_authority_for_swap_icon: dict | None = None
