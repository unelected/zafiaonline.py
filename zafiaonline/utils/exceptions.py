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

    This exception is useful for handling controlled test failures, debugging, or
    identifying particular patterns in received messages that need special
    handling.
    """

    def __init__(self, message="An example listening error occurred."):
        super().__init__(message)
