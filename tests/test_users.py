import uuid

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError


@pytest.mark.django_db
def test_user_creation_with_required_product_fields():
    user = get_user_model().objects.create_user(
        username="ada",
        email="ada@example.com",
        password="test-password",
        name="Ada Lovelace",
        role=get_user_model().Role.LEAD,
        slack_user_id="U123456",
    )

    assert isinstance(user.id, uuid.UUID)
    assert user.email == "ada@example.com"
    assert user.name == "Ada Lovelace"
    assert user.role == get_user_model().Role.LEAD
    assert user.slack_user_id == "U123456"
    assert user.created_at is not None


@pytest.mark.django_db
def test_duplicate_slack_user_id_is_rejected():
    get_user_model().objects.create_user(
        username="grace",
        email="grace@example.com",
        password="test-password",
        name="Grace Hopper",
        slack_user_id="U123456",
    )

    with pytest.raises(IntegrityError):
        get_user_model().objects.create_user(
            username="katherine",
            email="katherine@example.com",
            password="test-password",
            name="Katherine Johnson",
            slack_user_id="U123456",
        )


@pytest.mark.django_db
def test_multiple_users_can_exist_without_slack_user_id():
    get_user_model().objects.create_user(
        username="dorothy",
        email="dorothy@example.com",
        password="test-password",
        name="Dorothy Vaughan",
    )
    get_user_model().objects.create_user(
        username="mary",
        email="mary@example.com",
        password="test-password",
        name="Mary Jackson",
    )

    assert get_user_model().objects.filter(slack_user_id__isnull=True).count() == 2


def test_custom_user_model_is_configured(settings):
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert {choice.value for choice in get_user_model().Role} == {
        "MEMBER",
        "LEAD",
        "ADMIN",
    }
