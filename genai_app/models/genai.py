from django.db import models

from core.models import Organization


class OpenAIManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(provider=OrgProvider.Provider.OPENAI)


class AWSBedrockManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(provider=OrgProvider.Provider.AWS_BEDROCK)


class OrgProvider(models.Model):
    class Provider(models.TextChoices):
        OPENAI = 'OPENAI', 'OpenAI',
        AWS_BEDROCK = 'AWS_BEDROCK', 'AWS Bedrock'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=Provider.choices)
    name = models.CharField(max_length=255, null=False, blank=False)
    create_date = models.DateTimeField(auto_now_add=True)

    """ OpenAI = OpenAI API Key, AWS Bedrock = customer IAM role ARN """
    val1 = models.CharField(max_length=255, null=True, blank=True)
    """ AWS Bedrock = external ID """
    val2 = models.CharField(max_length=255, null=True, blank=True)
    """ AWS Bedrock = AWS region where Bedrock service is used """
    val3 = models.CharField(max_length=255, null=True, blank=True)

    objects = models.Manager()  # Default manager
    openai = OpenAIManager()
    aws_bedrock = AWSBedrockManager()

    class Meta:
        ordering=['organization', 'provider', 'name']
        indexes = [
            models.Index(fields=['organization', 'provider', 'name'])
        ]

    def __str__(self):
        return f"{self.organization}-{self.provider}-{self.name}"
