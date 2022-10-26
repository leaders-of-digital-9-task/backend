from django.apps import AppConfig


class DicomConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dicom"

    def ready(self):
        try:
            import image_markuper.dicom.signals  # noqa F401
        except ImportError:
            pass
