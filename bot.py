import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from prometheus_client import start_http_server, Counter

BOT_TOKEN = "7150704262:AAGU1B-5evIIilBPc9CHb8Iq6XXjbhHQlEY"

# Метрики Prometheus
start_counter = Counter("telegram_start_commands", "Count of /start commands")
ping_counter = Counter("telegram_ping_commands", "Count of /ping commands")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def log_to_fluentd(tag, message):
    url = "http://localhost:8080"
    headers = {"Content-Type": "application/json"}
    data = {
        "@log_name": tag,
        "message": message
    }
    try:
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Error sending log to Fluentd: {e}")

@dp.message(Command("start"))
async def start(event: types.Message):
    user = event.from_user
    msg = f"User {user.id} ({user.username}) started the bot"
    log_to_fluentd("telegram_bot", msg)
    start_counter.inc()  # інкремент метрики
    await event.answer("Привіт! Я бот з логуванням та метриками.")

@dp.message(Command("ping"))
async def ping(event: types.Message):
    msg = f"Ping from user {event.from_user.id}"
    log_to_fluentd("telegram_bot", msg)
    ping_counter.inc()  # інкремент метрики
    await event.answer("pong!")

async def main():
    logging.basicConfig(level=logging.INFO)
    # Запуск HTTP-серверу для метрик на порту 9091
    start_http_server(9091)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
