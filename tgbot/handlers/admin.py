import logging

from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.keyboards.inline import get_thanks_keyboard
from tgbot.misc.log_settings import RequestIdAdapter
from tgbot.misc.messages import Messages
from tgbot.models import User
from tgbot.services import UserService
from tgbot.services.auto_send_service import AutoSendService

logger = logging.getLogger(__name__)
logger = RequestIdAdapter(logger, {"id": None})


async def admin_start(message: Message, user: User, request_id: str):
    logger.info(f'Admin start command {user} ', id=request_id)
    await message.reply("Hello, admin!")


async def admin_mass_sending(message: Message, user: User, request_id: str):
    logger.info(f'Admin {user} mass sending command', id=request_id)
    await AutoSendService.mass_sending(message.bot, request_id)


async def admin_leader_sending_message(message: Message, user: User, request_id: str):
    user_id = message.get_args().split()[0]
    to_user = await UserService.get_user_by_id(user_id)
    logger.info(f'Admin {user} leader sending command for user {to_user} ', id=request_id)
    await message.bot.send_message(
        chat_id=to_user.tg_id,
        text=Messages.get_leader_message(to_user.full_name),
        reply_markup=get_thanks_keyboard()
    )
    await message.bot.send_message(
        chat_id=to_user.tg_id,
        text='🥇'
    )


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_message_handler(admin_mass_sending, commands=["mass_send"], state='*', is_admin=True)
    dp.register_message_handler(admin_leader_sending_message, commands=["leader_is"], state='*', is_admin=True)

