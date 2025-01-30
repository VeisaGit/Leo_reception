import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# Важно: сюда подставьте свой реальный токен
# Например, можно использовать os.getenv("BOT_TOKEN"),
# если хотите хранить токен в переменной окружения
BOT_TOKEN = "7929776211:AAFIdfvcXkfNrRbJyFPHNTOJ10w4Ri-ChT8"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def print_chat_id(message: types.Message):
    # Печатаем chat_id в консоль
    print("Chat ID:", message.chat.id)
    # Также отправим ответ обратно, чтобы вы видели в чате
    await message.answer(f"Your chat ID is {message.chat.id}")

async def main():
    """Запускаем бота в режиме long polling"""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())