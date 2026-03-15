import asyncio
import os
import requests
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

async def ask_yandex_gpt(user_message):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    prompt = f"""
You are a caring assistant for healthy lifestyle and mental health.
Answer briefly (2-3 sentences), warmly and to the point.
If asked about food — suggest a simple recipe.
If someone shares their mood — support them and give simple advice.

User message: {user_message}
"""
    
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "200"
        },
        "messages": [
            {
                "role": "system",
                "text": prompt
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            answer = result['result']['alternatives'][0]['message']['text']
            return answer
        else:
            return f"Sorry, connection error. Code: {response.status_code}"
    except Exception as e:
        return f"Sorry, something went wrong. Error: {str(e)}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🌿 Привет! Я твой помощник по здоровью.\n\n"
        "Можешь спросить меня:\n"
        "• что приготовить на ужин\n"
        "• как поднять настроение\n"
        "• дать зарядку\n"
        "• или просто поделится мыслями\n\n"
        "Чем помочь сегодня?"
    )

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(message.chat.id, action="typing")
    response = await ask_yandex_gpt(message.text)
    await message.answer(response)

async def main():
    print("✅ Bot is running and ready to work!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
