import os
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# إعداد البوت
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# الحالات لتخزين بيانات المستخدم خطوة بخطوة
class BookingStates(StatesGroup):
    waiting_for_service = State()
    waiting_for_code = State()
    waiting_for_birthdate = State()
    waiting_for_invite = State()

# بدء المحادثة
@dp.message(commands=["start"])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(BookingStates.waiting_for_service)
    await message.answer("Welcome! Please enter the service type (e.g., Segurança Privada):")

# الخطوة 1
@dp.message(BookingStates.waiting_for_service)
async def get_service(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await state.set_state(BookingStates.waiting_for_code)
    await message.answer("Please enter your request code:")

# الخطوة 2
@dp.message(BookingStates.waiting_for_code)
async def get_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    await state.set_state(BookingStates.waiting_for_birthdate)
    await message.answer("Please enter your date of birth (dd/mm/yyyy):")

# الخطوة 3
@dp.message(BookingStates.waiting_for_birthdate)
async def get_birthdate(message: types.Message, state: FSMContext):
    await state.update_data(birthdate=message.text)
    await state.set_state(BookingStates.waiting_for_invite)
    await message.answer("Please enter the private invitation code:")

# الخطوة 4 والأخيرة
@dp.message(BookingStates.waiting_for_invite)
async def get_invite(message: types.Message, state: FSMContext):
    invite_code = message.text
    if invite_code != "1924":
        await message.answer("❌ Invalid invitation code. Access denied.")
        await state.clear()
        return

    data = await state.get_data()
    user_data = {
        "chat_id": message.chat.id,
        "name": message.from_user.full_name,
        "service": data["service"],
        "code": data["code"],
        "birthdate": data["birthdate"],
        "auto_book": True,
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    # حفظ البيانات في users.json
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)
    except:
        users = []

    users.append(user_data)

    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

    await message.answer("✅ Your data has been saved. We will monitor and book automatically if available.")
    await state.clear()

# تشغيل البوت
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)