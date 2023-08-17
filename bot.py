import asyncio
import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.echo import register_echo
from tgbot.handlers.user_handlers import register_private_handlers
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.middlewares.request_id_middleware import RequestIdMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.middlewares.acl_middleware import ACLMiddleware
from tgbot.misc.db import DataBase
from tgbot.misc.messages import Messages

logger = logging.getLogger(__name__)


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("next", Messages.next_quote_text),
            types.BotCommand("genres", Messages.choice_genre_text),
            types.BotCommand("help", Messages.bot_help_text),
        ]
    )


def register_all_middlewares(dp, config):
    dp.setup_middleware(RequestIdMiddleware())
    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(ThrottlingMiddleware(limit=1))
    dp.setup_middleware(ACLMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_private_handlers(dp)
    register_echo(dp)


async def main():
    logging.basicConfig(
        handlers=[RotatingFileHandler('logs/i.log', maxBytes=1000000, backupCount=10)],
        level=logging.INFO,
        format=u'%(name)s %(funcName)s :%(lineno)d [%(asctime)s] #%(levelname)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    # Подключение к базе данных
    await DataBase.connect_db(postgres_uri=config.db.postgres_uri)
    await DataBase.init_db()

    # Инициализация бота
    storage = RedisStorage2(host=config.redis.host, port=config.redis.port, prefix=config.redis.prefix) \
        if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)
    await dp.skip_updates()
    await set_default_commands(dp)

    # todo: Сделать обработку TerminatedByOtherGetUpdates, чтобы информировать, когда подключается другой бот
    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()
        await DataBase.disconnect_db()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
