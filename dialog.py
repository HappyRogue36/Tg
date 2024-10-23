from pyrogram import Client
import yaml


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


# Основной клиент для работы с Телеграм
app = Client("my_account", api_id=api_id, api_hash=api_hash, phone_number=phone_number)


async def main():
    print("Получаем чаты...")
    # Получаем все диалоги (чаты)
    async for dialog in app.get_dialogs():
        chat = dialog.chat
        chat_id = chat.id
        chat_name = chat.first_name or chat.title or "Без названия"
        print(f"ID: {chat_id}, Название: {chat_name}")


# Запускаем приложение
with app:
    app.run(main())
