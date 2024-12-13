import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from aiogram import html, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.news import fetch_news
from app.services.search import search_links
from app.services.chat import chat_service

router = Router()

# Состояния для FSM
class SearchStates(StatesGroup):
    waiting_for_query = State()

# Состояния для чата
class ChatStates(StatesGroup):
    waiting_for_question = State()

# Клавиатура
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🔍 Поиск'), KeyboardButton(text='📰 Новости')],
    [KeyboardButton(text='💬 Задать вопрос')]
], resize_keyboard=True)

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}!\n"
        "Я бот ЧелГУ. Выберите действие:",
        reply_markup=main
    )

@router.message(F.text == "🔍 Поиск")
async def search_button_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer(
        "Введите поисковый запрос для поиска по сайту ЧелГУ:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='◀️ Назад')]],
            resize_keyboard=True
        )
    )

@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext) -> None:
    if message.text == "◀️ Назад":
        await state.clear()
        await message.answer("Выберите действие:", reply_markup=main)
        return

    await state.clear()
    try:
        processing_msg = await message.answer("🔍 Ищу информацию на сайте ЧелГУ...")
        
        search_results = search_links(message.text)
        
        await processing_msg.delete()
        
        if isinstance(search_results, dict) and "error" in search_results:
            await message.answer(
                f"❌ {search_results['error']}", 
                reply_markup=main
            )
            return
            
        if not search_results:
            await message.answer(
                "🔍 К сожалению, по вашему запросу ничего не найдено.\n"
                "Попробуйте сформулировать запрос иначе или используйте другие ключевые слова.",
                reply_markup=main
            )
            return
            
        response = "🔍 Результаты поиска на сайте ЧелГУ:\n\n"
        for i, item in enumerate(search_results, 1):
            response += f"{i}. {item['title']}\n"
            if item['snippet']:
                response += f"{item['snippet']}\n"
            response += f"{item['link']}\n\n"
        
        await message.answer(response, reply_markup=main)
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при поиске: {str(e)}", 
            reply_markup=main
        )

@router.message(F.text == "📰 Новости")
async def news_button_handler(message: Message) -> None:
    try:
        news = fetch_news()
        if not news:
            await message.answer(
                "❌ Новости не найдены.", 
                reply_markup=main
            )
            return
            
        response = "📰 Последние новости ЧелГУ:\n\n"
        for i, item in enumerate(news, 1):
            response += f"{i}. {item['title']}\n{item['url']}\n\n"
        
        await message.answer(response, reply_markup=main)
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при получении новостей: {str(e)}", 
            reply_markup=main
        )

@router.message(F.text == "💬 Задать вопрос")
async def chat_button_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(ChatStates.waiting_for_question)
    await message.answer(
        "Задайте свой вопрос о ЧелГУ, и я постараюсь на него ответить.\n"
        "Для возврата в главное меню нажмите '◀️ Назад'",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='◀️ Назад')]],
            resize_keyboard=True
        )
    )

@router.message(ChatStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext) -> None:
    if message.text == "◀️ Назад":
        await state.clear()
        await message.answer("Выберите действие:", reply_markup=main)
        return

    try:
        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer("🤔 Обдумываю ответ...")
        
        # Получаем ответ от модели
        response = chat_service.get_response(message.text)
        
        # Удаляем сообщение о обработке
        await processing_msg.delete()
        
        # Отправляем ответ
        await message.answer(response, reply_markup=main)
        await state.clear()
        
    except Exception as e:
        await message.answer(
            "❌ Извините, произошла ошибка при обработке вашего вопроса. "
            "Попробуйте переформулировать или задать другой вопрос.",
            reply_markup=main
        )
        await state.clear()

# Обработчик для неизвестных команд
@router.message()
async def unknown_message(message: Message) -> None:
    await message.answer(
        "Пожалуйста, используйте кнопки меню для навигации.",
        reply_markup=main
    ) 