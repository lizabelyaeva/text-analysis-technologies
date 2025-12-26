# user_storage.py
"""
Хранилище данных пользователей для многопользовательского режима
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserStorage:
    """
    Класс для хранения данных пользователей
    Обеспечивает многопользовательский режим работы бота
    """
    
    def __init__(self):
        """Инициализация хранилища"""
        # Словарь для хранения данных: {user_id: user_data}
        self._users: Dict[int, Dict] = {}
        # Счетчик запросов для статистики
        self._request_counter: Dict[int, int] = {}
    
    def get_user_data(self, user_id: int) -> Dict:
        """
        Получение данных пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Словарь с данными пользователя
        """
        if user_id not in self._users:
            # Создание новой записи для пользователя
            self._users[user_id] = {
                "user_id": user_id,
                "first_seen": datetime.now(),
                "last_activity": datetime.now(),
                "search_history": [],
                "favorite_genres": [],
                "total_requests": 0
            }
            self._request_counter[user_id] = 0
            logger.info(f"Создан новый пользователь: {user_id}")
        
        return self._users[user_id]
    
    def update_last_activity(self, user_id: int):
        """
        Обновление времени последней активности
        
        Args:
            user_id: ID пользователя
        """
        user_data = self.get_user_data(user_id)
        user_data["last_activity"] = datetime.now()
        user_data["total_requests"] += 1
    
    def add_to_search_history(self, user_id: int, query: str, query_type: str):
        """
        Добавление запроса в историю поиска
        
        Args:
            user_id: ID пользователя
            query: Текст запроса
            query_type: Тип запроса (movie, genre, top, random)
        """
        user_data = self.get_user_data(user_id)
        history_entry = {
            "query": query,
            "type": query_type,
            "timestamp": datetime.now()
        }
        
        # Ограничиваем историю последними 20 запросами
        user_data["search_history"].append(history_entry)
        if len(user_data["search_history"]) > 20:
            user_data["search_history"] = user_data["search_history"][-20:]
        
        self.update_last_activity(user_id)
    
    def add_favorite_genre(self, user_id: int, genre: str):
        """
        Добавление жанра в избранное (для будущих рекомендаций)
        
        Args:
            user_id: ID пользователя
            genre: Название жанра
        """
        user_data = self.get_user_data(user_id)
        
        # Подсчет частоты запросов жанра
        if genre not in user_data["favorite_genres"]:
            user_data["favorite_genres"].append(genre)
    
    def get_user_statistics(self, user_id: int) -> str:
        """
        Получение статистики пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Форматированная строка со статистикой
        """
        user_data = self.get_user_data(user_id)
        
        first_seen = user_data["first_seen"].strftime("%d.%m.%Y")
        total_requests = user_data["total_requests"]
        history_count = len(user_data["search_history"])
        
        stats = f"📊 <b>Ваша статистика:</b>\n\n"
        stats += f"📅 С нами с: {first_seen}\n"
        stats += f"🔍 Всего запросов: {total_requests}\n"
        stats += f"📜 Записей в истории: {history_count}\n"
        
        if user_data["favorite_genres"]:
            genres = ", ".join(user_data["favorite_genres"][:3])
            stats += f"❤️ Любимые жанры: {genres}\n"
        
        return stats
    
    def get_total_users(self) -> int:
        """
        Получение общего количества пользователей
        
        Returns:
            Количество пользователей
        """
        return len(self._users)
    
    def get_active_users(self, minutes: int = 60) -> int:
        """
        Получение количества активных пользователей за период
        
        Args:
            minutes: Период в минутах
            
        Returns:
            Количество активных пользователей
        """
        now = datetime.now()
        active = 0
        
        for user_data in self._users.values():
            last_activity = user_data["last_activity"]
            time_diff = (now - last_activity).total_seconds() / 60
            
            if time_diff <= minutes:
                active += 1
        
        return active
    
    def increment_request_counter(self, user_id: int):
        """
        Увеличение счетчика запросов
        
        Args:
            user_id: ID пользователя
        """
        if user_id not in self._request_counter:
            self._request_counter[user_id] = 0
        
        self._request_counter[user_id] += 1
    
    def get_request_count(self, user_id: int) -> int:
        """
        Получение количества запросов пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Количество запросов
        """
        return self._request_counter.get(user_id, 0)