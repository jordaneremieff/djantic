import uuid

from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import JSONField


class Group(models.Model):
    """
    A group of users.
    """

    description = models.TextField()
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, self.created_at)
        super().save(*args, **kwargs)


class User(models.Model):
    """
    A user of the application.
    """

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(Group)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Profile(models.Model):
    """
    A user's profile.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    website = models.URLField(default="", blank=True)
    location = models.CharField(max_length=100, default="", blank=True)


class Message(models.Model):
    """
    A message created by a user.
    """

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages")
    content = models.TextField()
    is_flagged = models.BooleanField(
        default=False, help_text="Review status of the message"
    )
    flagged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the message was flagged for review (if applicable)",
    )


class Configuration(models.Model):
    """
    A configuration container.
    """

    name = models.CharField(max_length=100)
    permissions = JSONField(default=dict, blank=True)
    changelog = JSONField(default=list, blank=True)
    metadata = JSONField(blank=True)


class RequestLog(models.Model):
    """
    A log entry for a server request.
    """

    request_id = models.UUIDField(
        default=uuid.uuid4, help_text="Unique id of the request."
    )
    response_time = models.DurationField()
    ip_address = models.GenericIPAddressField(blank=True)
    host_ipv4_address = models.GenericIPAddressField(protocol="ipv4", blank=True)
    host_ipv6_address = models.GenericIPAddressField(protocol="ipv6", blank=True)
    metadata = JSONField(blank=True)
