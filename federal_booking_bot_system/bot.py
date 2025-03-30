import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

INVITE_CODE = "1924"

# حالة المستخدم
class BookingState(StatesGroup):
    service = State()
    code = State()
    birthdate = State()
    invite = State()

# بدء البوت
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Welcome! Please enter the service type:")
    await BookingState.service.set()

# خدمة
@dp.message_handler(state=BookingState.service)
async def get_service(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await message.answer("Enter request number:")
    await BookingState.code.set()

# رقم الطلب
@dp.message_handler(state=BookingState.code)
async def get_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    await message.answer("Enter your birthdate (dd/mm/yyyy):")
    await BookingState.birthdate.set()

# تاريخ الميلاد
@dp.message_handler(state=BookingState.birthdate)
async def get_birthdate(message: types.Message, state: FSMContext):
    await state.update_data(birthdate=message.text)
    await message.answer("Enter the private invite code:")
    await BookingState.invite.set()

# رمز الدعوة
@dp.message_handler(state=BookingState.invite)
async def get_invite(message: types.Message, state: FSMContext):
    if message.text != INVITE_CODE:
        await message.answer("❌ Invalid code.")
        await state.finish()
        return

    data = await state.get_data()
    chat_id = str(message.chat.id)
    user_data = {
        "chat_id": chat_id,
        "name": message.from_user.first_name,
        "requests": [{
            "codigo": data['code'],
            "birthdate": data['birthdate'],
            "service": data['service'],
            "auto_book": False
        }]
    }

    try:
        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)
    except:
        users = []

    existing = next((u for u in users if u['chat_id'] == chat_id), None)
    if existing:
        existing['requests'].append(user_data['requests'][0])
    else:
        users.append(user_data)

    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

    await message.answer("✅ Your data has been saved! We will notify you when an appointment is available.")
    await state.finish()

# زر تأكيد الحجز
@dp.callback_query_handler(lambda c: c.data in ["confirm_booking", "ignore_booking"])
async def handle_confirmation(call: types.CallbackQuery):
    if call.data == "confirm_booking":
        await call.message.answer("Booking confirmed. We are processing your request...")
        # هنا يمكن ربطه بالحجز الحقيقي
    else:
        await call.message.answer("Booking ignored.")
    await call.answer()

# إرسال إشعار بالحجز عند توفره (تُستخدم من auto_checker)
async def notify_user(chat_id, date_str):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Yes, book it", callback_data="confirm_booking"),
        InlineKeyboardButton("❌ No, skip", callback_data="ignore_booking")
    )
    await bot.send_message(chat_id, f"🗓️ Appointment available on: {date_str}\nDo you want to book it?", reply_markup=markup)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)