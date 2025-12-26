# filters.py
"""
Нетривиальные алгоритмы обработки и фильтрации данных о фильмах
"""

from typing import List, Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


class MovieDataProcessor:
    """Класс для обработки и анализа данных о фильмах"""
    
    @staticmethod
    def filter_by_rating(movies: List[Dict], min_rating: float, 
                        min_votes: int = 1000) -> List[Dict]:
        """
        Фильтрация фильмов по рейтингу и количеству оценок
        
        Нетривиальный алгоритм: учитывает не только рейтинг,
        но и количество голосов для надежности
        
        Args:
            movies: Список фильмов
            min_rating: Минимальный рейтинг
            min_votes: Минимальное количество голосов
            
        Returns:
            Отфильтрованный список фильмов
        """
        filtered = []
        
        for movie in movies:
            rating = movie.get("rating", {}).get("kp", 0)
            votes = movie.get("votes", {}).get("kp", 0)
            
            # Проверка рейтинга и количества голосов
            if rating >= min_rating and votes >= min_votes:
                filtered.append(movie)
        
        return filtered
    
    @staticmethod
    def sort_by_weighted_rating(movies: List[Dict]) -> List[Dict]:
        """
        Сортировка по взвешенному рейтингу
        
        Нетривиальный алгоритм: использует формулу IMDB для расчета
        взвешенного рейтинга с учетом количества голосов
        
        Formula: WR = (v/(v+m)) * R + (m/(v+m)) * C
        где:
        - WR = взвешенный рейтинг
        - v = количество голосов за фильм
        - m = минимум голосов для попадания в топ (например, 25000)
        - R = средний рейтинг фильма
        - C = средний рейтинг по всем фильмам (например, 7.0)
        
        Args:
            movies: Список фильмов
            
        Returns:
            Отсортированный список
        """
        MIN_VOTES_THRESHOLD = 25000
        MEAN_RATING = 7.0
        
        for movie in movies:
            rating = movie.get("rating", {}).get("kp", 0)
            votes = movie.get("votes", {}).get("kp", 0)
            
            # Расчет взвешенного рейтинга
            if votes > 0:
                weighted = (votes / (votes + MIN_VOTES_THRESHOLD)) * rating + \
                          (MIN_VOTES_THRESHOLD / (votes + MIN_VOTES_THRESHOLD)) * MEAN_RATING
                movie["weighted_rating"] = round(weighted, 2)
            else:
                movie["weighted_rating"] = 0
        
        # Сортировка по взвешенному рейтингу
        return sorted(movies, key=lambda x: x.get("weighted_rating", 0), reverse=True)
    
    @staticmethod
    def analyze_movie_data(movie: Dict) -> Dict[str, any]:
        """
        Анализ данных о фильме
        
        Нетривиальный алгоритм: извлекает и обрабатывает различные
        метрики фильма для создания аналитики
        
        Args:
            movie: Данные о фильме
            
        Returns:
            Словарь с аналитическими данными
        """
        rating = movie.get("rating", {}).get("kp", 0)
        votes = movie.get("votes", {}).get("kp", 0)
        year = movie.get("year", 0)
        
        # Определение популярности
        if votes > 500000:
            popularity = "Очень популярный"
        elif votes > 100000:
            popularity = "Популярный"
        elif votes > 10000:
            popularity = "Известный"
        else:
            popularity = "Малоизвестный"
        
        # Определение качества по рейтингу
        if rating >= 8.5:
            quality = "Шедевр"
        elif rating >= 8.0:
            quality = "Отличный"
        elif rating >= 7.5:
            quality = "Хороший"
        elif rating >= 7.0:
            quality = "Неплохой"
        else:
            quality = "Средний"
        
        # Определение эпохи
        current_year = 2025
        if year >= current_year - 3:
            era = "Новинка"
        elif year >= current_year - 10:
            era = "Современный"
        elif year >= 2000:
            era = "2000-х"
        elif year >= 1990:
            era = "90-х"
        else:
            era = "Классика"
        
        return {
            "popularity": popularity,
            "quality": quality,
            "era": era,
            "votes_formatted": f"{votes:,}".replace(",", " ")
        }
    
    @staticmethod
    def clean_html(text: str) -> str:
        """
        Очищает текст от HTML-тегов, которые Telegram не поддерживает.
        Оставляет только <b>, <i>, <u>, <s>, <code>, <pre>, <a>
        """
        if not text:
            return ""
        # Удаляем все теги, кроме разрешенных
        return re.sub(r'</?(?!b|i|u|s|code|pre|a)[^>]*>', '', text)

    @staticmethod
    def format_movie_info(movie: Dict, include_poster: bool = True) -> tuple:
        """
        Форматирование информации о фильме для вывода в Telegram
        Безопасно для parse_mode=HTML
        
        Args:
            movie: Данные о фильме
            include_poster: Включать ли URL постера
            
        Returns:
            Кортеж (текст сообщения, URL постера или None)
        """
        # Извлечение данных
        name = movie.get("name", movie.get("alternativeName", "Без названия"))
        name = MovieDataProcessor.clean_html(name)
        year = movie.get("year", "—")
        rating = movie.get("rating", {}).get("kp", 0)
        
        # Жанры
        genres = movie.get("genres", [])
        genres_str = ", ".join([MovieDataProcessor.clean_html(g.get("name", "")) for g in genres[:3]]) if genres else "—"
        
        # Описание
        description = movie.get("shortDescription", movie.get("description", ""))
        description = MovieDataProcessor.clean_html(description)
        if description and len(description) > 200:
            description = description[:200] + "..."
        
        # Постер
        poster_url = None
        if include_poster:
            poster = movie.get("poster", {})
            poster_url = poster.get("url") or poster.get("previewUrl")
        
        # Анализ данных
        analysis = MovieDataProcessor.analyze_movie_data(movie)
        
        # Формирование сообщения
        message = f"🎬 <b>{name}</b> ({year})\n\n"
        message += f"⭐️ Рейтинг: <b>{rating:.1f}</b>/10\n"
        message += f"📊 Оценок: {analysis['votes_formatted']}\n"
        message += f"🎭 Жанр: {genres_str}\n"
        message += f"🏆 Качество: {analysis['quality']}\n"
        message += f"📈 Популярность: {analysis['popularity']}\n"
        message += f"📅 Эпоха: {analysis['era']}\n"
        
        if description:
            message += f"\n📝 {description}\n"
        
        return message, poster_url
    
    @staticmethod
    def format_movies_list(movies: List[Dict], title: str = "Фильмы") -> str:
        """
        Форматирование списка фильмов для жанров (компактный вид в одно сообщение)
        
        Args:
            movies: Список фильмов
            title: Заголовок списка
            
        Returns:
            Отформатированный текст
        """
        message = f"🎬 <b>{title}</b>\n\n"
        
        for i, movie in enumerate(movies, 1):
            name = movie.get("name", movie.get("alternativeName", "Без названия"))
            name = MovieDataProcessor.clean_html(name)
            year = movie.get("year", "—")
            rating = movie.get("rating", {}).get("kp", 0)
            
            # Жанры
            genres = movie.get("genres", [])
            genres_str = ", ".join([MovieDataProcessor.clean_html(g.get("name", "")) for g in genres[:2]]) if genres else "—"
            
            message += f"<b>{i}.</b> {name} ({year})\n"
            message += f"   ⭐️ {rating:.1f} | 🎭 {genres_str}\n\n"
        
        return message
    
    @staticmethod
    def format_popular_list(movies: List[Dict]) -> str:
        """
        Форматирование списка популярных фильмов и сериалов (то что сейчас смотрят)
        Показывает название, год и тип (фильм/сериал)
        
        Args:
            movies: Список фильмов
            
        Returns:
            Отформатированный текст
        """
        message = "🔥 <b>Что сейчас смотрят (популярные новинки)</b>\n"
        message += "<i>По данным посещаемости Кинопоиска</i>\n\n"
        
        for i, movie in enumerate(movies, 1):
            name = movie.get("name", movie.get("alternativeName", "Без названия"))
            name = MovieDataProcessor.clean_html(name)
            year = movie.get("year", "—")
            
            # Определяем тип (фильм или сериал)
            movie_type = movie.get("type", "")
            if movie_type == "tv-series":
                type_emoji = "📺"
                type_text = "Сериал"
            else:
                type_emoji = "🎬"
                type_text = "Фильм"
            
            # Эмодзи для топ-3
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📌"
            
            message += f"{emoji} <b>{i}.</b> {name} ({year}) {type_emoji} <i>{type_text}</i>\n"
        
        return message
    
    @staticmethod
    def deduplicate_movies(movies: List[Dict]) -> List[Dict]:
        """
        Удаление дубликатов фильмов
        
        Args:
            movies: Список фильмов
            
        Returns:
            Список без дубликатов
        """
        seen_ids = set()
        unique_movies = []
        
        for movie in movies:
            movie_id = movie.get("id")
            if movie_id and movie_id not in seen_ids:
                seen_ids.add(movie_id)
                unique_movies.append(movie)
        
        return unique_movies