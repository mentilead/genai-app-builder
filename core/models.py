import uuid

from django.db import models
from django.contrib.auth.models import User


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


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    teams = models.ManyToManyField(Team)
    USER_TYPE_CHOICES = (
        ('OWNER', 'Owner'),
        ('READER', 'Reader'),
    )

    role = models.CharField(max_length=6, choices=USER_TYPE_CHOICES)


class LLMAPIKey(models.Model):
    PROVIDER_CHOICES = [
        ('open_ai', 'OpenAI'),
        ('aws_bedrock', 'AWS Bedrock'),
        # add more providers here
    ]

    api_key_name = models.CharField(max_length=255, null=False, blank=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    provider_name = models.CharField(max_length=255, choices=PROVIDER_CHOICES)
    api_key = models.CharField(max_length=255, null=False, blank=False)
    secret_key = models.CharField(max_length=255, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.provider_name