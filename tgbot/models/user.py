from tortoise import fields
from tortoise.models import Model

from tgbot.models import Quote, Genre


class User(Model):
    user_id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255)
    tg_id = fields.BigIntField()

    quotes: fields.ManyToManyRelation[Quote] = fields.ManyToManyField(
        model_name='models.Quote',
        through='user_quote'
    )

    genres: fields.ManyToManyRelation[Genre] = fields.ManyToManyField(
        model_name='models.Genre',
        related_name='users',
        through='user_genre'
    )

    class Meta:
        table = "user_tg"

    def __str__(self):
        return f"{{ {self.user_id} : {self.username} : {self.full_name} }}"
