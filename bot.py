import asyncio
import logging
import os
import re
import threading
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Проверяем, является ли CHAT_ID числом (если да, приводим к int)
if CHAT_ID and CHAT_ID.lstrip("-").isdigit():
    CHAT_ID = int(CHAT_ID)

# Настройки логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
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

    # Проверяем наличие "плохих слов" по регулярным шаблонам
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in BAD_PATTERNS):
        await message.answer("Пожалуйста без мата и оскорблений, давайте по существу.")
        return

    # Благодарим пользователя
    await message.answer("Спасибо, информация принята")

    # Пересылаем сообщение в группу
    if CHAT_ID:
        try:
            sent_message = await bot.send_message(
                CHAT_ID,
                f"💡 Новая идея от @{message.from_user.username}:\n\n{message.text}"
            )
            logging.info(f"Сообщение успешно отправлено в группу! ID: {sent_message.message_id}")
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения в группу: {e}")

async def keep_alive():
    """Функция отправки пинга Telegram API раз в 5 минут, чтобы Render не отключал процесс"""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.telegram.org") as resp:
                    logging.info(f"Пинг Telegram API: {resp.status}")
        except Exception as e:
            logging.warning(f"Ошибка пинга: {e}")
        await asyncio.sleep(300)  # Пауза 5 минут

async def run_bot():
    """Функция запуска бота"""
    asyncio.create_task(keep_alive())  # Запуск функции keep_alive() в фоне
    await dp.start_polling(bot)

# Фиктивный HTTP-сервер для Render
class StubServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running.")

def run_http_server():
    """Запускаем HTTP-сервер на порту 10000, чтобы Render не отключал процесс"""
    server = HTTPServer(("0.0.0.0", 10000), StubServer)
    server.serve_forever()

if __name__ == "__main__":
    # Запускаем HTTP-сервер в отдельном потоке
    threading.Thread(target=run_http_server, daemon=True).start()

    # Запускаем бота
    asyncio.run(run_bot())