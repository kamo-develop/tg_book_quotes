from tortoise import fields
from tortoise.models import Model


class Author(Model):
    author_id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    link = fields.CharField(max_length=1000, null=True)

    books: fields.ManyToManyRelation["Book"]

    class Meta:
        table = "author"

    def __str__(self):
        return f'{self.author_id} : {self.name}  {self.link}'
