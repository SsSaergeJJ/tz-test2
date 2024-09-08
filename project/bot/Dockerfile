# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app/bot

# Копируем файл requirements.txt.txt в контейнер
COPY requirements.txt ./

# Устанавливаем зависимости проекта
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в рабочую директорию
COPY . /app

# Команда для запуска бота
CMD ["python", "main.py"]
