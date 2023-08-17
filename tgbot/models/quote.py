from tortoise import fields
from tortoise.models import Model

from tgbot.models import Book


class Quote(Model):
    quote_id = fields.IntField(pk=True)
    text = fields.TextField()
    likes_count = fields.IntField(null=True)
    length_text = fields.IntField(null=True)

    book: fields.ForeignKeyRelation[Book] = fields.ForeignKeyField(
        model_name='models.Book',
        related_name='quotes'
    )

    users: fields.ManyToManyRelation["User"]

    class Meta:
        table = "quote"

    def __str__(self):
        return f'{{ {self.quote_id} }}'
