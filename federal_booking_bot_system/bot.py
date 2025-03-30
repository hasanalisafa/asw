import os
import json
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get bot token from environment variable
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Temp storage for user steps
user_states = {}

# Handle /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_states[message.chat.id] = {'step': 1}
    await message.answer("Welcome! Please enter the service type (e.g., Segurança Privada):")

# Handle each step
@dp.message_handler(lambda message: True)
async def collect_data(message: types.Message):
    user_id = message.chat.id
    state = user_states.get(user_id, {})

    if not state:
        await message.answer("Please type /start to begin.")
        return

    step = state.get('step', 1)

    if step == 1:
        state['service'] = message.text
        state['step'] = 2
        await message.answer("Please enter your request number:")
    elif step == 2:
        state['code'] = message.text
        state['step'] = 3
        await message.answer("Please enter your date of birth (dd/mm/yyyy):")
    elif step == 3:
        state['birthdate'] = message.text
        state['step'] = 4
        await message.answer("Please enter the private invitation code:")
    elif step == 4:
        if message.text != "1924":
            await message.answer("❌ Invalid invite code.")
            user_states.pop(user_id, None)
            return
        # Save data
        user_data = {
            "chat_id": user_id,
            "name": message.from_user.full_name,
            "service": state['service'],
            "code": state['code'],
            "birthdate": state['birthdate'],
            "auto_book": True,
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        try:
            with open("users.json", "r", encoding="utf-8") as f:
                users = json.load(f)
        except:
            users = []

        users.append(user_data)
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

        await message.answer("✅ Your data has been saved successfully. We will notify you when a slot is found.")
        user_states.pop(user_id, None)

# Run bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)