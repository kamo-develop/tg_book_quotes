import logging

from aiogram.utils.markdown import hlink

from tgbot.misc.log_settings import RequestIdAdapter
from tgbot.models import Quote

logger = logging.getLogger(__name__)
logger = RequestIdAdapter(logger, {"id": None})

class Messages:

    bot_name = '📚 Интересные цитаты из книг 📚'
    next_quote_text = '💬 Следующая цитата'
    choice_genre_text = '📚 Выбор жанров'
    bot_help_text = '🆘 Помощь по боту'
    start_quote_text = '💬 Погрузиться в книжный мир'
    throttling_text = 'Не так часто! 🙃'

    first_button_forward = "💬 ВПЕРЁД!"

    any_message_answer = '👆👆👆\nНажмите на нужную Вам кнопку в меню выше, чтобы продолжить 😊'

    help_text = f'📖 Бот присылает Вам самые интересные цитаты из книг тех жанров, которые вы выбрали в меню.\n\n' \
                f'👍 Вы можете оценивать цитаты лайками или дизайками. ' \
                f'Мы будем подбирать для Вас книги и цитаты на основе Ваших предпочтений.\n\n' \
                f'{choice_genre_text} - /genres\n\n' \
                f'{next_quote_text} - /next'

    @staticmethod
    def get_first_greeting(full_name):
        return f"Здравствуйте, {full_name}! 😊\n\n" \
               f"<b>Добро пожаловать в бот с самыми интересными цитатами из книг!</b>\n\n" \
                f"📖 Здесь можно получать цитаты из книг, которые подобраны специально для Вас\n\n" \
                f"📚 Вы можете выбрать те жанры, которые Вам по душе, и погрузиться в разнообразнейший книжный мир.\n\n" \
               f"Не забывайте ставить 👍 или 👎, и мы через некоторое время начнём подбирать для Вас книги и цитаты на основе Ваших предпочтений."

    @staticmethod
    def get_first_choice_genre():
        return f'📚 Можете выбрать любимые жанры и погрузиться в книжный мир.\n\n' \
               f'👇👇👇'
               # f'Не знаете, что выбрать?\nНичего страшного, бот подстроиться под Ваши предпочтения, главное не забывайте оценивать цитаты.\n\n👇👇👇'

    @staticmethod
    def get_quote_text(quote: Quote, request_id: str):
        name_authors = ''
        for author in quote.book.authors:
            name_authors += author.name + ', '
        name_authors = name_authors[:-2]

        title_genres = ''
        for genre in quote.book.genres:
            title_genres += genre.title + ', '
        title_genres = title_genres[:-2]

        book_link = hlink('https://www.livelib.ru/book...', quote.book.link)
        result = f'📖 <b>{quote.book.title}</b>\n' \
                 f'<i>{name_authors}</i>\n' \
                 f'<i>{quote.book.public_year}</i>\n\n' \
                 f'<b>"{quote.text}"</b>\n\n' \
                 f'{book_link}\n\n' \
                 f'{Messages.choice_genre_text} - /genres'
        if len(result) > 4000:
            logger.warning(f'Too long quote {quote}', id=request_id)
        return result

    @staticmethod
    def get_choice_genres():
        return '📚 Выберите интересующие Вас жанры и получайте цитаты только из тех книг, которые Вам по душе.\n\n👇👇👇'

    @staticmethod
    def get_like_reaction(is_like: bool):
        # rating_symbol = '👍' if is_like else '👎'
        # return f'Мы учтём в будущем Ваш {rating_symbol} для рекомендаций.\nНо это не точно 🤭\n\n' \
        #        f'{Messages.next_quote_text} - /next'
        return '☺️😊👆' if is_like else '🤔😌👆'
