import asyncio
from typing import TYPE_CHECKING

from zafiaonline.structures import PacketDataKeys
from zafiaonline.structures.enums import MessageStyles
from zafiaonline.utils.utils import get_user_attributes
from zafiaonline.utils.utils_for_send_messages import Utils, SentMessages


class GlobalChat:
    if TYPE_CHECKING:  # Импорт выполняется только для аннотации типов
        from zafiaonline.api_client.user_methods import Auth
    def __init__(self, client: "Auth"):
        self.client = client
        if self.client:
            get_user_attributes(self.client)
        self.sent_messages: "SentMessages" = SentMessages()

    async def send_server(self, data, remove_token_from_object = False):
        await self.client.send_server(data, remove_token_from_object)

    async def join_global_chat(self) -> None:
        """
        Sends a request to join the global chat.

        This function allows the client to enter the global chat and receive
        messages from other users.

        Returns:
            None
        """
        chat_join_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_CHAT
        }
        await self.send_server(chat_join_request)

    async def leave_from_global_chat(self) -> None:
        """
        Sends a request to add the client to the dashboard.

        This function requests the server to place the client on the
        dashboard, typically used for accessing account-related information
        or lobby interactions.

        Returns:
            None
        """
        leave_from_chat_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_DASHBOARD
        }
        await self.send_server(leave_from_chat_request)


    async def send_message_global(self, content: str, message_style: int =
                                MessageStyles.NO_COLOR) -> None:
        """
        Sends a message to the global chat.

        Parameters:
            content (str): The text of the message to be sent.
            message_style (int, optional): The style of the message.
            Defaults to 0.

        Returns:
            None

        Notes:
            - If the content is empty, the function prevents sending to
            avoid spam or bans.
        """
        utils: "Utils" = Utils()
        if not utils.validate_message_content(content):
            return None
        content = utils.clean_content(content)
        self.sent_messages.add_message(content)
        utils.auto_delete_first_message(self.sent_messages)
        if utils.is_ban_risk_message(self.sent_messages) is True:
            await asyncio.sleep(5)
            return None

        message_data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.CHAT_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.TEXT: content,
                PacketDataKeys.MESSAGE_STYLE: message_style,
            }
        }
        await self.send_server(message_data)
        return None
