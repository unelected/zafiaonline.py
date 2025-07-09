import asyncio
import json

from typing import List, Optional, Dict, Any, TYPE_CHECKING
from msgspec.json import decode

if TYPE_CHECKING:
    from zafiaonline.api_client.user_methods import Auth
from zafiaonline.structures.packet_data_keys import PacketDataKeys
from zafiaonline.structures.models import ModelFriend, ModelMessage
from zafiaonline.structures.enums import RatingMode, RatingType
from zafiaonline.utils.utils import get_user_attributes
from zafiaonline.utils.utils_for_send_messages import Utils, SentMessages
from zafiaonline.utils.logging_config import logger


class Players:
    def __init__(self, client: "Auth"):
        self.client = client
        if self.client:
            get_user_attributes(self.client)
        self.sent_messages = SentMessages()

    async def send_server(self, data, remove_token_from_object = False):
        await self.client.send_server(data, remove_token_from_object)

    async def listen(self):
        return await self.client.listen()

    async def get_data(self, data):
        return await self.client.get_data(data)

    async def friend_list(self) -> List[ModelFriend]:
        """
        Retrieves the user's friend list.

        Returns:
            List[ModelFriend]: A list of friends as ModelFriend objects.
        """
        friends_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_FRIENDSHIP_LIST
        }
        await self.send_server(friends_request)

        await asyncio.sleep(.01)
        received_data: dict | None = await self.get_data(PacketDataKeys.FRIENDSHIP_LIST)
        if received_data is None:
            raise AttributeError

        friends: List[ModelFriend] = []

        for friend in received_data[PacketDataKeys.FRIENDSHIP_LIST]:
            friends.append(decode(json.dumps(friend), type = ModelFriend))
        return friends

    async def get_friend_invite_list(self):
        get_invite_list_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_FRIENDS_IN_INVITE_LIST
        }
        await self.send_server(get_invite_list_request)
        await asyncio.sleep(.01)
        return await self.get_data(PacketDataKeys.FRIENDS_IN_INVITE_LIST)

    async def invite_friend(self, player_id: str):
        invite_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.SEND_FRIEND_INVITE_TO_ROOM,
            PacketDataKeys.USER_OBJECT_ID: player_id
        }
        await self.send_server(invite_request)
        await asyncio.sleep(.1)
        return await self.get_data(PacketDataKeys.FRIEND_IS_INVITED)

    async def search_player(self, nickname: str) -> dict | None:
        """
        Searches for a player by their nickname.

        Parameters:
            nickname (str): The nickname of the player to search for.

        Returns:
            dict: The search result data.
        """
        search_info_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.SEARCH_USER,
            PacketDataKeys.SEARCH_TEXT: nickname
        }
        await self.send_server(search_info_request)
        await asyncio.sleep(.01)
        return await self.get_data(PacketDataKeys.SEARCH_USER)

    async def remove_friend(self, friend_id: str) -> None:
        """
        Removes a friend from the user's friend list.

        Parameters:
            friend_id (str): The unique identifier of the friend to remove.

        Returns:
            None
        """
        remove_friend_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.REMOVE_FRIEND,
            PacketDataKeys.FRIEND_USER_OBJECT_ID: friend_id
        }
        await self.send_server(remove_friend_request)

    async def kick_user_vote(self, room_id: str, value: bool = True) -> None:
        """
        Sends a vote request to kick a user from the room.

        Parameters:
            room_id (str): The unique identifier of the room.
            value (bool, optional): The vote decision.
            Defaults to True (vote to kick).

        Returns:
            None
        """
        vote_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.KICK_USER_VOTE,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.VOTE: value
        }
        await self.send_server(vote_request)

    async def kick_user(self, user_id: str, room_id: str) -> None:
        """
        Sends a request to kick a user from the specified room.

        Parameters:
            user_id (str): The unique identifier of the user to be kicked.
            room_id (str): The unique identifier of the room.

        Returns:
            None
        """
        kick_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.KICK_USER,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.USER_OBJECT_ID: user_id
        }
        await self.send_server(kick_request)

    async def message_complaint(self, reason: str, screenshot_id: int,
                                user_id: str) -> dict | None:
        """
        Submits a complaint about a user's message.

        This method allows users to report inappropriate messages by
        specifying a reason
        and attaching a screenshot.

        Parameters:
            reason (str): The reason for the complaint.
            screenshot_id (int): The ID of the uploaded screenshot.
                Obtained from update_photo_server().
            user_id (str): The ID of the user being reported.

        Returns:
            dict: The server response to the complaint request.
        """
        complaint_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MAKE_COMPLAINT,
            PacketDataKeys.USER_OBJECT_ID: user_id,
            PacketDataKeys.REASON: reason,
            PacketDataKeys.SCREENSHOT: screenshot_id
            # Retrieved from update_photo_server()
        }
        await self.send_server(complaint_request)
        return await self.listen()

    async def get_private_messages(self, friend_id: str) -> List[ModelMessage]:
        """
        Retrieves the list of private messages exchanged with a specific
        friend.

        Parameters:
            friend_id (str): The unique identifier of the friend.

        Returns:
            List[ModelMessage]: A list of private messages.
        """
        private_messages_request: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_PRIVATE_CHAT,
            PacketDataKeys.FRIENDSHIP: friend_id
        }
        await self.send_server(private_messages_request)

        await asyncio.sleep(.01)
        received_messages: dict | None = await self.get_data(
            PacketDataKeys.PRIVATE_CHAT_LIST_MESSAGES
        )
        if received_messages is None:
            raise AttributeError

        messages: List[ModelMessage] = [
            decode(json.dumps(message), type=ModelMessage)
            for message in received_messages[PacketDataKeys.MESSAGES]
        ]

        return messages

    async def get_rating(self, rating_type: RatingType =
                        RatingType.AUTHORITY,
                        rating_mode: RatingMode = RatingMode.ALL_TIME) -> dict | None:
        """
        Retrieves the player rating based on the specified type and mode.

        Parameters:
            rating_type (RatingType): The type of rating to retrieve.
                Defaults to RatingType.AUTHORITY.
            rating_mode (RatingMode): The time period for the rating.
                Defaults to RatingMode.ALL_TIME.

        Returns:
            dict: A dictionary containing the rating data.
        """
        rating_query: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_RATING,
            PacketDataKeys.RATING_TYPE: rating_type,
            PacketDataKeys.RATING_MODE: rating_mode
        }
        await self.send_server(rating_query)
        await asyncio.sleep(.01)
        return await self.get_data(PacketDataKeys.RATING)

    async def send_message_friend(self, friend_id: str, content: str) -> None:
        """
        Sends a private message to a friend.

        Parameters:
            friend_id (str): The unique identifier of the friend.
            content (str): The message text to be sent.

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
            PacketDataKeys.TYPE: PacketDataKeys.PRIVATE_CHAT_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.FRIENDSHIP: friend_id,
                PacketDataKeys.TEXT: content
            }
        }
        await self.send_server(message_data)
        return None

    async def get_user(self, user_id: str) -> Optional[dict]:
        """
        Retrieves the profile data of a specific user.

        Parameters:
            user_id (str): The unique identifier of the user.

        Returns:
            Optional[dict]: The user's profile data if successfully
            retrieved, otherwise None.

        Raises:
            Exception: If an unexpected error occurs while fetching the data.

        Notes:
            - Logs an error if no data is returned.
            - Uses exception handling to catch and log potential failures.
        """
        user_payload: Dict[str, Any] = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_USER_PROFILE,
            PacketDataKeys.USER_RECEIVER: user_id,
            PacketDataKeys.USER_OBJECT_ID: self.client.user.user_id,
        }
        await self.send_server(user_payload)

        try:
            user_data: dict | None = await self.get_data(PacketDataKeys.USER_PROFILE)
            if not user_data:
                logger.error(f"Error: get_data returned {user_data}")
                return None
            return user_data
        except Exception as e:
            logger.error(f"Error retrieving user {user_id} data: {e}",
                          exc_info = True)
            return None
