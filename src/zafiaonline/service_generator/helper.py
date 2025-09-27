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
Factory for creating lazily-loaded submodule properties.

This module provides a helper function :func:`make_submodule_property`
that allows dynamic and lazy initialization of client submodules. It is
primarily used inside the `Client` class of the `zafiaonline` package to
instantiate API submodules (e.g., authentication, rooms, matchmaking)
only when they are accessed.

The design follows a combination of the "Lazy Initialization" and
"Factory" patterns. Dependencies between submodules are resolved through
callable factories, ensuring that the correct references are injected at
initialization time.

Example:
    from zafiaonline.main import Client
    client = Client()
    client.auth  # lazily instantiates AuthService
    client.room  # lazily instantiates RoomMethods, injecting auth

Typical usage within Client:
    auth = make_submodule_property(
        "auth", "user_methods", "AuthService", client=lambda self: self
    )
    room = make_submodule_property(
        "room", "room_methods", "RoomMethods", auth_client=lambda self: self.auth
    )
"""
from typing import Any, Callable


def make_submodule_property(
    attr: str,
    module_name: str,
    class_name: str,
    **init_factories: Callable,
) -> property:
    """
    Create a lazily-initialized submodule property.

    This function returns a property object that, when accessed,
    imports a submodule dynamically, instantiates a target class,
    and injects required dependencies. The created instance is
    cached by the client to avoid repeated initialization.

    Args:
        attr (str): Attribute name used as the cache key.
        module_name (str): Name of the submodule inside
            ``zafiaonline.api_client``.
        class_name (str): Target class name within the submodule.
        **init_factories (Callable): Keyword arguments passed to the
            class constructor. Each value can be:
            - a callable (e.g., ``lambda self: self.auth``) that will
              be evaluated with the client instance.
            - a static value passed directly.

    Returns:
        property: A property descriptor that lazily initializes and
        returns the requested submodule instance.

    Raises:
        AttributeError: If a required dependency cannot be resolved
            (e.g., accessing a submodule before its dependency exists).
        ImportError: If the requested submodule cannot be imported.
    """
    def _getter(self) -> object:
        """
        Retrieve or initialize the submodule instance.

        This getter is used internally by ``make_submodule_property`` to lazily
        construct and cache submodules on first access. It builds the keyword
        arguments from the provided init factories, then delegates submodule
        loading to :meth:`Client._import_submodule`.

        Returns:
            object: The cached or newly created submodule instance.

        Raises:
            RuntimeError: If building kwargs from init factories fails, or if
                the submodule class fails to initialize.
            ImportError: If the target module or class cannot be imported.
        """
        try:
            kwargs: dict[str, Any] = {
                kwarg: (factory(self) if callable(factory) else factory)
                for kwarg, factory in init_factories.items()
            }

        except Exception as e:
            raise RuntimeError(
                f"Failed to build kwargs for submodule '{class_name}' "
                f"(attr='{attr}')"
            ) from e

        try:
            return self._import_submodule(
                attr,
                module_name,
                class_name,
                **kwargs
            )

        except ImportError as e:
            raise ImportError(
                f"Could not import submodule '{module_name}.{class_name}' "
                f"for attribute '{attr}'"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize submodule '{class_name}' "
                f"from '{module_name}'"
            ) from e

    return property(_getter)
