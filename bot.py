import asyncio
import logging
import os
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Теперь без int(), если ID не число, это не вызовет ошибку

# Настройки бота
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Список РЕГУЛЯРНЫХ ШАБЛОНОВ «плохих слов»
BAD_PATTERNS = [
    r"\w*хуй",
    r"\w*хуё",
    r"\w*хуе",
    r"\w*охуе",
    r"\w*пидр",
    r"\w*шлюх",
    r"\w*еба",
    r"\w*ебу",
]

@dp.message(Command("start"))
async def start_command(message: Message):
    """Обработчик команды /start"""
    text = r"""
👋 *Добро пожаловать в официальную приёмную Леонида Пивотского\!*  

📌 *Ваши идеи важны для нас\!*  
\(но не факт, что они кому\-то нужны\)  

🗂 *Как работает эта махина бюрократии\?*  
1\. Вы присылаете свою гениальную \(или не очень\) идею\.  
2\. Мы с важным лицом записываем её в цифровой архив\.  
3\. Дальше идея отправляется в загадочное место под названием _"куда надо"_\.  
4\. Вы получаете вежливое _"Спасибо, информация принята\!"_ и ощущение выполненного долга\.  
    """
    await message.answer(text, parse_mode="MarkdownV2")

@dp.message()
async def handle_message(message: Message):
    """Обработчик входящих сообщений"""
    text = message.text.lower()

    # Проверяем наличие "плохих слов" по нашим регулярным шаблонам
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in BAD_PATTERNS):
        await message.answer("Пожалуйста без мата и оскорблений, давайте по существу.")
        return

    # Благодарим пользователя
    await message.answer("Спасибо, информация принята")

    # Пересылаем сообщение в группу и отлавливаем ошибки
    try:
        sent_message = await bot.send_message(
            CHAT_ID,
            f"💡 Новая идея от @{message.from_user.username}:\n\n{message.text}"
        )
        logging.info(f"Сообщение успешно отправлено в группу! ID: {sent_message.message_id}")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения в группу: {e}")

async def main():
    """Функция запуска бота"""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())