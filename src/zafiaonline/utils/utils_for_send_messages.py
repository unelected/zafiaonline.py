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
Provides anti-ban protection and message tracking utilities for chat bots.

This module includes logic for handling sent messages, measuring time intervals
between them, and applying rules to avoid triggering automated bans on platforms
with rate-limiting or spam detection systems.

It includes the `SentMessages` class for storing and managing message history,
as well as utility functions for validating message content, calculating
average time deltas, and detecting suspicious behavior.

Typical usage example:

  messages = SentMessages(enable_logging=True)
  messages.add_message("hello world")
  if antiban.is_ban_risk_message(messages):
      print("Slow down to avoid ban.")
"""
import re
from datetime import datetime
from typing import List, TypedDict

from zafiaonline.utils.logging_config import logger


class Message(TypedDict):
    """
    Represents a single text message with a timestamp.

    Attributes:
        message_time (datetime): The time when the message was created or sent.
        text (str): The textual content of the message.
    """
    message_time: datetime
    text: str



# TODO: @unelected - расширить класс
class SentMessages:
    """
    Manages sent messages with optional logging.

    Attributes:
        messages (List[Message]): All messages that have been sent.
        logged_messages (List[Message]): Messages that have been logged.
        enable_logging (bool): Whether to store messages in the log list.
    """
    def __init__(self, enable_logging: bool = False):
        """
        Initializes a SentMessages instance.

        Args:
            enable_logging (bool, optional): Whether to enable logging of messages.
                If True, sent messages will also be stored in `logged_messages`.
                Defaults to False.
        """
        self.messages: List[Message] = []
        self.logged_messages: List[Message] = []
        self.enable_logging: bool = enable_logging

    def add_message(self, message: str) -> None:
        """
        Adds a message to the internal storage with a timestamp.

        The message is added to `messages`, and if logging is enabled, also
        to `logged_messages`.

        Args:
            message (str): The message text to store.
        """
        message_time: datetime = self.get_time()
        self.messages.append({"message_time": message_time, "text":
            message})
        if self.enable_logging:
            self.logged_messages.append({"message_time":
                                             message_time,
                                         "text": message})

    @staticmethod
    def get_time() -> datetime:
        """
        Returns the current local date and time.

        Returns:
            datetime: The current local datetime object.
        """
        return datetime.now()

    def get_messages(self) -> List[Message]:
        """
        Returns a list of all recorded messages.

        Returns:
            List[Message]: A list of messages stored in the instance.
        """
        return self.messages

    def clear_messages(self) -> None:
        """
        Clears all stored messages.

        This method removes all messages from the internal `messages` list.
        """
        self.messages.clear()

    def get_length_last_messages(self, max_len: int = 6) -> int:
        """
        Returns the number of last messages up to `max_len`.

        Args:
            max_len (int, optional): Maximum number of recent messages to consider. Defaults to 6.

        Returns:
            int: Number of messages in the last `max_len` entries.

        Raises:
            ValueError: If no messages are available.
        """
        if self.messages:
            return len(self.messages[-max_len:])
        raise ValueError("List messages is None")

    def delete_first_message_in_list(self) -> None:
        """
        Deletes the first message from the list, if it exists.

        Does nothing if the message list is empty.
        """
        if self.messages:
            self.messages.pop(0)

    def get_logged_messages(self) -> List[Message]:
        """
        Returns the list of logged messages.

        Returns:
            List[Message]: A list of messages that were logged.
        """
        return self.logged_messages


class Utils:
    @staticmethod
    def clean_content(content: str) -> str:
        """
        Cleans and truncates a string to 200 characters, replacing multiple spaces with one.

        Args:
            content (str): The input text content.

        Returns:
            str: The cleaned and truncated string.
        """
        new_content = content[:200]
        clean_content = re.sub(r'\s+', ' ', new_content)
        return clean_content

    @staticmethod
    def validate_message_content(content: str) -> bool:
        """
        Checks if the message content is not empty or whitespace.

        Args:
            content (str): The message content to validate.

        Returns:
            bool: True if the message is not blank, False otherwise.
        """
        if not content.strip():
            logger.warning(
                "Anti-ban protection: the message hasn't"
                " been sent because it's blank.")
            return False
        return True

    @staticmethod
    def get_time_of_messages(messages: List[Message]) -> List[datetime]:
        """
        Extracts the message_time field from a list of Message dictionaries.

        Args:
            messages (List[Message]): A list of messages, each with a 'message_time' key.

        Returns:
            List[datetime]: A list of datetime objects extracted from the messages.

        Raises:
            ValueError: If the input list is empty or any message lacks 'message_time'.
        """
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
        """
        Calculates the elapsed time in seconds since each datetime in the list.

        Args:
            time_list (List[datetime]): A list of datetime objects.

        Returns:
            List[float]: A list of time differences (in seconds) between now and each datetime.

        Example:
            If time_list contains datetimes from 5 and 10 seconds ago,
            the returned list will be approximately [5.0, 10.0].
        """
        out_time_list: List[float] = []
        new_time: float = datetime.now().timestamp()
        for time in time_list:
            out_time: float = new_time - time.timestamp()
            out_time_list.append(out_time)
        return out_time_list

    def auto_delete_first_message(self, handler: SentMessages) -> None:
        """
        Automatically deletes or clears messages from the handler based on timing and count.

        Deletes the first message if the number of recent messages is 10 or more.
        Clears all messages if the average time since recent messages exceeds 20 seconds
        and there are at least 3 recent messages.

        Args:
            handler (SentMessages): The message handler that stores and manages messages.

        Returns:
            None
        """
        average_time: float = self.get_average_time(handler)
        len_messages: int = handler.get_length_last_messages()
        if len_messages >= 10:
            handler.delete_first_message_in_list()
        elif average_time >= 20 and len_messages >= 3:
            handler.clear_messages()
        return None

    def get_average_time(self, handler: SentMessages, max_len = 6) -> float:
        """
        Calculates the average age (in seconds) of the most recent messages.

        This function extracts timestamps from the last `max_len` messages stored
        in the handler, computes how much time has passed since each message was sent,
        and returns the average of these time differences.

        Args:
            handler (SentMessages): The message handler containing messages.
            max_len (int, optional): The number of most recent messages to consider. Defaults to 6.

        Returns:
            float: The average time (in seconds) since the selected messages were sent.

        Raises:
            ValueError: If the list of messages is empty or contains messages without valid timestamps.
        """
        messages: List[Message] =  handler.messages
        time_messages: List[datetime] = self.get_time_of_messages(messages)
        current_time: List[float] = self.get_current_time_of_messages(time_messages[
                                                         -max_len:])
        average_time: float = sum(current_time) / len(current_time)
        return average_time

    def is_ban_risk_message(self, sent_messages_class: SentMessages) -> bool:
        """
        Determines whether recent messaging behavior poses a ban risk.

        This method analyzes the frequency of sent messages and determines if the
        message rate is high enough to trigger anti-spam or anti-bot protection.

        Args:
            sent_messages_class (SentMessages): The message handler containing the list of sent messages.

        Returns:
            bool: True if the message rate suggests ban risk, False otherwise.
        """
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
