from django.conf import settings

from weekly_feedback.settings import database_config_from_env


def test_django_settings_load_without_external_services():
    assert settings.ROOT_URLCONF == "weekly_feedback.urls"
    assert "django.contrib.admin" in settings.INSTALLED_APPS
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"


def test_database_config_uses_postgresql_environment(monkeypatch):
    monkeypatch.setenv("POSTGRES_DB", "feedback_dev")
    monkeypatch.setenv("POSTGRES_USER", "feedback_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "feedback_password")
    monkeypatch.setenv("POSTGRES_HOST", "postgres")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("POSTGRES_TEST_DB", "feedback_test")

    config = database_config_from_env()

    assert config == {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "feedback_dev",
        "USER": "feedback_user",
        "PASSWORD": "feedback_password",
        "HOST": "postgres",
        "PORT": "5433",
        "TEST": {
            "NAME": "feedback_test",
        },
    }
