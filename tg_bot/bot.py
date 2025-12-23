import logging
import aiohttp
import hashlib
import hmac
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
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


# FSM States
class RegistrationStates(StatesGroup):
    waiting_for_phone = State()


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
async def start_handler(message: Message, state: FSMContext):
    """
    /start buyrug'i - telefon raqamini so'raydi
    """
    user = message.from_user
    telegram_id = user.id
    first_name = user.first_name or ""
    username = user.username or ""

    logger.info(f"Start command from user {telegram_id} ({username or first_name})")

    # Telefon raqami uchun keyboard
    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Share Phone Number", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    # State'ga user ma'lumotlarini saqlash
    await state.update_data(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=user.last_name or "",
        username=username
    )

    # Telefon raqamini so'rash
    await message.answer(
        f"👋 Welcome to Marketplace, <b>{first_name}</b>!\n\n"
        f"📱 Please share your phone number to continue.\n\n"
        f"Click the button below to share your contact information.",
        reply_markup=phone_keyboard
    )

    # State'ni o'zgartirish
    await state.set_state(RegistrationStates.waiting_for_phone)


@dp.message(RegistrationStates.waiting_for_phone, F.contact)
async def phone_received_handler(message: Message, state: FSMContext):
    """
    Telefon raqami qabul qilish va autentifikatsiya
    """
    contact = message.contact
    phone_number = contact.phone_number

    # State'dan ma'lumotlarni olish
    user_data = await state.get_data()
    telegram_id = user_data.get('telegram_id')
    first_name = user_data.get('first_name', '')
    last_name = user_data.get('last_name', '')
    username = user_data.get('username', '')

    logger.info(f"Phone number received from user {telegram_id}: {phone_number}")

    # Telegram auth data yaratish
    auth_data = {
        'id': telegram_id,
        'auth_date': int(time.time()),
        'phone_number': phone_number  # Telefon raqamini qo'shish
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
    auth_data['hash'] = auth_hash

    # Mini app URL yaratish
    mini_app_url = "https://marketplacenone.netlify.app"

    # Inline keyboard yaratish - Web App tugmasi
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛒 Open Marketplace",
            web_app=WebAppInfo(url=mini_app_url)
        )]
    ])

    # Django backend ga registration/login so'rovi
    logger.info(f"Sending auth data to Django: {auth_data}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    f"{API_URL}/user/auth/telegram/",
                    json=auth_data,
                    headers={'Content-Type': 'application/json'}
            ) as resp:
                response_text = await resp.text()
                logger.info(f"API Response Status: {resp.status}")
                logger.info(f"API Response Body: {response_text[:500]}")

                if resp.status == 200:
                    try:
                        response_data = await resp.json()

                        success = response_data.get('success')
                        created = response_data.get('created')
                        user_data_response = response_data.get('user', {})
                        tokens = response_data.get('tokens', {})

                        if success:
                            user_name = user_data_response.get('name', first_name)

                            # Keyboard'ni olib tashlash
                            if created:
                                # Yangi user yaratildi
                                logger.info(f"New user created: {telegram_id}")
                                await message.answer(
                                    f"🎉 Welcome to Marketplace, <b>{user_name}</b>!\n\n"
                                    f"✅ Your account has been created successfully.\n"
                                    f"📱 Phone: {phone_number}\n"
                                    f"🔐 You are now logged in.\n\n"
                                    f"Click the button below to open the marketplace! 👇",
                                    reply_markup=ReplyKeyboardRemove()
                                )
                                await message.answer(
                                    "🛒 <b>Open Marketplace</b>",
                                    reply_markup=keyboard
                                )
                            else:
                                # Mavjud user login qildi
                                logger.info(f"Existing user logged in: {telegram_id}")
                                await message.answer(
                                    f"👋 Welcome back, <b>{user_name}</b>!\n\n"
                                    f"✅ You are now logged in.\n"
                                    f"📱 Phone: {phone_number}\n\n"
                                    f"Click the button below to open the marketplace! 👇",
                                    reply_markup=ReplyKeyboardRemove()
                                )
                                await message.answer(
                                    "🛒 <b>Open Marketplace</b>",
                                    reply_markup=keyboard
                                )

                            logger.info(f"Access token received for user {telegram_id}")

                            # State'ni tozalash
                            await state.clear()

                        else:
                            logger.warning(f"Authentication failed for user {telegram_id}")
                            await message.answer(
                                "⚠️ Authentication failed. Please try again with /start",
                                reply_markup=ReplyKeyboardRemove()
                            )
                            await state.clear()

                    except Exception as json_error:
                        logger.error(f"Error parsing JSON response: {json_error}")
                        logger.error(f"Raw response: {response_text}")
                        await message.answer(
                            "⚠️ Server error. Please try again later.",
                            reply_markup=ReplyKeyboardRemove()
                        )
                        await state.clear()

                else:
                    logger.warning(f"Authentication failed with status {resp.status}")
                    logger.warning(f"Response: {response_text[:500]}")
                    await message.answer(
                        "⚠️ Authentication failed. Please try again with /start",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    await state.clear()

        except aiohttp.ClientError as e:
            logger.error(f"Network error during authentication: {e}")
            await message.answer(
                "⚠️ Network error. Please check your connection and try /start again.",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}", exc_info=True)
            await message.answer(
                "⚠️ An unexpected error occurred. Please try /start again.",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()


@dp.message(RegistrationStates.waiting_for_phone)
async def invalid_phone_handler(message: Message):
    """
    Telefon raqami kutilayotganda noto'g'ri xabar kelsa
    """
    await message.answer(
        "⚠️ Please use the button below to share your phone number.\n\n"
        "If you don't see the button, please use /start again."
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

