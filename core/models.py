import logging
import uuid
from typing import List

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

logger = logging.getLogger(__name__)


class Organization(models.Model):
    name = models.CharField(max_length=50)
    api_id = models.CharField(editable=False, max_length=40)

    def save(self, *args, **kwargs):
        if not self.api_id:
            self.api_id = f"org-{uuid.uuid4().hex}"
        super().save(*args, **kwargs)


class Team(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


# https://testdriven.io/blog/django-custom-user-model/
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: List[str] = []

    objects = CustomUserManager()

    groups = models.ManyToManyField(
        verbose_name='groups',
        to='auth.Group',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        verbose_name='user permissions',
        to='auth.Permission',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )

    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    teams = models.ManyToManyField(Team)
    USER_TYPE_CHOICES = (
        ('OWNER', 'Owner'),
        ('READER', 'Reader'),
    )

    role = models.CharField(max_length=6, choices=USER_TYPE_CHOICES)
    lite_llm_api_key = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.email
