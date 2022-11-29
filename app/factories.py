import factory


class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "authtoken.Token"


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = "auth.User"

    username = factory.Sequence(lambda n: f"User {n + 1}")
    token = factory.RelatedFactory(
        TokenFactory,
        factory_related_name="user",
    )
