from tortoise import fields
from tortoise.models import Model


class Genre(Model):
    genre_id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    alias = fields.CharField(max_length=50)
    link = fields.CharField(max_length=1000, null=True)
    is_menu = fields.BooleanField(default=False)
    ordinal_number = fields.IntField(null=True)

    parent: fields.ForeignKeyRelation["Genre"] = \
        fields.ForeignKeyField(model_name='models.Genre', related_name='children', null=True)

    books: fields.ManyToManyRelation["Book"]

    users: fields.ManyToManyRelation["User"]

    class Meta:
        table = "genre"

    def __str__(self):
        return f'{{ {self.genre_id} : {self.title} }}'
