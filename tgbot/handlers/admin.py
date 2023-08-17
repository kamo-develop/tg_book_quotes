import logging

from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.misc.log_settings import RequestIdAdapter
from tgbot.models import User

logger = logging.getLogger(__name__)
logger = RequestIdAdapter(logger, {"id": None})


async def admin_start(message: Message, user: User, request_id: str):
    logger.info(f'Admin start command {user} ', id=request_id)
    await message.reply("Hello, admin!")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
