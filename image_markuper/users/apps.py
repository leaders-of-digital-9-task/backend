from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "image_markuper.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import image_markuper.users.signals  # noqa F401
        except ImportError:
            pass
