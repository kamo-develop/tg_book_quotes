from aiogram import Bot

from tgbot.config import Config
from tgbot.models import User


class AdminNotification:
    @staticmethod
    async def new_user(user: User, bot: Bot):
        admins = bot['config'].tg_bot.admin_ids
        for admin_id in admins:
            await bot.send_message(chat_id=admin_id, text=f"New user: {user}")
