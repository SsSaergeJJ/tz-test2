# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app/api

# Копируем файл requirements.txt в контейнер
COPY requirements.txt ./

# Устанавливаем зависимости проекта
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в рабочую директорию /app/api
COPY . .

# Команда для запуска FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
