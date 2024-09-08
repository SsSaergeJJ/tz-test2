import redis.asyncio as aioredis  # Импортируем через redis.asyncio для совместимости с новой версией
from fastapi import FastAPI, HTTPException, status
from datetime import datetime
from typing import List
from models import MessageModel
from db import get_collection  # Импорт функции подключения к коллекции
import logging
import pytz
import json

app = FastAPI()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Устанавливаем часовой пояс
moscow_tz = pytz.timezone('Europe/Moscow')

# Инициализация Redis
redis = None

@app.on_event("startup")
async def startup():
    global redis
    try:
        redis = aioredis.from_url("redis://redis:6379", decode_responses=True)
        pong = await redis.ping()
        if pong:
            logging.info("Подключение к Redis успешно!")
    except Exception as e:
        logging.error(f"Ошибка при подключении к Redis: {str(e)}")

@app.on_event("shutdown")
async def shutdown():
    await redis.close()

# Эндпоинт для получения всех сообщений
@app.get("/api/v1/messages/", response_model=List[MessageModel], status_code=status.HTTP_200_OK)
async def get_messages():
    try:
        # Проверяем кэшированные данные
        cached_messages = await redis.get("messages")
        if cached_messages:
            logging.info("Сообщения получены из кэша Redis")
            return json.loads(cached_messages)

        # Если кэш пуст, загружаем данные из MongoDB
        logging.info("Кэш Redis пуст. Получение сообщений из MongoDB")
        collection = await get_collection()
        messages = await collection.find({}, {'_id': 0}).to_list(length=100)  # Асинхронный запрос

        # Сохраняем данные в кэш Redis
        await redis.set("messages", json.dumps(messages))
        logging.info("Сообщения сохранены в кэш Redis")

        return messages
    except Exception as e:
        logging.error(f"Ошибка при получении сообщений: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении сообщений: {str(e)}")



# Эндпоинт для добавления сообщения
@app.post("/api/v1/message/", status_code=status.HTTP_201_CREATED)
async def create_message(message: MessageModel):
    try:
        collection = await get_collection()

        # Получаем текущее время с учётом часового пояса
        current_time = datetime.now(tz=moscow_tz)
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        message_data = {
            "username": message.username,
            "text": message.text,
            "timestamp": formatted_time
        }

        # Логируем сообщение перед сохранением
        logging.info(f"Сохраняем сообщение: {message_data}")

        # Сохраняем сообщение в базу данных
        await collection.insert_one(message_data)

        # Очищаем кэш после добавления нового сообщения
        await redis.delete("messages")
        logging.info("Кэш Redis сброшен после добавления нового сообщения")

        return {"message": "Message added successfully"}
    except Exception as e:
        logging.error(f"Ошибка при добавлении сообщения: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении сообщения: {str(e)}")


