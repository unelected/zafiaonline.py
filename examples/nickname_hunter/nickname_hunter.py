import asyncio
import logging

from zafiaonline.structures import PacketDataKeys
from zafiaonline.main import Client

from models import entertainers, trackeds

"""
    Script powered by zakovskiy && forked by unelected
"""
async def main_function():
    await main.create_connection()
    while True:
        await check_accounts()
        await asyncio.sleep(.5)

class SearchPlayerError(Exception):
    """error open user profile"""
    pass

async def check_accounts() -> None:
    for i in range(len(trackeds)):
        try:
            tracked = trackeds[i]
        except Exception as e:
            logging.error(f"ошибка {e}")
            continue
        account = await get_account(tracked)
        if account is None:
            continue

        try:
            nickname = account.get(PacketDataKeys.USER)[
                PacketDataKeys.USERNAME]
            if not nickname:
                continue

        except Exception as e:
            logging.critical(f"username in account does not exist, {e}")
            raise

        if tracked[1] == "":
            trackeds[i][1] = nickname
            logging.info(f"nickname: {nickname}")
            logging.info('~set nickname')

        elif nickname != tracked[1]: # if nickname is not old nickname
            await enter_nickname(tracked[1])
            del trackeds[i]
        await asyncio.sleep(2)
    trackeds[:] = [t for t in trackeds if t is not None]

async def fetch_user(user_id):
    """Запрашивает данные пользователя по user_id."""
    try:
        return await main.get_user(user_id)
    except (ValueError, SearchPlayerError) as e:
        return await handle_search_error(e)

async def handle_search_error(error):
    """Обрабатывает ошибку поиска игрока, логирует её и делает задержку перед повторной попыткой."""
    logging.error(f"Ошибка при поиске игрока: {error}")
    await asyncio.sleep(10)
    return None

async def get_account(tracked):
    """Получает аккаунт пользователя, обрабатывает ошибки и возвращает результат."""
    if not tracked:
        logging.error("Список tracked пуст, невозможно получить пользователя")
        return None

    return await fetch_user(tracked[0])


async def sign_in_with_entertainer(index: int) -> None:
    """Авторизуется с указанной учетной записью из списка entertainers."""
    if not entertainers:
        logging.error("Нет доступных учетных записей")
        return

    if 0 <= index <= len(entertainers):
        await main.sign_in(entertainers[index][0], entertainers[index][1])
        del entertainers[index]
    else:
        logging.error("Попытка входа с несуществующей учетной записью")

async def set_nickname(nickname: str) -> None:
    """Устанавливает ник пользователя и логирует его."""
    await main.username_set(nickname)
    logging.info(f"Заняли ник {nickname}")

async def enter_nickname(nickname: str) -> None:
    """Ищет индекс для аккаунта по нику игрока."""
    # if nickname == "just example for you":
    #    index = 0
    #else:
    #    index = 1
    index = 0

    await sign_in_with_entertainer(index)
    await set_nickname(nickname)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        datefmt="%H:%M:%S")
    main = Client()

    try:
        asyncio.run(main_function())
    except KeyboardInterrupt:
        logging.info("успешный выход из программы")
