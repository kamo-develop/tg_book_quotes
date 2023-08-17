import datetime
import logging

from aiogram import types

from tgbot.misc.log_settings import RequestIdAdapter
from tgbot.models import User, Genre

logger = logging.getLogger(__name__)
logger = RequestIdAdapter(logger, {'id': None})


class UserService:
    @staticmethod
    async def get_user_by_tg_id(tg_id) -> User:
        return await User.filter(tg_id=tg_id).first()

    @staticmethod
    async def create_user(user: types.User):
        return await User.create(username=user.username, full_name=user.full_name, tg_id=user.id)

    @staticmethod
    async def set_username(user: User, new_username: str):
        user.username = new_username
        return await user.save()

    @staticmethod
    async def get_genres_preferences_for_menu(user: User):
        # Список жанров для выбора
        genres = await Genre.filter(is_menu=True).order_by('ordinal_number').values('genre_id', 'title', 'alias')
        genres_preferences = [
            {
                'title': genre.get('alias'),
                'genre_id': genre.get('genre_id'),
                'is_preferences': False
            } for genre in genres
        ]

        # Определение выбранных пользователем жанров
        await user.fetch_related('genres')
        for user_genre in user.genres:
            matching_genre = next(filter(lambda genre: genre['genre_id'] == user_genre.genre_id, genres_preferences))
            matching_genre['is_preferences'] = True

        return genres_preferences

    @staticmethod
    async def set_genres_user_preferences(user: User, genre_id: int, request_id: str):
        user_genre = await user.genres.filter(genre_id=genre_id).first()

        if user_genre is None:
            # Если этот жанр не был выбран
            genre = await Genre.filter(genre_id=genre_id).first()
            logger.info(f'{user} choice genre {genre}', id=request_id)
            await user.genres.add(genre)
        else:
            # Если жанр уже был выбран
            logger.info(f'{user} remove genre {user_genre}', id=request_id)
            await user.genres.remove(user_genre)


