from tortoise import fields
from tortoise.models import Model

from tgbot.models import Book, Genre


class BookGenre(Model):
    id = fields.IntField(pk=True)
    book: fields.ForeignKeyRelation[Book] = fields.ForeignKeyField(
        model_name='models.Book',
        related_name='book_genres'
    )
    genre: fields.ForeignKeyRelation[Genre] = fields.ForeignKeyField(
        model_name='models.Genre',
        related_name='book_genres'
    )
    is_top = fields.BooleanField(default=False)

    class Meta:
        table = "book_genre"

    def __str__(self):
        return f'{self.id}'
