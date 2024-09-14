from pydantic import ValidationError
from schemas import CreateUser


def test_user_incorrect_group():
    try:
        test_user = CreateUser(
            email="test@test.com", password="test", user_group="test"
        )
        assert False
    except Exception as e:
        assert isinstance(e, ValidationError)


def test_user_incorrect_email():
    try:
        test_user = CreateUser(
            email="test@test.test", password="test", user_group="developer"
        )
        assert False
    except Exception as e:
        assert isinstance(e, ValidationError)


def test_user_incorrect_password():
    try:
        test_user = CreateUser(
            email="test@test.com", password="", user_group="developer"
        )
        assert False
    except Exception as e:
        assert isinstance(e, ValidationError)


"""down there might be your additional api tests, I'll settle for manual testing"""
