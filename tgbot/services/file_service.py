import logging

from aiogram.types import InputFile

from tgbot.config import Config
from tgbot.misc.log_settings import RequestIdAdapter
from tgbot.models import Book

logger = logging.getLogger(__name__)
logger = RequestIdAdapter(logger, {'id': None})


class FileService:

    @staticmethod
    async def get_image(image_name: str, config: Config):
        # todo: обработать отсутствие картинки, чтобы не отправлять её
        return InputFile(path_or_bytesio=f'{config.misc.media_dir}/{image_name}')


    @staticmethod
    async def get_book_cover(book: Book, config: Config, request_id: str):
        if book.local_cover is None:
            logger.info(f'Book cover {book} download from site', id=request_id)
            return book.cover
        else:
            logger.info(f'Book cover {book} download from local storage', id=request_id)
            cover_image = await FileService.get_image(book.local_cover, config)
            return cover_image