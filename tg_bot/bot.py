# import logging
# import aiohttp
# from aiogram import Bot, Dispatcher, types
# from aiogram.enums import ParseMode
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.types import Message
# from aiogram.filters import CommandStart
# from aiogram.client.default import DefaultBotProperties
# from tg_bot.tokens import *
#
#
# logging.basicConfig(level=logging.INFO)
#
#
# bot = Bot(
#     token=BOT_TOKEN,
#     default=DefaultBotProperties(parse_mode=ParseMode.HTML)
# )
# dp = Dispatcher(storage=MemoryStorage())
#
# # /start command
# @dp.message(CommandStart())
# async def start_handler(message: Message):
#     user = message.from_user
#     telegram_id = user.id
#     username = user.username or f"{user.first_name} {user.last_name or ''}".strip()
#
#     await message.answer(f"👋 Welcome, <b>{username}</b>!")
#
#     # Send data to backend
#     async with aiohttp.ClientSession() as session:
#         data = {
#             "telegram_id": telegram_id,
#             "name": username,
#         }
#         try:
#             async with session.post(API_URL, data=data) as resp:
#                 if resp.status in (200, 201):
#                     logging.info("User registered successfully.")
#                 else:
#                     logging.warning(f"Registration failed: {await resp.text()}")
#         except Exception as e:
#             logging.error(f"Error posting data: {e}")
#
# # Run bot
# async def main():
#     await dp.start_polling(bot)
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())


import logging
import aiohttp
import hashlib
import hmac
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from tg_bot.tokens import *

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())


def generate_auth_hash(telegram_id: int, username: str) -> str:
    """Generate a secure hash for mini app authentication"""
    # Use bot token as secret key for HMAC
    secret = BOT_TOKEN.split(':')[1]  # Get the secret part of bot token
    data = f"{telegram_id}:{username}"
    return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()


@dp.message(CommandStart())
async def start_handler(message: Message):
    user = message.from_user
    telegram_id = user.id
    username = user.username or f"{user.first_name} {user.last_name or ''}".strip()

    # Generate auth hash for mini app
    auth_hash = generate_auth_hash(telegram_id, username)

    # Create mini app URL with user data
    mini_app_url = f"https://yourdomain.com/miniapp?user_id={telegram_id}&username={username}&auth_hash={auth_hash}"

    # Create inline keyboard with mini app button
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛒 Open Marketplace",
            web_app=WebAppInfo(url=mini_app_url)
        )]
    ])

    await message.answer(
        f"👋 Welcome to the Marketplace, <b>{username}</b>!\n"
        f"Click the button below to start buying and selling:",
        reply_markup=keyboard
    )

    # Register user and get JWT token
    async with aiohttp.ClientSession() as session:
        data = {
            "telegram_id": telegram_id,
            "name": username,
            "auth_hash": auth_hash  # Send auth hash for verification
        }
        try:
            async with session.post(f"{API_URL}/user/register/", json=data) as resp:
                if resp.status in (200, 201):
                    response_data = await resp.json()
                    jwt_token = response_data.get('jwt_token')
                    logging.info(f"User {telegram_id} registered with JWT token")
                else:
                    logging.warning(f"Registration failed: {await resp.text()}")
        except Exception as e:
            logging.error(f"Error posting data: {e}")


# Run bot
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())