import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db.utils import IntegrityError


from core.models import Organization, CustomUser
from .tasks import sync_lite_llm_user

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Add error handling
        try:
            organization = Organization.objects.create(name=f"{instance.get_full_name()}'s Organization")
            instance.organization = organization
            instance.save()
            logger.info(f"Creating organization for user {instance.id}")

        except IntegrityError:
            # There was an error, possibly due to a conflict with existing data in DB
            logger.error(f"Error creating organization for user {instance.id}")
            return
        except ValueError as e:
            logger.error(f"An value error occurred when creating organization for user {instance.id}")
            return

        # Save as a separate operation, after user_profile has been successfully created
        try:
            sync_lite_llm_user.delay(instance.id)
        except Exception as e:
            logger.error(f"Failed to create sync_lite_llm_user task for user {instance.id}, error: {e}")
