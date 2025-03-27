import re

from zafiaonline.utils.logging_config import logger


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