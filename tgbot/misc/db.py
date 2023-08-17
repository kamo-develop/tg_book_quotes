import logging

from tortoise import Tortoise

from tgbot.misc.log_settings import RequestIdAdapter

logger = logging.getLogger(__name__)
logger = RequestIdAdapter(logger, {"id": None})


class DataBase:

    # Подключение к базе
    @staticmethod
    async def connect_db(postgres_uri: str):
        await Tortoise.init(
            db_url=postgres_uri,
            modules={
                "models": ['tgbot.models']
            }
        )
        logger.info('Connect to Data Base success')

    # Создание таблиц, если они ещё не созданы
    @staticmethod
    async def init_db():
        await Tortoise.generate_schemas(safe=True)
        logger.info('Initialization Data schema success')

    # Отключение от базы
    @staticmethod
    async def disconnect_db():
        await Tortoise.close_connections()