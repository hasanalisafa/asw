import json
import os
import random
import time
import asyncio
from bot import notify_user  # استدعاء الدالة من البوت
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))

async def check_for_appointments():
    while True:
        try:
            with open("users.json", "r", encoding="utf-8") as f:
                users = json.load(f)
        except:
            users = []

        for user in users:
            chat_id = user['chat_id']
            for request in user['requests']:
                # وهمي: إذا تم العثور على موعد، أرسل إشعار
                # في النسخة الفعلية نستخدم Selenium هنا للتحقق من توفر المواعيد
                date_found = "Friday 05/04 at 10:30"
                await notify_user(chat_id, date_found)

        # انتظر 4 دقائق ±30 ثانية عشوائية
        delay = random.randint(230, 270)
        await asyncio.sleep(delay)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_for_appointments())