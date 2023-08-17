from tortoise import fields
from tortoise.models import Model


class Tag(Model):
    tag_id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    link = fields.CharField(max_length=1000, null=True)

    books: fields.ManyToManyRelation["Book"]

    class Meta:
        table = "tag"

    def __str__(self):
        return f'{self.tag_id} : {self.title}  {self.link}'
