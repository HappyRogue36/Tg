import asyncio
import yaml
import time
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode


# Загрузка конфигурации из файла
def load_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


config = load_config('config.yaml')

api_id = config['api_id']
api_hash = config['api_hash']
phone_number = config['phone_number']
bot_token = config['bot_token']
alert_channel = config['alert_channel']
scan_interval = config['scan_interval']
chat_ids = config['chat_ids']
keywords = config['keywords']

bot = Bot(token=config['bot_token'])

dp = Dispatcher()

# Основной клиент для работы с Телеграм
app = Client("my_account", api_id=api_id, api_hash=api_hash, phone_number=phone_number)


# Функция для проверки наличия ключевых слов в сообщении с использованием схожести
def check_keywords(message_text):
    for keyword in keywords:
        if fuzz.partial_ratio(keyword.lower(), message_text.lower()) >= 75:
            return True
    return False


# Функция для обработки сообщений из чатов
async def process_chat_messages(start_time: datetime):
    for chat_id in chat_ids:
        try:
            # Асинхронно перебираем сообщения из истории чата
            async for message in app.get_chat_history(chat_id):
                # Проверяем, является ли это текстовым сообщением
                if isinstance(message, Message) and message.text:
                    # Фильтрация по времени отправки
                    if message.date >= start_time:
                        # Если сообщение подходит, выводим его текст
                        print(message.text)
                        # Можно также добавить проверку ключевых слов и отправку алерта
                        if check_keywords(message.text):
                            await send_alert(message)
        except FloodWait as e:
            print(f"Flood wait for {e.x} seconds")
            await asyncio.sleep(e.x)
        except Exception as e:
            print(e)


# Функция для отправки алерта через бота
async def send_alert(message):
    if message.from_user:
        user = message.from_user.username
    else:
        user = "Не удалось определить отправителя"
    alert_text = (
        f"📢 <b>Сообщение найдено</b>\n"
        f"🗣 <b>Отправитель:</b> {user}\n"
        f"💬 <b>Текст:</b> {message.text}\n"
        f"⏰ <b>Время:</b> {message.date.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await bot.send_message(alert_channel, alert_text, parse_mode=ParseMode.HTML)


# Функция для планирования задачи
async def job():
    print("Сканируем чаты...")
    await process_chat_messages(datetime.now() - timedelta(minutes=scan_interval))


async def main() -> None:
    async with app:
        while True:
            try:
                await job()
            except Exception as e:
                print(e)
                pass
            time.sleep(scan_interval * 60)


# Основной цикл
if __name__ == "__main__":
    asyncio.run(main())
