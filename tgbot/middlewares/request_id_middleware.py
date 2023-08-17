import logging
import uuid

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

logger = logging.getLogger(__name__)

# Присвоение запросу уникального идентификатора
class RequestIdMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        data['request_id'] = str(uuid.uuid4())
        logger.info('\n\n')
        logger.info(f"New request {{ {data['request_id']} }}")

    async def on_pre_process_callback_query(self, call: types.CallbackQuery, data: dict):
        data['request_id'] = str(uuid.uuid4())
        logger.info('\n\n')
        logger.info(f"New request {{ {data['request_id']} }}")

