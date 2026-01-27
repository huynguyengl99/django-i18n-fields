from django.test import TestCase

import pytest

from accounts.factories.user import UserFactory
from accounts.models import User


class UserManagerTestCase(TestCase):
    def test_create_user(self) -> None:
        assert User.objects.count() == 0

        fake_password = "fake_password"
        user = User.objects.create_user(email="user@mail.com", password=fake_password)

        assert User.objects.count() == 1
        assert not user.password == fake_password

    def test_create_user_no_email(self) -> None:
        assert User.objects.count() == 0
        with pytest.raises(ValueError, match="Users must have an email address"):
            fake_password = "fake_password"
            User.objects.create_user(email=None, password=fake_password)  # type: ignore[arg-type]  # ignore mypy for test

        assert User.objects.count() == 0

    def test_create_super_user(self) -> None:
        assert User.objects.count() == 0

        fake_password = "fake_password"
        user = User.objects.create_superuser(
            email="user@mail.com", password=fake_password
        )

        assert User.objects.count() == 1
        assert user.is_superuser
        assert not user.password == fake_password


class UserModelTestCase(TestCase):
    def test_normal_user(self) -> None:
        user = UserFactory.create()
        assert str(user) == user.email
        assert not user.is_staff

    def test_superuser(self) -> None:
        user = UserFactory.create(is_superuser=True)
        assert str(user) == user.email
        assert user.is_superuser
