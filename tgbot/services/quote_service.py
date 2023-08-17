import logging
import random

from aiogram.dispatcher import FSMContext
from tortoise import Tortoise
from tortoise.expressions import Q

from tgbot.misc.log_settings import RequestIdAdapter
from tgbot.models import Quote, UserQuote, User, Genre

logger = logging.getLogger(__name__)
logger = RequestIdAdapter(logger, {'id': None})


class QuoteService:
    @staticmethod
    async def get_next_quote(user: User, state: FSMContext, request_id: str) -> Quote:
        # не просмотреные книги пользователем в заданном жанре
        query_unseen_book = """
            SELECT book_id
            FROM (
                SELECT book_id, quote_id
                FROM user_quote
                JOIN quote USING(quote_id)
                WHERE user_id = $1
            ) AS viewed_quotes
            RIGHT OUTER JOIN book USING(book_id)
            JOIN book_genre USING(book_id)
            WHERE genre_id = $2
            AND quote_id is NULL
            AND book.quotes_count > 10
            LIMIT 30
        """
        #  ORDER BY book.readers_count DESC

        # Список книг жанра отсортированных по возрастанию количества просмотренных в них цитат
        query_count_quotes_by_book = """
            SELECT book_id
            FROM user_quote
            JOIN quote USING(quote_id)
            JOIN book USING(book_id)
            JOIN book_genre USING(book_id)
            WHERE user_id = $1
            AND genre_id = $2
            GROUP BY book_id
            ORDER BY COUNT(quote_id)
            LIMIT 10
        """

        # Список цитат по популярности, которых ещё не видел пользователь, из заданной книги
        query_unseen_quote_from_book = """
            SELECT quote_id
            FROM
                (SELECT book_id, quote_id
                FROM user_quote
                JOIN quote USING(quote_id)
                WHERE user_id = $1
                AND book_id = $2) as viewed_quotes
            RIGHT OUTER JOIN quote USING(quote_id)
            WHERE quote.book_id = $2
            AND viewed_quotes.quote_id IS NULL
            AND quote.length_text <= 1000
            ORDER BY quote.likes_count DESC
            LIMIT 5
        """
        # todo: нужно разнообразить цитаты, чередую популярные книги и не очень известные

        connect = Tortoise.get_connection('default')
        # выбор рандомного жанра из предпочтительных для пользователя
        genre_id = await QuoteService.choice_random_genre_for_user(user, state, request_id)

        unseen_books = await connect.execute_query_dict(query_unseen_book, [user.user_id, genre_id])
        # если непросмотренных книг больше нет
        if len(unseen_books) == 0:
            logger.info(f'No more unseen books for {user}', id=request_id)
            next_books = await connect.execute_query_dict(query_count_quotes_by_book, [user.user_id, genre_id])
            next_book_id = next_books[random.randint(0, len(next_books) - 1)].get('book_id')
            quotes_from_book = await connect.execute_query_dict(query_unseen_quote_from_book, [user.user_id, next_book_id])
            quote_id = quotes_from_book[random.randint(0, len(quotes_from_book) - 1)].get('quote_id')
            quote = await Quote.filter(quote_id=quote_id).first()
        else:
            # Выбор случайной книги из первых непросмотренных
            next_book_id = unseen_books[random.randint(0, len(unseen_books) - 1)].get('book_id')

            # Выбор случайной цитаты их первых 10ти
            quote = await Quote\
                .filter(Q(book__book_id=next_book_id) & Q(length_text__lte=1000))\
                .order_by('-likes_count')\
                .limit(1)\
                .offset(random.randint(1, 10))\
                .first()

        if quote is None:
            logger.error(f'Quote is None')
        await quote.fetch_related('book', 'book__authors', 'book__genres')
        return quote

    # выбор рандомного жанра из предпочтительных для пользователя
    @staticmethod
    async def choice_random_genre_for_user(user: User, state: FSMContext, request_id: str) -> int:
        # Предыдущие n - 1 жанров, показанных пользователю,
        # где n это общее кол-во выбранных жанров в качестве предпочтительных
        state_data = await state.get_data()
        previous_genres = state_data.get('previous_genres')
        if previous_genres is None:
            previous_genres = set()
        else:
            previous_genres = set(previous_genres)

        # предпочтения пользователя
        user_genres = await Genre.filter(users__user_id=user.user_id).values('genre_id')
        if len(user_genres) == 0:
            logger.info(f'No selected genre for {user}', id=request_id)
            user_genres = await Genre.filter(is_menu=True).values('genre_id')
        user_genres = set([genre.get('genre_id') for genre in user_genres])

        # разность между предпочтениями и предыдущими показанными
        next_genres = user_genres.difference(previous_genres)
        if len(next_genres) == 0:
            previous_genres.clear()
            next_genres = user_genres
        next_genres = list(next_genres)

        # выбор рандомного
        random.seed()
        random_index = random.randint(0, len(next_genres) - 1)
        genre_id = next_genres[random_index]

        # обновление списка предыдущих жанров
        previous_genres.add(genre_id)
        await state.update_data(previous_genres=list(previous_genres))
        logger.info(f'Random genre is {genre_id} for {user}', id=request_id)

        return genre_id

    @staticmethod
    async def save_user_viewing_quote(quote_id: int, user_id: int) -> int:
        user_quote = await UserQuote.create(user_id=user_id, quote_id=quote_id)
        return user_quote.id

    @staticmethod
    async def set_like(user_quote_id: int, is_like: bool):
        user_quote = await UserQuote.get(id=user_quote_id)
        if is_like is True:
            user_quote.like = True
            user_quote.dislike = False
        else:
            user_quote.dislike = True
            user_quote.like = False

        await user_quote.save()
