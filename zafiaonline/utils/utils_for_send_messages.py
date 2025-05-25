import re
import time
from datetime import datetime
from typing import Type, List, TypedDict, Optional

from zafiaonline.utils.logging_config import logger

class Message(TypedDict):
    message_time: str
    text: str

class Utils:
    @staticmethod
    def clean_content(content):
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
    def add_sent_messages_list() -> Type:
        #TODO расширить класс, сделать класс без костыля
        class SentMessages:
            def __init__(self, enable_logging: bool = False):
                self.messages: List[Message] = []
                self.logged_messages: List[Message] = []
                self.enable_logging = enable_logging


            def add_message(self, message: str) -> None:
                message_time = self.get_time()
                self.messages.append({"message_time": message_time, "text":
                    message})
                if self.enable_logging:
                    self.logged_messages.append({"message_time":
                                        message_time, "text": message})

            @staticmethod
            def get_time() -> str:
                message_time = datetime.now().strftime("%H:%M:%S")
                return message_time

            def get_last_messages(self) -> List[Message]:
                return self.messages

            def clear_last_messages(self) -> None:
                self.messages.clear()

            def get_length_last_messages(self) -> Optional[int]:
                if self.messages:
                    return len(self.messages)
                raise ValueError("List messages is None")

            def delete_first_message_in_list(self) -> None:
                if self.messages:
                    self.messages.pop(0)

            def get_logged_messages(self) -> None:
                return self.logged_messages

        return SentMessages

    @staticmethod
    def get_time_messages(messages: List[Message]) -> List[str]:
        if not messages:
            raise ValueError("Argument 'messages' is None or empty list.")
        messages_time: List[str] = []
        for message in messages:
            message_time = message.get("message_time", None)
            if message_time is None:
                raise ValueError("Argument 'message_time' in 'message' is "
                                 "not found")
            messages_time.append(message_time)
        return messages_time

    async def auto_delete_first_last_message(self, messages: List[Message],
                                             cls):
        time_messages = self.get_time_messages(messages)
        average_time = sum(time_messages)/len(time_messages)
        if average_time == 2 and len(messages) >= 6:
            logger.warning("anti-ban: ban protection, sent too many messages"
                           "\nwait 2 seconds")
            time.sleep(2)
            cls.clear_last_messages()

        

    @staticmethod
    def is_ban_risk_message(sent_messages_class: Type) -> bool:
        #TODO add time
        sent_messages = sent_messages_class()
        if sent_messages.get_length_messages == 6: #and time
            logger.warning("AntiLegShotProtection prevented autoban")
            return True
        return False
