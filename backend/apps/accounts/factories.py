import factory

from .models import User


class UserFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda number: f"customer{number}@example.test")
    password = factory.PostGenerationMethodCall("set_password", "not-a-real-password")
