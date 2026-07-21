import factory

from comments.models import Comment


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    user_name = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    home_page = "https://example.com"
    text = "Test comment"
    parent = None
                                               