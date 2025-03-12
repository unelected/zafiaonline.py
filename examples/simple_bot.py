# simple mafia online bot
import asyncio

from zafiaonline.utils.exceptions import ListenExampleErrorException
from zafiaonline.main import Client
from zafiaonline.structures import PacketDataKeys

async def main():
    user_agreement = input("[en] send messages may ban you, do you accept "
                           "this? if "
                      "don't "
                "accept you'll use only chat listener\n"
                "if you agree, write yes: \n\n"
                "[ru] отправка сообщений может заблокировать аккаунт, "
                           "принимаешь "
                "ли ты это? если нет то будет доступна только прослушка чата\n"
                "если ты согласен то введи да: ")
    
    Mafia = Client()
    await Mafia.sign_in("email", "password")

    await Mafia.join_global_chat()  # join global chat

    while True:
        try:
            result = await Mafia.listen() # try listen data for result
        except ListenExampleErrorException as e:
            print("listen error", e)
            continue

        if result[
            PacketDataKeys.TYPE] == PacketDataKeys.MESSAGE:  # if new message
            message = result[PacketDataKeys.MESSAGE]
            message_type = message[PacketDataKeys.MESSAGE_TYPE]

            if message_type == 1:  # if message type "text"
                uu = message[PacketDataKeys.USER]  # message user info
                content = message[PacketDataKeys.TEXT] # get text

                user_id = uu[PacketDataKeys.OBJECT_ID] # get sender id
                user_name = uu[PacketDataKeys.USERNAME] # get sender nickname

                print(f"[{user_name}]: {content}") # print nickname
                # with message

                if user_id != Mafia.id: # id sameness check
                    send_content = content # in id with sender and you are
                    # not the same content will send
                else:
                    send_content = None

                if user_agreement in ("yes", "да"):
                    if send_content: # if have content
                        await Mafia.send_message_global(
                            send_content)  # send message to global chat

logging.basicConfig(level=logging.INFO)
asyncio.run(main())
