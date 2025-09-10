# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 unelected
#
# This file is part of the zafiaonline project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Unified client for Mafia Online services.

This module provides a unified interface for interacting with the
MafiaOnline API. It includes methods for authentication, room
management, global chat, matchmaking, and more.

Typical usage example:

    client = Client()
    client.auth.login(...)
"""
import importlib
import types

from typing import TYPE_CHECKING, Any, TypeVar, cast

from zafiaonline.utils.proxy_store import store
if TYPE_CHECKING:
    from zafiaonline.api_client.player_methods import Players 
    from zafiaonline.api_client.global_chat_methods import GlobalChat 
    from zafiaonline.api_client.user_methods import Auth, User 
    from zafiaonline.api_client.room_methods import Room, MatchMaking 
    from zafiaonline.api_client.https_api import HttpsApi 
    from zafiaonline.api_client.zafia_api import ZafiaApi


class Client:
    """
    Unified API client for MafiaOnline.

    Provides a single entry point for interacting with different MafiaOnline
    services. Each service (submodule) is lazily imported on first access and
    cached for reuse. This design allows modular usage without eagerly loading
    all dependencies.

    Submodules are automatically initialized with the shared client context
    and, when required, with the authentication submodule.

    Attributes:
        proxy (str | None): Optional proxy URL used for HTTPS requests.
        _cache (dict[str, Any]): Stores lazily created submodule instances.
    """
    _submodule = TypeVar("_submodule")
    def __init__(self, proxy: str | None = None):
        """
        Initializes all service submodules with shared client context.

        Dynamically imports and instantiates each API submodule, injecting
        this client (or the auth submodule) and optional proxy settings.

        Args:
            proxy (str | None): Optional proxy URL applied to HTTP sessions.
                If None, no proxy will be used.
        """
        self._cache: dict[str, Any] = {}
        if isinstance(proxy, str):
            store.add(proxy)

    def __getattr__(self, name: str):
        """
        Retrieve a cached submodule by attribute access.

        This method allows dynamic attribute access for submodules that have
        been lazily imported and stored in the cache.

        Args:
            name (str): The attribute name to look up in the cache.

        Returns:
            object: The cached submodule instance if found.

        Raises:
            AttributeError: If the attribute is not present in the cache.
        """
        if name in self._cache:
            return self._cache[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def _import_submodule(self, attr: str, module_name: str, class_name: str, *args, **kwargs) -> object:
        """
        Lazily imports a submodule class, instantiates it, and caches the instance.

        If the submodule is already cached under the given attribute name,
        the cached instance is returned. Otherwise, the module is imported,
        the class is instantiated with the provided arguments, and the
        instance is stored in the cache.

        Args:
            attr (str): Cache key (attribute name) for storing the instance.
            module_name (str): Submodule name inside `zafiaonline.api_client`.
            class_name (str): Name of the class within the submodule to instantiate.
            *args: Positional arguments forwarded to the class constructor.
            **kwargs: Keyword arguments forwarded to the class constructor.

        Returns:
            object: The cached or newly created instance of the requested class.
        """
        if attr not in self._cache:
            module: types.ModuleType = importlib.import_module(f"zafiaonline.api_client.{module_name}")
            cls: type[Client._submodule] = getattr(module, class_name)
            self._cache[attr] = cls(*args, **kwargs)
        return self._cache[attr]

    @property
    def auth(self) -> "Auth":
        """
        Access the authentication submodule.

        Lazily imports and returns an instance of the `Auth` submodule,
        caching it on first access. Used for handling user authentication
        such as sign-in, sign-up, and token management.

        Returns:
            Auth: The authentication submodule instance.
        """
        return cast("Auth", self._import_submodule("auth", 
                                                   "user_methods", "Auth", client = self))

    @property
    def players(self) -> "Players":
        """
        Access the players submodule.

        Lazily imports and returns an instance of the `Players` submodule,
        caching it on first access. Provides methods for interacting with
        player-related operations such as fetching player data or managing
        player state.

        Returns:
            Players: The players submodule instance.
        """
        return cast("Players", self._import_submodule("players", 
                                                      "player_methods", "Players", auth_client = self.auth))

    @property
    def user(self) -> "User":
        """
        Access the user submodule.

        Lazily imports and returns an instance of the `User` submodule,
        caching it on first access. Provides methods for interacting with
        the currently authenticated user, such as retrieving profile data
        or managing account information.

        Returns:
            User: The user submodule instance.
        """
        return cast("User", self._import_submodule("user", 
                                                   "user_methods", "User", auth_client = self.auth))

    @property
    def global_chat(self) -> "GlobalChat":
        """
        Access the global chat submodule.

        Lazily imports and returns an instance of the `GlobalChat` submodule,
        caching it on first access. Provides methods for interacting with the
        game's global chat, such as sending or receiving messages.

        Returns:
            GlobalChat: The global chat submodule instance.
        """
        return cast("GlobalChat", self._import_submodule("global_chat", 
                                                         "global_chat_methods", "GlobalChat", auth_client = self.auth))

    @property
    def room(self) -> "Room":
        """
        Access the room submodule.

        Lazily imports and returns an instance of the `Room` submodule,
        caching it on first access. Provides methods for creating, joining,
        and managing game rooms.

        Returns:
            Room: The room submodule instance.
        """
        return cast("Room", self._import_submodule("room", 
                                                   "room_methods", "Room", auth_client = self.auth))

    @property
    def matchmaking(self) -> "MatchMaking":
        """
        Access the matchmaking submodule.

        Lazily imports and returns an instance of the `MatchMaking` submodule,
        caching it on first access. Provides methods for automatic matchmaking
        and quick room joining.

        Returns:
            MatchMaking: The matchmaking submodule instance.
        """
        return cast("MatchMaking", self._import_submodule("matchmaking", 
                                                          "room_methods", "MatchMaking", auth_client = self.auth))

    @property
    def https(self) -> "HttpsApi":
        """
        Access the HTTPS API submodule.

        Lazily imports and returns an instance of the `HttpsApi` submodule,
        caching it on first access. Provides direct interaction with the
        HTTPS-based API endpoints, using the configured proxy if available.

        Returns:
            HttpsApi: The HTTPS API submodule instance.
        """
        return cast("HttpsApi", self._import_submodule("https", 
                                                       "https_api", "HttpsApi"))

    @property
    def zafia(self) -> "ZafiaApi":
        """
        Access the Zafia API submodule.

        Lazily imports and returns an instance of the `ZafiaApi` submodule,
        caching it on first access. Provides direct interaction with the
        Zafia-specific API endpoints, using the configured proxy if available.

        Returns:
            ZafiaApi: The Zafia API submodule instance.
        """
        return cast("ZafiaApi", self._import_submodule("zafia", 
                                                       "zafia_api", "ZafiaApi"))
