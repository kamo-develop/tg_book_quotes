
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from tgbot.services import UserService


# Управление доступом
class ACLMiddleware(BaseMiddleware):

    # Берёт пользователя из базы или создаёт нового и ставит флаг нового запуска
    @staticmethod
    async def setup_current_user(data: dict, user: types.User):
        # todo: отслеживать изменение имени и логина пользователя и обновлять данные в базе
        current_user = await UserService.get_user_by_tg_id(user.id)
        if not current_user:
            current_user = await UserService.create_user(user)
            data["is_new_user"] = True
        else:
            data["is_new_user"] = False
        if current_user.username is None and user.username is not None:
            current_user = await UserService.set_username(user=current_user, new_username=user.username)
        # if current_user.username != user.username:
        #     current_user = await UserService.set_username(user=current_user, new_username=user.username)
        # if current_user.full_name != user.full_name:
        #     current_user = await UserService.set_fullname(user=current_user, new_fullname=user.full_name)

        data["user"] = current_user

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.setup_current_user(data, message.from_user)

    async def on_pre_process_callback_query(self, call: types.CallbackQuery, data: dict):
        await self.setup_current_user(data, call.from_user)
