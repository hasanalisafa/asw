import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Temporary in-memory user state
user_steps = {}

# Logging
logging.basicConfig(level=logging.INFO)

# Start command
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.chat.id
    user_steps[chat_id] = {'step': 1}
    await message.answer("Welcome! Please enter the service type (e.g., Segurança Privada):")

# Handle step-by-step input
@dp.message_handler()
async def handle_steps(message: types.Message):
    chat_id = message.chat.id
    text = message.text
    step_data = user_steps.get(chat_id)

    if not step_data:
        await message.answer("Please type /start to begin.")
        return

    step = step_data.get("step", 1)

    if step == 1:
        step_data["service"] = text
        step_data["step"] = 2
        await message.answer("Please enter your request number:")
    elif step == 2:
        step_data["code"] = text
        step_data["step"] = 3
        await message.answer("Please enter your date of birth (dd/mm/yyyy):")
    elif step == 3:
        step_data["birthdate"] = text
        step_data["step"] = 4
        await message.answer("Please enter the private invitation code:")
    elif step == 4:
        if text.strip() != "1924":
            await message.answer("❌ Invalid invite code.")
            user_steps.pop(chat_id, None)
            return

        # Save user data
        user_data = {
            "chat_id": chat_id,
            "name": message.from_user.full_name,
            "service": step_data["service"],
            "code": step_data["code"],
            "birthdate": step_data["birthdate"],
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

        await message.answer("✅ Your data has been saved. We will notify you when an appointment is available.")
        user_steps.pop(chat_id, None)

# Run the bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)