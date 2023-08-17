import asyncio
import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter, CommandStart
from aiogram.types import Message, ChatType, CallbackQuery, InputFile
from aiogram.utils.exceptions import InvalidHTTPUrlContent, BadRequest

from tgbot.config import Config
from tgbot.keyboards.inline import get_quote_menu_keyboard, quote_menu_callback, get_genres_choice_keyboard, \
    genres_choice_menu_callback, get_next_quote_menu_keyboard, get_first_start_keyboard, first_start_menu_callback
from tgbot.misc.log_settings import RequestIdAdapter
from tgbot.misc.messages import Messages
from tgbot.models import User
from tgbot.services import UserService
from tgbot.services.file_service import FileService
from tgbot.services.quote_service import QuoteService

logger = logging.getLogger(__name__)
logger = RequestIdAdapter(logger, {"id": None})


async def next_handler(message: Message, user: User, state: FSMContext, request_id: str):
    logger.info(f"Next command from {user}", id=request_id)
    await next_quote(message, user, state, request_id)


async def next_quote(message: Message, user: User, state: FSMContext, request_id: str):
    # Получить цитату и сохранить факт её просмотра
    next_quote = await QuoteService.get_next_quote(user, state, request_id)
    logger.info(f'Next quote {next_quote} for {user} from {next_quote.book}', id=request_id)
    user_quote_id = await QuoteService.save_user_viewing_quote(quote_id=next_quote.quote_id, user_id=user.user_id)

    message_text = Messages.get_quote_text(next_quote, request_id)
    try:
        cover_image = await FileService.get_book_cover(next_quote.book, message.bot['config'], request_id)
        await message.answer_photo(
            photo=cover_image
        )
    except InvalidHTTPUrlContent as ex:
        logger.exception("InvalidHTTPUrlContent exception", id=request_id)
    except BadRequest as ex:
        logger.exception("BadRequest during image loading", id=request_id)

    # Задержка после фото
    await message.answer_chat_action("typing")
    await asyncio.sleep(0.5)

    await message.answer(
        text=message_text,
        reply_markup=get_quote_menu_keyboard(user_quote_id=user_quote_id),
        disable_web_page_preview=True
    )


async def start_handler(message: Message, user: User, is_new_user: bool, state: FSMContext, request_id: str):
    logger.info(f"Start command from {user}", id=request_id)

    if is_new_user:
        logger.info(f"New user {user}", id=request_id)

        greeting_photo = await FileService.get_image('books_for_greeting.jpg', message.bot['config'])
        await message.answer_photo(
            photo=greeting_photo,
            caption=Messages.get_first_greeting(full_name=message.from_user.full_name),
            reply_markup=get_first_start_keyboard()
        )
    else:
        await next_quote(message, user, state, request_id)


async def first_genres_choice_handler(call: CallbackQuery, user: User, request_id: str):
    await call.answer(cache_time=3)
    logger.info(f'Forward button from {user}')
    genres_preferences = await UserService.get_genres_preferences_for_menu(user)

    await call.message.answer(
        text=Messages.get_first_choice_genre(),
        reply_markup=get_genres_choice_keyboard(genres_preferences, True)
    )
    await call.message.edit_reply_markup()


# меню выбора жанров
async def genres_choice_handler(message: Message, user: User, request_id: str):
    logger.info(f'Genres choice menu for {user}', id=request_id)
    genres_preferences = await UserService.get_genres_preferences_for_menu(user)

    await message.answer(
        text=Messages.get_choice_genres(),
        reply_markup=get_genres_choice_keyboard(genres_preferences, False)
    )


# Обработка кнопок лайка и дизлайка
async def like_callback_handler(call: CallbackQuery, callback_data: dict, state: FSMContext, user: User, request_id: str):
    await call.answer(cache_time=3)
    await call.message.edit_reply_markup(
        reply_markup=get_next_quote_menu_keyboard()
    )

    # Получение данных от кнопки
    user_quote_id = int(callback_data.get('user_quote_id'))
    is_like = bool(int(callback_data.get('is_like')))

    logger.info(f"{'Like' if is_like else 'DisLike'} from {user} for user_quote {{ {user_quote_id} }}", id=request_id)

    # Сохранение лайка или дизлайка
    await QuoteService.set_like(user_quote_id, is_like)
    await call.message.answer(
        text=Messages.get_like_reaction(is_like),
        # reply_markup=get_next_quote_menu_keyboard()
    )


# для кнопки перехода к следующей цитате
async def next_quote_callback_handler(call: CallbackQuery, user: User, state: FSMContext, request_id: str):
    logger.info(f"Next Button from {user}", id=request_id)
    await call.answer(cache_time=3)
    await next_quote(call.message, user, state, request_id)


# Обработка кнопок выбора жанра
async def genres_choice_callback_handler(call: CallbackQuery, callback_data: dict, user: User, request_id: str):
    genre_id = int(callback_data.get('genre_id'))
    await UserService.set_genres_user_preferences(user, genre_id, request_id)
    # Ответ на call
    await call.answer()
    is_start = int(callback_data.get('is_start'))

    # Обновление меню
    # todo: можно не запрашивать заново меню из базы
    genres_preferences = await UserService.get_genres_preferences_for_menu(user)
    await call.message.edit_reply_markup(
        reply_markup=get_genres_choice_keyboard(genres_preferences, bool(is_start))
    )


def register_private_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, ChatTypeFilter(ChatType.PRIVATE), commands=["start"])
    dp.register_callback_query_handler(first_genres_choice_handler, first_start_menu_callback.filter())
    dp.register_message_handler(next_handler, ChatTypeFilter(ChatType.PRIVATE), commands=["next"])
    dp.register_message_handler(genres_choice_handler, ChatTypeFilter(ChatType.PRIVATE), commands=["genres"])

    dp.register_callback_query_handler(like_callback_handler, quote_menu_callback.filter(action='like'))
    dp.register_callback_query_handler(next_quote_callback_handler, quote_menu_callback.filter(action='next'))

    dp.register_callback_query_handler(genres_choice_callback_handler, genres_choice_menu_callback.filter(action='genre'))
    dp.register_callback_query_handler(next_quote_callback_handler, genres_choice_menu_callback.filter(action='next'))
