from tortoise import fields
from tortoise.models import Model

from tgbot.models import Author, Tag, Genre


class Book(Model):
    book_id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    link = fields.CharField(max_length=1000, null=True)
    cover = fields.CharField(max_length=1000, null=True)
    local_cover = fields.CharField(max_length=100, null=True)
    description = fields.TextField(null=True)
    public_year = fields.IntField(null=True)
    volume = fields.IntField(null=True)
    isbn = fields.CharField(max_length=120, null=True)
    rating = fields.FloatField(null=True)
    likes_count = fields.IntField(null=True)
    quotes_count = fields.IntField(null=True)
    readers_count = fields.IntField(null=True)

    authors: fields.ManyToManyRelation[Author] = fields.ManyToManyField(
        model_name='models.Author',
        related_name='books',
        through='book_author'
    )

    tags: fields.ManyToManyRelation[Tag] = fields.ManyToManyField(
        model_name='models.Tag',
        related_name='books',
        through='book_tag'
    )

    genres: fields.ManyToManyRelation[Genre] = fields.ManyToManyField(
        model_name='models.Genre',
        # related_name='books',
        through='book_genre'
    )

    quotes: fields.ReverseRelation["Quote"]

    class Meta:
        table = "book"

    def __str__(self):
        return f'{{ {self.book_id} : {self.title} }}'
