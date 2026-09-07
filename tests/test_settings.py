from django.conf import settings


def test_django_settings_load_without_external_services():
    assert settings.ROOT_URLCONF == "weekly_feedback.urls"
    assert "django.contrib.admin" in settings.INSTALLED_APPS
