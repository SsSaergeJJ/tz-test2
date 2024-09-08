from datetime import datetime

from aiogram import types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram import Router
import logging

from state import AddMessageState
from services.api_client import get_messages_from_api, send_message_to_api

router = Router()

PAGE_SIZE = 5  # Количество сообщений на странице


# Приветственное сообщение
@router.message(F.text == "/start")  # Используем фильтр F для команды
async def send_welcome(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Добавить сообщение", callback_data="add_message")
    keyboard.button(text="Прочитать сообщения", callback_data="read_messages")
    keyboard.adjust(2)  # Количество кнопок в одном ряду

    await message.answer(
        "Привет! Что вы хотите сделать?",
        reply_markup=keyboard.as_markup()
    )


# Обработчик нажатия кнопки "Добавить сообщение"
@router.callback_query(F.data == "add_message")
async def process_add_message(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info("Пользователь нажал кнопку 'Добавить сообщение'")
    await callback_query.message.answer("Введите сообщение, которое вы хотите сохранить:")
    await state.set_state(AddMessageState.waiting_for_message)


# Обработчик получения и сохранения сообщения
@router.message(AddMessageState.waiting_for_message)
async def save_message(message: types.Message, state: FSMContext):
    logging.info(f"Сохраняю сообщение от пользователя: {message.text}")

    success = await send_message_to_api(message.from_user.username, message.text)

    if success:
        await message.answer("Ваше сообщение сохранено!")
    else:
        await message.answer("Произошла ошибка при сохранении сообщения.")

    await state.clear()
    logging.info("Состояние очищено после сохранения сообщения")


# Обработчик нажатия кнопки "Прочитать сообщения"
@router.callback_query(F.data == "read_messages")
async def process_read_messages(callback_query: types.CallbackQuery):
    page = 0  # Начинаем с первой страницы
    messages, total = await get_messages_from_api(page)

    if messages is None:
        await callback_query.message.answer("Произошла ошибка при получении сообщений.")
        return

    if not messages:
        await callback_query.message.answer("Сообщений пока нет.")
        return

    # Создаем клавиатуру для пагинации
    keyboard = InlineKeyboardBuilder()
    if total > PAGE_SIZE:
        keyboard.button(text="Следующая страница", callback_data=f"next_page:{page + 1}")

    keyboard.adjust(1)

    # Формируем список сообщений для вывода
    message_text = "\n".join(
        [
            f"{msg['username']} ({format_timestamp(msg['timestamp'])}): {msg['text']}"
            for msg in messages
        ]
    )

    await callback_query.message.answer(
        message_text,
        reply_markup=keyboard.as_markup()
    )

# Вспомогательная функция для форматирования времени
def format_timestamp(timestamp: str) -> str:
    dt = datetime.fromisoformat(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# Обработчик для пагинации (следующая страница)
@router.callback_query(F.data.startswith("next_page"))
async def process_next_page(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split(":")[1])
    logging.info(f"Загружаю следующую страницу: {page}")
    messages, total = await get_messages_from_api(page)

    if messages is None:
        await callback_query.message.answer("Произошла ошибка при получении сообщений.")
        return

    if not messages:
        await callback_query.message.answer("Сообщений больше нет.")
        return

    # Логируем текущие сообщения
    logging.info(f"Полученные сообщения: {messages}")

    # Создаем клавиатуру для пагинации
    keyboard = InlineKeyboardBuilder()
    if page > 0:
        keyboard.button(text="Предыдущая страница", callback_data=f"prev_page:{page - 1}")
    if total > (page + 1) * PAGE_SIZE:
        keyboard.button(text="Следующая страница", callback_data=f"next_page:{page + 1}")

    keyboard.adjust(1)

    # Формируем текст с датой для каждой страницы
    message_text = "\n".join(
        [
            f"{msg['username']} ({format_timestamp(msg['timestamp'])}): {msg['text']}"
            for msg in messages
        ]
    )

    await callback_query.message.edit_text(
        message_text,
        reply_markup=keyboard.as_markup()
    )

# Обработчик для пагинации (предыдущая страница)
@router.callback_query(F.data.startswith("prev_page"))
async def process_prev_page(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split(":")[1])
    messages, total = await get_messages_from_api(page)

    if messages is None:
        await callback_query.message.answer("Произошла ошибка при получении сообщений.")
        return

    # Создаем клавиатуру для пагинации
    keyboard = InlineKeyboardBuilder()
    if page > 0:
        keyboard.button(text="Предыдущая страница", callback_data=f"prev_page:{page - 1}")

    if total > (page + 1) * PAGE_SIZE:
        keyboard.button(text="Следующая страница", callback_data=f"next_page:{page + 1}")

    keyboard.adjust(1)

    # Формируем текст с датой для каждой страницы
    message_text = "\n".join(
        [
            f"{msg['username']} ({format_timestamp(msg['timestamp'])}): {msg['text']}"
            for msg in messages
        ]
    )

    await callback_query.message.edit_text(
        message_text,
        reply_markup=keyboard.as_markup()
    )