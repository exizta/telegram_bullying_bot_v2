import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from keep_alive import keep_alive

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [int(x) for x in os.getenv("ADMINS", "").split(",") if x.strip().isdigit()]

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Главное меню
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💬 Мне нужно выговориться")],
        [KeyboardButton(text="📖 Я хочу получить совет, что делать")],
        [KeyboardButton(text="🆘 Мне нужна срочная помощь")],
        [KeyboardButton(text="ℹ️ Я хочу узнать больше о буллинге")]
    ],
    resize_keyboard=True
)

# Состояние пользователя: ждем текст после кнопки
user_waiting_for_text = {}

# Стартовое сообщение
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "С чего начнем? Выбери, о чем хочешь поговорить:",
        reply_markup=main_kb
    )

# Обработка кнопок
@dp.message(F.text.in_(["💬 Мне нужно выговориться",
                        "📖 Я хочу получить совет, что делать",
                        "🆘 Мне нужна срочная помощь",
                        "ℹ️ Я хочу узнать больше о буллинге"]))
async def handle_button(message: Message):
    user_waiting_for_text[message.from_user.id] = message.text
    await message.answer("Расскажи подробнее:")

# Обработка текста от пользователя
@dp.message()
async def handle_text(message: Message):
    user_id = message.from_user.id
    if user_id in user_waiting_for_text:
        category = user_waiting_for_text.pop(user_id)
        for admin_id in ADMINS:
            try:
                await bot.send_message(
                    admin_id,
                    f"📨 Новое сообщение по теме '{category}':\n\n{message.text}"
                )
            except Exception as e:
                print(f"Не удалось отправить админу {admin_id}: {e}")
        await message.answer("✅ Спасибо! Твое сообщение отправлено анонимно.")
    else:
        await message.answer("Пожалуйста, сначала выбери тему в меню.")

# Запуск бота
if __name__ == "__main__":
    keep_alive()
    asyncio.run(dp.start_polling(bot))
