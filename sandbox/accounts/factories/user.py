import factory

from accounts.models import User
from test_utils.factory import BaseModelFactory


class UserFactory(BaseModelFactory[User]):
    email = factory.Faker("email")  # type:ignore[attr-defined,no-untyped-call]
    password = "password"
    is_active = True
    is_superuser = False
    is_staff = False
