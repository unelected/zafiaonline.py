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
