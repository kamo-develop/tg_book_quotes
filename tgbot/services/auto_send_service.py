import logging

from aiogram import Bot, Dispatcher
from aiogram.utils.exceptions import BotBlocked, InvalidHTTPUrlContent, BadRequest

from tgbot.keyboards.inline import get_quote_menu_keyboard
from tgbot.misc.log_settings import RequestIdAdapter
from tgbot.misc.messages import Messages
from tgbot.services import UserService
from tgbot.services.file_service import FileService
from tgbot.services.quote_service import QuoteService

logger = logging.getLogger(__name__)
logger = RequestIdAdapter(logger, {'id': None})


class AutoSendService:

    @staticmethod
    async def mass_sending(bot: Bot, request_id: str):
        # Получение пользовтелей с давней активностью
        users_tg_id = await UserService.get_long_time_ago_users()

        for tg_id in users_tg_id:
            try:
                # Получение цитаты для текущего пользователя
                user = await UserService.get_user_by_tg_id(tg_id)
                user_state = Dispatcher.get_current().current_state(chat=tg_id, user=tg_id)
                next_quote = await QuoteService.get_next_quote(user, user_state, request_id)

                # todo: код частично дублирует код из хендлера next_quote
                logger.info(f'Next AUTO SENDING quote {next_quote} for {user} from {next_quote.book}', id=request_id)
                user_quote_id = await QuoteService.save_user_auto_sending_quote(
                    quote_id=next_quote.quote_id,
                    user_id=user.user_id
                )

                # Отправка цитаты
                message_text = Messages.get_quote_text(next_quote, request_id)
                try:
                    cover_image = await FileService.get_book_cover(next_quote.book, bot['config'], request_id)
                    await bot.send_photo(
                        chat_id=tg_id,
                        photo=cover_image
                    )
                except InvalidHTTPUrlContent as ex:
                    logger.exception("InvalidHTTPUrlContent exception", id=request_id)
                except BadRequest as ex:
                    logger.exception("BadRequest during image loading", id=request_id)

                await bot.send_message(
                    chat_id=tg_id,
                    text=message_text,
                    reply_markup=get_quote_menu_keyboard(user_quote_id=user_quote_id),
                    disable_web_page_preview=True
                )
            except BotBlocked:
                logger.warning(f"Bot was BLOCKED by user {tg_id}", id=request_id)
