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
Copies non-callable attributes of a client object onto itself.

This module provides a utility function for copying all non-callable
attributes from a client's `__dict__` back to the client instance.

Intended for use in dynamic or reflective systems where attribute resetting
or propagation is necessary.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zafiaonline.api_client.user_methods import Auth


def get_user_attributes(auth: "Auth") -> None:
    """
    Reassigns all non-callable attributes from a client's __dict__ to itself.

    Args:
        auth: The client object whose attributes will be reassigned.

    Returns:
        None
    """
    for key, value in auth.__dict__.items():
        if not callable(value):
            setattr(auth, key, value)
