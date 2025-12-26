# api_client.py
"""
Клиент для работы с API Кинопоиска
Реализует все запросы к внешнему API
"""

import requests
from typing import Optional, List, Dict, Any
import logging
from config import KINOPOISK_API_KEY, KINOPOISK_API_URL

logger = logging.getLogger(__name__)


class KinopoiskAPIClient:
    """Клиент для работы с API Кинопоиска"""
    
    def __init__(self, api_key: str):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ для доступа к Кинопоиску
        """
        self.api_key = api_key
        self.base_url = KINOPOISK_API_URL
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """
        Выполняет HTTP-запрос к API
        
        Args:
            endpoint: Конечная точка API
            params: Параметры запроса
            
        Returns:
            Словарь с ответом или None в случае ошибки
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к API: {e}")
            return None
    
    def search_movie_by_name(self, name: str, limit: int = 5) -> List[Dict]:
        """
        Поиск фильма по названию
        
        Args:
            name: Название фильма
            limit: Максимальное количество результатов
            
        Returns:
            Список найденных фильмов
        """
        params = {
            "page": 1,
            "limit": limit,
            "query": name,
            "type": "movie"
        }
        
        result = self._make_request("movie/search", params)
        
        if result and "docs" in result:
            return result["docs"]
        return []
    
    def get_movies_by_genre(self, genre: str, limit: int = 10, 
                           min_rating: float = 7.0) -> List[Dict]:
        """
        Получение фильмов по жанру с фильтрацией по рейтингу
        
        Args:
            genre: Название жанра
            limit: Максимальное количество результатов
            min_rating: Минимальный рейтинг
            
        Returns:
            Список фильмов
        """
        params = {
            "page": 1,
            "limit": limit,
            "genres.name": genre,
            "rating.kp": f"{min_rating}-10",
            "sortField": "rating.kp",
            "sortType": "-1",
            "type": "movie"
        }
        
        result = self._make_request("movie", params)
        
        if result and "docs" in result:
            return result["docs"]
        return []
    
    def get_top_movies(self, limit: int = 10, min_rating: float = 8.0) -> List[Dict]:
        """
        Получение топ фильмов по рейтингу
        
        Args:
            limit: Количество фильмов
            min_rating: Минимальный рейтинг
            
        Returns:
            Список лучших фильмов
        """
        params = {
            "page": 1,
            "limit": limit,
            "rating.kp": f"{min_rating}-10",
            "votes.kp": "100000-10000000",  # Только популярные фильмы
            "sortField": "rating.kp",
            "sortType": "-1",
            "type": "movie"
        }
        
        result = self._make_request("movie", params)
        
        if result and "docs" in result:
            return result["docs"]
        return []
    
    def get_random_movie(self, min_rating: float = 7.0) -> Optional[Dict]:
        """
        Получение случайного фильма с хорошим рейтингом
        
        Args:
            min_rating: Минимальный рейтинг
            
        Returns:
            Случайный фильм
        """
        import random
        
        # Получаем случайную страницу от 1 до 50
        random_page = random.randint(1, 50)
        
        params = {
            "page": random_page,
            "limit": 10,
            "rating.kp": f"{min_rating}-10",
            "votes.kp": "10000-10000000",
            "type": "movie"
        }
        
        result = self._make_request("movie", params)
        
        if result and "docs" in result and len(result["docs"]) > 0:
            # Выбираем случайный фильм из полученных
            return random.choice(result["docs"])
        return None
    
    def get_popular_movies(self, limit: int = 10) -> List[Dict]:
        """
        Получение популярных фильмов (то что сейчас смотрят)
        Сортируется по посещаемости - новинки и популярные сериалы
        
        Args:
            limit: Количество фильмов
            
        Returns:
            Список популярных фильмов
        """
        # Получаем популярные фильмы и сериалы за последние 2 года
        # Сортируем по количеству просмотров (votes.kp) - это показатель популярности
        params = {
            "page": 1,
            "limit": limit,
            "year": "2025",  # Только свежие
            "votes.kp": "10000-10000000",  # Только с большим количеством просмотров
            "sortField": "votes.kp",  # Сортируем по популярности
            "sortType": "-1",  # По убыванию
            "type": ["movie", "tv-series"]  # Фильмы и сериалы
        }
        
        result = self._make_request("movie", params)
        
        if result and "docs" in result:
            return result["docs"]
        return []