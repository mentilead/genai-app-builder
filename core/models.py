import uuid

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        organization = Organization.objects.create(name=f"{instance.get_full_name()}'s Organization")
        UserProfile.objects.create(user=instance,
                                   organization=organization,
                                   role='OWNER')


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

