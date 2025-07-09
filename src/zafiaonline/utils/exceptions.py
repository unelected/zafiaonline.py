from typing import Type

from zafiaonline.main import Client


class ListenDataException(Exception):
    """
    Raised when an error occurs while receiving data from the WebSocket
    listener.

    This exception is typically used to indicate unexpected issues during the
    WebSocket message listening process, such as malformed data, timeouts, or
    disconnections that were not handled properly.
    """

    def __init__(self, message: str = "An error occurred while receiving data from "
                               "the listener."):
        super().__init__(message)


class ListenExampleErrorException(Exception):
    """
    Raised for specific test cases or example scenarios involving WebSocket
    listening errors.

    This exception is useful for handling controlled test failures, debugging,
    or identifying particular patterns in received messages that need special
    handling.
    """

    def __init__(self, message: str = "An example listening error occurred."):
        super().__init__(message)

class BanError(Exception):
    def __init__(self, client: "Client", data: dict = {}, auth: Type | None = None):
        from zafiaonline.structures.packet_data_keys import PacketDataKeys


        self.client = client
        self.auth = auth

        # Ensure data is not None before accessing it
        reason: str = data[PacketDataKeys.REASON.value]

        if self.auth is None or self.client is None:
            raise AttributeError
        if not self.auth.user or not self.client.user:
            raise AttributeError
        username = (self.client.user.username or self.auth.user.username or
                    "UnknownUser")
        time: str | int = data[PacketDataKeys.TIME_SEC_REMAINING.value]
        ban_time_seconds: int = int(time)

        ban_time = round(ban_time_seconds / 3600, 1)

        message = (f"{username} have been banned due to {reason}, "
                   f"remaining lockout {ban_time} hours")
        super().__init__(message)

class LoginError(Exception):
    pass
