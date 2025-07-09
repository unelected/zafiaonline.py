import re
from datetime import datetime
from typing import List, TypedDict

from zafiaonline.utils.logging_config import logger


class Message(TypedDict):
    message_time: datetime
    text: str

class SentMessages:
    # TODO расширить класс
    def __init__(self, enable_logging: bool = False):
        self.messages: List[Message] = []
        self.logged_messages: List[Message] = []
        self.enable_logging: bool = enable_logging

    def add_message(self, message: str) -> None:
        message_time: datetime = self.get_time()
        self.messages.append({"message_time": message_time, "text":
            message})
        if self.enable_logging:
            self.logged_messages.append({"message_time":
                                             message_time,
                                         "text": message})

    @staticmethod
    def get_time() -> datetime:
        return datetime.now()

    def get_messages(self) -> List[Message]:
        return self.messages

    def clear_messages(self) -> None:
        self.messages.clear()

    def get_length_last_messages(self, max_len: int = 6) -> int:
        if self.messages:
            return len(self.messages[-max_len:])
        raise ValueError("List messages is None")

    def delete_first_message_in_list(self) -> None:
        if self.messages:
            self.messages.pop(0)

    def get_logged_messages(self) -> List[Message]:
        return self.logged_messages

class Utils:
    @staticmethod
    def clean_content(content: str) -> str:
        new_content = content[:200]
        clean_content = re.sub(r'\s+', ' ', new_content)
        return clean_content

    @staticmethod
    def validate_message_content(content: str) -> bool:
        """
        Validates the message content to prevent sending empty messages.

        Parameters:
            content (str): The message content.

        Returns:
            bool: True if the message is valid, False otherwise.
        """
        if not content.strip():
            logger.warning(
                "Anti-ban protection: the message hasn't"
                " been sent because it's blank.")
            return False
        return True

    @staticmethod
    def get_time_of_messages(messages: List[Message]) -> List[datetime]:
        if not messages:
            raise ValueError("Argument 'messages' is None or empty list.")
        messages_time: List[datetime] = []
        for message in messages:
            message_time: datetime | None = message.get("message_time", None)
            if message_time is None:
                raise ValueError("Argument 'message_time' in 'message' is "
                                 "not found")
            messages_time.append(message_time)
        return messages_time

    @staticmethod
    def get_current_time_of_messages(time_list: List[datetime]) -> List[float]:
        out_time_list: List[float] = []
        new_time: float = datetime.now().timestamp()
        for time in time_list:
            out_time: float = new_time - time.timestamp()
            out_time_list.append(out_time)
        return out_time_list

    def auto_delete_first_message(self, handler: SentMessages) -> None:
        average_time: float = self.get_average_time(handler)
        len_messages: int = handler.get_length_last_messages()
        if len_messages >= 10:
            handler.delete_first_message_in_list()
        elif average_time >= 20 and len_messages >= 3:
            handler.clear_messages()
        return None

    def get_average_time(self, handler: SentMessages, max_len = 6) -> float:
        messages: List[Message] =  handler.messages
        time_messages: List[datetime] = self.get_time_of_messages(messages)
        current_time: List[float] = self.get_current_time_of_messages(time_messages[
                                                         -max_len:])
        average_time: float = sum(current_time) / len(current_time)
        return average_time

    def is_ban_risk_message(self, sent_messages_class: SentMessages) -> bool:
        messages: List[Message] = sent_messages_class.messages
        if not messages:
            return False
        short_time: float = self.get_average_time(sent_messages_class)
        long_time: float = self.get_average_time(sent_messages_class, max_len = 9)
        if (sent_messages_class.get_length_last_messages() >= 6 and short_time <=
                2.1) or (sent_messages_class.get_length_last_messages(
            max_len = 20) >= 9 and long_time <= 3):
            logger.warning("AntiBanProtection prevented autoban")
            return True
        return False
