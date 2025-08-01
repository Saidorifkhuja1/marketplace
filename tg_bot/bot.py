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

# Enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())


def generate_auth_hash(telegram_id: int, username: str) -> str:
    """Generate a secure hash for mini app authentication"""
    secret = BOT_TOKEN.split(':')[1]
    data = f"{telegram_id}:{username}"
    hash_value = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
    logger.info(f"Generated hash for {telegram_id}:{username} = {hash_value}")
    return hash_value


@dp.message(CommandStart())
async def start_handler(message: Message):
    user = message.from_user
    telegram_id = user.id
    username = user.username or f"{user.first_name} {user.last_name or ''}".strip()

    logger.info(f"Start command from user {telegram_id} ({username})")

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
    registration_data = {
        "telegram_id": telegram_id,
        "name": username,
        "auth_hash": auth_hash
    }

    logger.info(f"Sending registration data: {registration_data}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    f"{API_URL}/user/register/",
                    json=registration_data,
                    headers={'Content-Type': 'application/json'}
            ) as resp:
                response_text = await resp.text()
                logger.info(f"API Response Status: {resp.status}")
                logger.info(f"API Response Body: {response_text}")

                if resp.status in (200, 201):
                    try:
                        response_data = await resp.json()
                        jwt_token = response_data.get('jwt_token')
                        logger.info(f"User {telegram_id} registered successfully with JWT token")
                    except Exception as json_error:
                        logger.error(f"Error parsing JSON response: {json_error}")
                        logger.error(f"Raw response: {response_text}")
                else:
                    logger.warning(f"Registration failed with status {resp.status}: {response_text}")
                    # Send error message to user
                    await message.answer("⚠️ Registration failed. Please try again later.")

        except aiohttp.ClientError as e:
            logger.error(f"Network error during registration: {e}")
            await message.answer("⚠️ Network error. Please check your connection and try again.")
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}")
            await message.answer("⚠️ An unexpected error occurred. Please try again.")


# Run bot
async def main():
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())