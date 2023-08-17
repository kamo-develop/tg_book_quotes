from dataclasses import dataclass

from environs import Env

# 12345BOOKS67890

@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    postgres_uri: str


@dataclass
class RedisConfig:
    host: str
    password: str
    port: int
    prefix: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class Miscellaneous:
    media_dir: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous
    redis: RedisConfig


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    db_host = env.str('DB_HOST')
    db_pass = env.str('DB_PASS')
    db_user = env.str('DB_USER')
    db_name = env.str('DB_NAME')

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            host=db_host,
            password=db_pass,
            user=db_user,
            database=db_name,
            postgres_uri=f"postgres://{db_user}:{db_pass}@{db_host}/{db_name}"
        ),
        misc=Miscellaneous(
            media_dir=env.str('MEDIA_DIR')
        ),
        redis=RedisConfig(
            host=env.str('REDIS_HOST'),
            port=env.int('REDIS_PORT'),
            password=env.str('REDIS_PASSWORD'),
            prefix=env.str('REDIS_PREFIX')
        )
    )
