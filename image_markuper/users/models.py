from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class User(AbstractUser):
    """
    Default custom user model for Image markuper.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    first_name = None  # type: ignore
    last_name = None  # type: ignore
    email = None  # type: ignore

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
