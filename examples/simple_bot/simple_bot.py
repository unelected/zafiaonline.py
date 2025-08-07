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

import asyncio
import logging
import os

from dotenv import load_dotenv
from zafiaonline.api_client.api_decorators import ApiDecorators
from zafiaonline.utils.exceptions import ListenExampleErrorException
from zafiaonline.main import Client


class AccountData: 
    EMAIL: str = os.getenv("EMAIL") or "email"
    PASSWORD: str = os.getenv("PASSWORD") or "password"
    print(EMAIL, PASSWORD)

class Main:
    @staticmethod
    async def main():
        messages_handle, user_agreement = await Main.prepare_classes()
        user_agreement.show_user_agreement()
        await Mafia.sign_in(AccountData.EMAIL, AccountData.PASSWORD)
        await Mafia.join_global_chat()  # join in global chat
        await messages_handle.chat_handle()

    @staticmethod
    async def prepare_classes():
        user_agreement = UserAgreement()
        messages_handle = MessagesHandle()
        return messages_handle, user_agreement


class MessagesHandle:
    USER_NAME = None
    USER_ID = None
    def __init__(self):
        self.user_name = None
        self.user_id = None

    async def chat_handle(self):
        while True:
            try:
                result = await Mafia.listen()  # try listen data for result
            except Exception as e:
                logging.error(f"listen error {e}")
                raise ListenExampleErrorException

            processed_result = self.message_handle(content = result)
            if processed_result is not None:
                await processed_result


    @ApiDecorators.extract_message  # get text message data
    async def message_handle(self, content):
        user_agreement, utils = await self.prepare_classes()
        await self.set_sender_data()
        utils.log_message(content)
        send_content = self.get_content_of_other_players(content)
        if user_agreement.user_agreement_is_confirmed() and send_content:
            await Mafia.send_message_global(
                send_content)  # send message to global chat

    async def set_sender_data(self):
        MessagesHandle.USER_NAME = self.user_name
        MessagesHandle.USER_ID = self.user_id

    @staticmethod
    async def prepare_classes():
        user_agreement = UserAgreement()
        utils = Utils()
        return user_agreement, utils

    @staticmethod
    def get_content_of_other_players(content):
        message_handle = MessagesHandle()
        if message_handle.USER_ID != Mafia.user.user_id:  # id sameness check
            send_content = content  # in id with sender and you are
            # not the same content will send
        else:
            send_content = None
        return send_content


class Utils:
    @staticmethod
    def log_message(content):
        message_handle = MessagesHandle()
        print(f"[{message_handle.USER_NAME}]: {content}") # print nickname with
        # message


class UserAgreement:
    USER_AGREEMENT = None

    @staticmethod
    def show_user_agreement():
        UserAgreement.USER_AGREEMENT = input("[en] send messages may ban "
                                             "you, do you accept this? "
                                    "if don't accept you'll use only "
                                    "chat listener\n"
                                    "if you agree, write yes: \n\n"
                                    "[ru] отправка сообщений может "
                                    "заблокировать аккаунт, "
                                    "принимаешь ли ты это? если нет то "
                                    "будет доступна только прослушка чата\n"
                                    "если ты согласен то введи да: ")
        print("\n\n\n")

    @staticmethod
    def user_agreement_is_confirmed():
        user_agreement = UserAgreement()
        return (user_agreement.USER_AGREEMENT == "yes" or
                user_agreement.USER_AGREEMENT == "да")


if __name__ == "__main__":
    load_dotenv("example.env")
    Mafia = Client()
    main = Main()
    try:
        asyncio.run(main.main())
    except KeyboardInterrupt:
        pass
