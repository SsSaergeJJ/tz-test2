import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from fastapi import HTTPException

# Загружаем переменные окружения из файла .env
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

if not MONGO_URL or not MONGO_DB_NAME:
    raise HTTPException(status_code=500, detail="Проблема с переменными окружения для MongoDB")

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]

async def get_collection():
    try:
        return db['messages']
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при подключении к коллекции MongoDB")
