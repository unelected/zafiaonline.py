from zafiaonline.ApiClient.user_methods import Auth


class ListenDataException(Exception):
    """
    Raised when an error occurs while receiving data from the WebSocket
    listener.

    This exception is typically used to indicate unexpected issues during the
    WebSocket message listening process, such as malformed data, timeouts, or
    disconnections that were not handled properly.
    """

    def __init__(self, message="An error occurred while receiving data from "
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

    def __init__(self, message="An example listening error occurred."):
        super().__init__(message)

class BanError(Exception):
    def __init__(self, event=None):
        from zafiaonline import Client  # Ensure correct import
        from zafiaonline.structures.packet_data_keys import PacketDataKeys

        # Ensure event is not None before accessing it
        reason = event[PacketDataKeys.REASON] if event else "unknown reason"
        username = Client().user.username if (Client().user or Auth().user.
                                              username) else "Unknownser"

        message = f"{username}, You have been banned due to {reason}"
        super().__init__(message)

        # Disconnect the client
        Client().disconnect()
