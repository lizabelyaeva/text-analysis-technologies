# bot.py
"""
Основной файл Telegram-бота "КиноПоиск"
Реализует обработчики команд и логику работы
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

# Импорт модулей проекта
from config import (
    BOT_TOKEN, KINOPOISK_API_KEY, WELCOME_MESSAGE, HELP_MESSAGE,
    MIN_RATING, MAX_RESULTS, MIN_VOTES, AVAILABLE_GENRES
)
from api_client import KinopoiskAPIClient
from filters import MovieDataProcessor
from user_storage import UserStorage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация компонентов
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
api_client = KinopoiskAPIClient(KINOPOISK_API_KEY)
processor = MovieDataProcessor()
user_storage = UserStorage()


def get_main_keyboard():
    """Главная клавиатура с основными командами"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔍 Найти фильм"),
                KeyboardButton(text="🎭 По жанру")
            ],
            [
                KeyboardButton(text="🏆 Топ фильмов"),
                KeyboardButton(text="🔥 Популярные")
            ],
            [
                KeyboardButton(text="🎲 Случайный фильм"),
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return keyboard


def get_genres_keyboard():
    """Клавиатура с жанрами"""
    buttons = []
    row = []
    for i, genre in enumerate(AVAILABLE_GENRES, 1):
        row.append(InlineKeyboardButton(text=genre.capitalize(), callback_data=f"genre_{genre}"))
        if i % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard



@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    user_storage.get_user_data(user_id)
    user_storage.update_last_activity(user_id)
    
    logger.info(f"Пользователь {username} (ID: {user_id}) запустил бота")
    
    await message.answer(
        f"Привет, {username}!\n\n{WELCOME_MESSAGE}",
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    user_id = message.from_user.id
    user_storage.update_last_activity(user_id)
    
    await message.answer(HELP_MESSAGE, parse_mode=ParseMode.HTML)


@dp.message(Command("movie"))
async def cmd_movie(message: Message):
    """Обработчик команды /movie <название>"""
    user_id = message.from_user.id
    user_storage.update_last_activity(user_id)
    
    command_parts = message.text.split(maxsplit=1)
    
    if len(command_parts) < 2:
        await message.answer(
            "❌ Пожалуйста, укажите название фильма.\n"
            "Пример: /movie Inception",
            parse_mode=ParseMode.HTML
        )
        return
    
    movie_name = command_parts[1].strip()
    status_msg = await message.answer(f"🔍 Ищу фильм '{movie_name}'...")
    
    try:
        movies = api_client.search_movie_by_name(movie_name, limit=3)
        
        if not movies:
            await status_msg.edit_text(
                f"❌ Фильм '{movie_name}' не найден.\n"
                "Попробуйте изменить запрос."
            )
            return
        
        filtered_movies = processor.filter_by_rating(
            movies, min_rating=MIN_RATING - 1, min_votes=MIN_VOTES
        )
        
        if not filtered_movies:
            filtered_movies = movies[:3]
        
        user_storage.add_to_search_history(user_id, movie_name, "movie")
        
        await status_msg.delete()
        
        for movie in filtered_movies[:3]:
            movie_info, poster_url = processor.format_movie_info(movie)
            
            if poster_url:
                try:
                    await message.answer_photo(
                        photo=poster_url,
                        caption=movie_info,
                        parse_mode=ParseMode.HTML
                    )
                except:
                    await message.answer(movie_info, parse_mode=ParseMode.HTML)
            else:
                await message.answer(movie_info, parse_mode=ParseMode.HTML)
            
            await asyncio.sleep(0.5)
    
    except Exception as e:
        logger.error(f"Ошибка при поиске фильма: {e}")
        await status_msg.edit_text(
            "❌ Произошла ошибка при поиске. Попробуйте позже."
        )


@dp.message(Command("genre"))
async def cmd_genre(message: Message):
    """Обработчик команды /genre <жанр>"""
    user_id = message.from_user.id
    user_storage.update_last_activity(user_id)
    
    command_parts = message.text.split(maxsplit=1)
    
    if len(command_parts) < 2:
        await message.answer(
            "🎭 Выберите жанр:",
            reply_markup=get_genres_keyboard()
        )
        return
    
    genre = command_parts[1].strip().lower()
    await process_genre_request(message, genre)


@dp.callback_query(F.data.startswith("genre_"))
async def callback_genre(callback: types.CallbackQuery):
    """Обработчик нажатий на кнопки жанров"""
    genre = callback.data.replace("genre_", "")
    await callback.answer()
    await process_genre_request(callback.message, genre)


async def process_genre_request(message: Message, genre: str):
    """Обработка запроса фильмов по жанру"""
    user_id = message.from_user.id if message.from_user else 0
    
    status_msg = await message.answer(f"🎭 Подбираю фильмы жанра '{genre}'...")
    
    try:
        movies = api_client.get_movies_by_genre(
            genre, limit=MAX_RESULTS, min_rating=MIN_RATING
        )
        
        if not movies:
            await status_msg.edit_text(
                f"❌ Фильмы жанра '{genre}' не найдены.\n"
                "Проверьте правильность написания жанра."
            )
            return
        
        sorted_movies = processor.sort_by_weighted_rating(movies)
        unique_movies = processor.deduplicate_movies(sorted_movies)
        
        user_storage.add_favorite_genre(user_id, genre)
        user_storage.add_to_search_history(user_id, genre, "genre")
        
        # Формируем ОДНО сообщение со списком
        movies_list = processor.format_movies_list(
            unique_movies[:5], 
            f"Топ-5 фильмов жанра '{genre}'"
        )
        
        await status_msg.delete()
        await message.answer(movies_list, parse_mode=ParseMode.HTML)
    
    except Exception as e:
        logger.error(f"Ошибка при поиске по жанру: {e}")
        await status_msg.edit_text(
            "❌ Произошла ошибка при поиске. Попробуйте позже."
        )


@dp.message(Command("top"))
async def cmd_top(message: Message):
    """Обработчик команды /top - Топ-10 лучших фильмов С ОПИСАНИЯМИ"""
    user_id = message.from_user.id
    user_storage.update_last_activity(user_id)
    
    status_msg = await message.answer("🏆 Формирую топ лучших фильмов...")
    
    try:
        movies = api_client.get_top_movies(limit=10, min_rating=8.0)
        
        if not movies:
            await status_msg.edit_text(
                "❌ Не удалось получить топ фильмов. Попробуйте позже."
            )
            return
        
        sorted_movies = processor.sort_by_weighted_rating(movies)
        user_storage.add_to_search_history(user_id, "top", "top")
        
        await status_msg.delete()
        
        # Заголовок
        await message.answer(
            "🏆 <b>Топ-10 лучших фильмов по рейтингу</b>\n",
            parse_mode=ParseMode.HTML
        )
        
        # Выводим каждый фильм с полным описанием
        for i, movie in enumerate(sorted_movies[:10], 1):
            movie_info, poster_url = processor.format_movie_info(movie, include_poster=False)
            
            await message.answer(
                f"<b>#{i}</b>\n{movie_info}",
                parse_mode=ParseMode.HTML
            )
            
            # Небольшая задержка между сообщениями
            if i < 10:
                await asyncio.sleep(0.3)
    
    except Exception as e:
        logger.error(f"Ошибка при получении топа: {e}")
        await status_msg.edit_text(
            "❌ Произошла ошибка при получении топа. Попробуйте позже."
        )


@dp.message(Command("popular"))
async def cmd_popular(message: Message):
    """Обработчик команды /popular - Топ-10 популярных фильмов"""
    user_id = message.from_user.id
    user_storage.update_last_activity(user_id)
    
    status_msg = await message.answer("🔥 Получаю популярные фильмы...")
    
    try:
        movies = api_client.get_popular_movies(limit=10)
        
        if not movies:
            await status_msg.edit_text(
                "❌ Не удалось получить популярные фильмы. Попробуйте позже."
            )
            return
        
        user_storage.add_to_search_history(user_id, "popular", "popular")
        
        # Форматируем список популярных фильмов
        popular_list = processor.format_popular_list(movies[:10])
        
        await status_msg.delete()
        await message.answer(popular_list, parse_mode=ParseMode.HTML)
    
    except Exception as e:
        logger.error(f"Ошибка при получении популярных: {e}")
        await status_msg.edit_text(
            "❌ Произошла ошибка. Попробуйте позже."
        )


@dp.message(Command("random"))
async def cmd_random(message: Message):
    """Обработчик команды /random - Случайный фильм"""
    user_id = message.from_user.id
    user_storage.update_last_activity(user_id)
    
    status_msg = await message.answer("🎲 Выбираю случайный фильм...")
    
    try:
        movie = api_client.get_random_movie(min_rating=MIN_RATING)
        
        if not movie:
            await status_msg.edit_text(
                "❌ Не удалось получить рекомендацию. Попробуйте еще раз."
            )
            return
        
        user_storage.add_to_search_history(user_id, "random", "random")
        
        movie_info, poster_url = processor.format_movie_info(movie)
        
        await status_msg.delete()
        
        if poster_url:
            try:
                await message.answer_photo(
                    photo=poster_url,
                    caption=f"🎲 <b>Случайная рекомендация:</b>\n\n{movie_info}",
                    parse_mode=ParseMode.HTML
                )
            except:
                await message.answer(
                    f"🎲 <b>Случайная рекомендация:</b>\n\n{movie_info}",
                    parse_mode=ParseMode.HTML
                )
        else:
            await message.answer(
                f"🎲 <b>Случайная рекомендация:</b>\n\n{movie_info}",
                parse_mode=ParseMode.HTML
            )
    
    except Exception as e:
        logger.error(f"Ошибка при получении случайного фильма: {e}")
        await status_msg.edit_text(
            "❌ Произошла ошибка. Попробуйте еще раз."
        )


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    """Обработчик команды /stats"""
    user_id = message.from_user.id
    user_storage.update_last_activity(user_id)
    
    stats = user_storage.get_user_statistics(user_id)
    await message.answer(stats, parse_mode=ParseMode.HTML)



@dp.message(F.text == "🔍 Найти фильм")
async def button_search(message: Message):
    """Кнопка поиска фильма"""
    await message.answer(
        "🔍 Введите название фильма в формате:\n"
        "<code>/movie Название фильма</code>\n\n"
        "Например: <code>/movie Inception</code>",
        parse_mode=ParseMode.HTML
    )


@dp.message(F.text == "🎭 По жанру")
async def button_genre(message: Message):
    """Кнопка выбора жанра"""
    await message.answer(
        "🎭 Выберите жанр:",
        reply_markup=get_genres_keyboard()
    )


@dp.message(F.text == "🏆 Топ фильмов")
async def button_top(message: Message):
    """Кнопка топ фильмов"""
    await cmd_top(message)


@dp.message(F.text == "🔥 Популярные")
async def button_popular(message: Message):
    """Кнопка популярных фильмов"""
    await cmd_popular(message)


@dp.message(F.text == "🎲 Случайный фильм")
async def button_random(message: Message):
    """Кнопка случайного фильма"""
    await cmd_random(message)


@dp.message(F.text == "❓ Помощь")
async def button_help(message: Message):
    """Кнопка помощи"""
    await cmd_help(message)


@dp.message()
async def handle_unknown(message: Message):
    """Обработчик неизвестных команд"""
    await message.answer(
        "❌ Неизвестная команда.\n\n"
        "Используйте кнопки меню или /help для просмотра команд.",
        parse_mode=ParseMode.HTML
    )



async def main():
    """Главная функция запуска бота"""
    logger.info("Запуск бота...")
    
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error("Ошибка: не указан BOT_TOKEN в config.py")
        return
    
    if KINOPOISK_API_KEY == "YOUR_KINOPOISK_API_KEY_HERE":
        logger.error("Ошибка: не указан KINOPOISK_API_KEY в config.py")
        return
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        
        logger.info("Бот успешно запущен!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())