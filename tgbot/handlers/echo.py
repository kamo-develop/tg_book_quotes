import logging

from aiogram import types, Dispatcher

from tgbot.misc.log_settings import RequestIdAdapter
from tgbot.misc.messages import Messages
from tgbot.models import User

logger = logging.getLogger(__name__)
logger = RequestIdAdapter(logger, {"id": None})


async def bot_echo(message: types.Message, user: User, request_id: str):
    logger.info(f'Message {message.text} from user {user}', id=request_id)
    await message.answer(text=Messages.any_message_answer)


async def help_handler(message: types.Message, user: User, request_id: str):
    logger.info(f'Help command from user {user}', id=request_id)
    await message.answer(text=Messages.help_text)


def register_echo(dp: Dispatcher):
    dp.register_message_handler(help_handler, commands=['help'])
    dp.register_message_handler(bot_echo)
