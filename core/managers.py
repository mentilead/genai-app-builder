import logging
from typing import Any, Dict

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def validate_email(self, email: str) -> str:
        """
        Validates the given email address.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        return self.normalize_email(email)

    def create_and_save_user(self, email: str, password: str, **extra_fields: Dict[str, Any]) -> Any:
        """
        .. function:: create_and_save_user(self, email, password, **extra_fields)

            Creates and saves a new user with the given email, password, and additional fields.
        """
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email: str, password: str, **extra_fields: Dict[str, Any]) -> Any:
        """
        Create and save a user with the given email and password.
        """
        email = self.validate_email(email)
        try:
            return self.create_and_save_user(email, password, **extra_fields)
        except Exception as e:
            logger.error(f"An error occurred while creating a user: {e}")

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)
