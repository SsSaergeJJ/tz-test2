import aiohttp
import logging
import os

FASTAPI_URL = os.getenv('FASTAPI_URL')

# Функция для отправки данных в FastAPI (POST /api/v1/message/)
async def send_message_to_api(username, text):
    async with aiohttp.ClientSession() as session:
        payload = {"username": username, "text": text}
        try:
            async with session.post(f"{FASTAPI_URL}/api/v1/message/", json=payload) as response:
                if response.status not in {200, 201}:
                    logging.error(f"Ошибка при отправке данных в FastAPI: {response.status}")
                    return False
                else:
                    logging.info("Сообщение успешно отправлено в FastAPI")
                    return True
        except aiohttp.ClientConnectorError:
            logging.error("Не удалось подключиться к FastAPI.")
            return False

# Функция для получения сообщений из FastAPI (GET /api/v1/messages/)
async def get_messages_from_api(page: int):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{FASTAPI_URL}/api/v1/messages/") as response:
                if response.status != 200:
                    logging.error(f"Ошибка при получении данных от FastAPI: {response.status}")
                    return None, 0

                # Получаем список сообщений
                messages = await response.json()
                logging.info(f"Сообщения от FastAPI: {messages}")

                # Пагинация
                PAGE_SIZE = 5
                start = page * PAGE_SIZE
                end = start + PAGE_SIZE

                return messages[start:end], len(messages)

        except aiohttp.ClientConnectorError as e:
            logging.error(f"Не удалось подключиться к FastAPI. Ошибка: {str(e)}")
            return None, 0
