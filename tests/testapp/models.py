import uuid

from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import JSONField

from .fields import ListField, NotNullRestrictedCharField


class Thread(models.Model):
    """
    A thread of messages.
    """

    title = models.CharField(max_length=30)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Message(models.Model):
    """
    A message posted in a thread.
    """

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="messages"
    )

    def __str__(self):
        return f"Message created in {self.thread} @ {self.created_at.isoformat()}"


class Publication(models.Model):
    """
    A news publication.
    """

    title = models.CharField(max_length=30)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Article(models.Model):
    """
    A news article.
    """

    headline = models.CharField(max_length=100)
    pub_date = models.DateField()
    publications = models.ManyToManyField(Publication)

    class Meta:
        ordering = ["headline"]

    def __str__(self):
        return self.headline


class Group(models.Model):
    """
    A group of users.
    """

    title = models.TextField()
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
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Profile(models.Model):
    """
    A user's profile.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    website = models.URLField(default="", blank=True)
    location = models.CharField(max_length=100, default="", blank=True)


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


class Record(models.Model):
    """
    A generic record model.
    """

    title = NotNullRestrictedCharField()
    items = ListField()
