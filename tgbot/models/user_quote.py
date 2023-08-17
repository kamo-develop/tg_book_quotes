from tortoise import fields
from tortoise.models import Model

from tgbot.models import User, Quote


class UserQuote(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        model_name='models.User',
        related_name='user_quote'
    )
    quote: fields.ForeignKeyRelation[Quote] = fields.ForeignKeyField(
        model_name='models.Quote',
        related_name='user_quote'
    )

    created = fields.DatetimeField(auto_now_add=True)
    like = fields.BooleanField(default=False)
    dislike = fields.BooleanField(default=False)

    class Meta:
        table = 'user_quote'

    def __str__(self):
        return f'{{ {self.id} }}'
