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

from typing import Any, TypeVar

from zafiaonline.utils.proxy_store import store
from zafiaonline.service_generator.helper import make_submodule_property


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
    # User
    auth = make_submodule_property(
        "auth",
        "user_methods",
        "AuthService",
        client=lambda self: self
    )
    user = make_submodule_property(
        "user",
        "user_methods",
        "UserMethods",
        auth_client=lambda self: self.auth
    )

    # Players
    players = make_submodule_property(
        "players",
        "player_methods",
        "PlayersMethods",
        auth_client=lambda self: self.auth
    )

    # Global Chat
    global_chat = make_submodule_property(
        "global_chat",
        "global_chat_methods",
        "GlobalChatMethods",
        auth_client=lambda self: self.auth
    )

    # Room
    room = make_submodule_property(
        "room",
        "room_methods",
        "RoomMethods",
        auth_client=lambda self: self.auth
    )
    matchmaking = make_submodule_property(
        "matchmaking",
        "room_methods",
        "MatchMakingMethods",
        auth_client=lambda self: self.auth
    )

    # Traffic
    https = make_submodule_property(
        "https",
        "https_api",
        "HttpsApiMethods"
    )
    zafia = make_submodule_property(
        "zafia",
        "zafia_api",
        "ZafiaApiMethods"
    )

    # Typing
    _submodule = TypeVar("_submodule")

    def __init__(self, proxy: str | None = None) -> None:
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

    def __getattr__(self, name: str) -> object:
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
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def _import_submodule(
        self,
        attr: str,
        module_name: str,
        class_name: str,
        *args: Any,
        **kwargs: Any
    ) -> object:
        """
        Lazily imports a submodule class, instantiates it, and caches the instance.

        This method ensures that each submodule is loaded only once and reused
        across the client. On first access, the specified module is imported,
        the target class is retrieved and instantiated, and the instance is
        stored in the internal cache. Subsequent calls return the cached instance.

        Args:
            attr (str): Cache key (attribute name) for storing the instance.
            module_name (str): Submodule name inside `zafiaonline.api_client`.
            class_name (str): Name of the class within the submodule to instantiate.
            *args: Positional arguments forwarded to the class constructor.
            **kwargs: Keyword arguments forwarded to the class constructor.

        Returns:
            object: The cached or newly created instance of the requested class.

        Raises:
            ImportError: If the submodule cannot be imported, or the expected class
                is not defined inside the module.
            RuntimeError: If the class cannot be instantiated with the provided
                arguments or other unexpected errors occur during initialization.
        """
        if attr not in self._cache:
            try:
                module: types.ModuleType = importlib.import_module(
                    f"zafiaonline.api_client.{module_name}"
                )
                cls: type[Client._submodule] = getattr(module, class_name)
                self._cache[attr] = cls(*args, **kwargs)

            except ImportError as e:
                raise ImportError(
                    f"Failed to import module "
                    f"'zafiaonline.api_client.{module_name}'"
                ) from e
            except AttributeError as e:
                raise ImportError(
                    f"Module '{module_name}'" 
                    f"does not define class '{class_name}'"
                ) from e
            except Exception as e:
                raise RuntimeError(
                    f"Failed to initialize "
                    f"'{class_name}' from '{module_name}' "
                    f"with args={args}, kwargs={kwargs}"
                ) from e

        return self._cache[attr]
