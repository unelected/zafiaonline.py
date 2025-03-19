# simple mafia online bot
import asyncio
import logging

from zafiaonline.utils import ApiDecorators
from zafiaonline.utils.exceptions import ListenExampleErrorException
from zafiaonline.main import Client


class Main:
    def __init__(self):
        self.user_agreement = None
        self.user_id = None
        self.user_name = None

    async def main(self):
        self.user_agreement = input("[en] send messages may ban you, do you "
                                 "accept "
                               "this? if "
                          "don't "
                    "accept you'll use only chat listener\n"
                    "if you agree, write yes: \n\n"
                    "[ru] отправка сообщений может заблокировать аккаунт, "
                               "принимаешь "
                    "ли ты это? если нет то будет доступна только прослушка чата\n"
                    "если ты согласен то введи да: ")
        print("\n\n\n")

        await Mafia.sign_in("email", "password")

        await Mafia.join_global_chat()  # join in global chat

        while True:
            try:
                result = await Mafia.listen() # try listen data for result
            except ListenExampleErrorException as e:
                print("listen error", e)
                continue

            await self.message_handle(result)

    @ApiDecorators.extract_message
    async def message_handle(self, content):
        print(f"[{self.user_name}]: {content}")  # print nickname
        # with message
        if self.user_id != Mafia.id:  # id sameness check
            send_content = content  # in id with sender and you are
            # not the same content will send
        else:
            send_content = None
        if self.user_agreement == "yes" or self.user_agreement == "да":
            if send_content:  # have content
                await Mafia.send_message_global(
                    send_content)  # send message to global chat


if __name__ == "__main__":
    Mafia = Client()
    main = Main()
    try:
        asyncio.run(main.main())
    except KeyboardInterrupt:
        logging.info("программа завершена выходом из программы")
