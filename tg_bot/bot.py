

import logging
import aiohttp
import hashlib
import hmac
import time
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


def generate_telegram_hash(auth_data: dict, bot_token: str) -> str:
    """
    Generate Telegram WebApp authentication hash
    To'g'ri Telegram hash generation algoritmi
    """
    # Data check string yaratish (sorted keys)
    data_check_arr = [f"{k}={v}" for k, v in sorted(auth_data.items())]
    data_check_string = '\n'.join(data_check_arr)

    # Secret key yaratish
    secret_key = hmac.new(
        key="WebAppData".encode(),
        msg=bot_token.encode(),
        digestmod=hashlib.sha256
    ).digest()

    # Hash yaratish
    hash_value = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    logger.info(f"Generated Telegram hash: {hash_value}")
    return hash_value


@dp.message(CommandStart())
async def start_handler(message: Message):
    user = message.from_user
    telegram_id = user.id
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    username = user.username or ""

    logger.info(f"Start command from user {telegram_id} ({username or first_name})")

    # Telegram auth data yaratish (Django backend kutgan format)
    # Faqat bo'sh bo'lmagan qiymatlarni qo'shamiz
    auth_data = {
        'id': telegram_id,
        'auth_date': int(time.time()),
    }

    # Bo'sh bo'lmagan maydonlarni qo'shish
    if first_name:
        auth_data['first_name'] = first_name
    if last_name:
        auth_data['last_name'] = last_name
    if username:
        auth_data['username'] = username

    # Hash yaratish
    auth_hash = generate_telegram_hash(auth_data.copy(), BOT_TOKEN)

    # Hash ni auth_data ga qo'shish
    auth_data['hash'] = auth_hash

    # Mini app URL (agar kerak bo'lsa)
    # mini_app_url = f"https://yourdomain.com/miniapp?..."

    # Inline keyboard (ixtiyoriy - agar web app kerak bo'lsa)
    # keyboard = InlineKeyboardMarkup(inline_keyboard=[
    #     [InlineKeyboardButton(
    #         text="🛒 Open Marketplace",
    #         web_app=WebAppInfo(url=mini_app_url)
    #     )]
    # ])

    # Django backend ga registration/login so'rovi
    logger.info(f"Sending auth data to Django: {auth_data}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    f"{API_URL}/user/auth/telegram/",  # To'g'ri endpoint
                    json=auth_data,
                    headers={'Content-Type': 'application/json'}
            ) as resp:
                response_text = await resp.text()
                logger.info(f"API Response Status: {resp.status}")
                logger.info(f"API Response Body: {response_text[:500]}")  # First 500 chars

                if resp.status == 200:
                    try:
                        response_data = await resp.json()

                        # Response dan ma'lumotlarni olish
                        success = response_data.get('success')
                        created = response_data.get('created')
                        user_data = response_data.get('user', {})
                        tokens = response_data.get('tokens', {})
                        access_token = tokens.get('access')
                        refresh_token = tokens.get('refresh')

                        if success:
                            user_name = user_data.get('name', first_name)

                            if created:
                                # Yangi user yaratildi
                                logger.info(f"New user created: {telegram_id}")
                                await message.answer(
                                    f"🎉 Welcome to Marketplace, <b>{user_name}</b>!\n\n"
                                    f"✅ Your account has been created successfully.\n"
                                    f"🔐 You are now logged in.\n\n"
                                    f"Use /menu to explore the marketplace."
                                )
                            else:
                                # Mavjud user login qildi
                                logger.info(f"Existing user logged in: {telegram_id}")
                                await message.answer(
                                    f"👋 Welcome back, <b>{user_name}</b>!\n\n"
                                    f"✅ You are now logged in.\n\n"
                                    f"Use /menu to explore the marketplace."
                                )

                            # Token'larni saqlash (ixtiyoriy - bot uchun kerak bo'lmasligi mumkin)
                            # Agar kerak bo'lsa, database yoki cache'ga saqlang
                            logger.info(f"Access token received for user {telegram_id}")

                        else:
                            logger.warning(f"Authentication failed for user {telegram_id}")
                            await message.answer(
                                "⚠️ Authentication failed. Please try again with /start"
                            )

                    except Exception as json_error:
                        logger.error(f"Error parsing JSON response: {json_error}")
                        logger.error(f"Raw response: {response_text}")
                        await message.answer(
                            "⚠️ Server error. Please try again later."
                        )

                else:
                    logger.warning(f"Authentication failed with status {resp.status}")
                    logger.warning(f"Response: {response_text[:500]}")
                    await message.answer(
                        "⚠️ Authentication failed. Please try again with /start"
                    )

        except aiohttp.ClientError as e:
            logger.error(f"Network error during authentication: {e}")
            await message.answer(
                "⚠️ Network error. Please check your connection and try /start again."
            )
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}", exc_info=True)
            await message.answer(
                "⚠️ An unexpected error occurred. Please try /start again."
            )


@dp.message()
async def echo_handler(message: Message):
    """
    Echo handler for all other messages
    """
    await message.answer(
        "👋 Hi! Use /start to begin.\n\n"
        "Available commands:\n"
        "/start - Register or login"
    )


# Run bot
async def main():
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())