import uuid
from datetime import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext_lazy as _
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

    config_id = models.UUIDField(
        default=uuid.uuid4, help_text=_("Unique id of the configuration.")
    )
    name = models.CharField(max_length=100)
    permissions = JSONField(default=dict, blank=True)
    changelog = JSONField(default=list, blank=True)
    metadata = JSONField(blank=True)
    version = models.CharField(default="0.0.1", max_length=5)


class RequestLog(models.Model):
    """
    A log entry for a server request.
    """

    request_id = models.UUIDField(
        default=uuid.uuid4, help_text=_("Unique id of the request.")
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

    NEW = "NEW"
    OLD = "OLD"

    PENDING = 0
    CANCELLED = 1
    CONFIRMED = 2

    RECORD_TYPE_CHOICES = ((NEW, "New"), (OLD, "Old"))
    RECORD_STATUS_CHOICES = (
        (PENDING, "Pending"),
        (CANCELLED, "Cancelled"),
        (CONFIRMED, "Confirmed"),
    )

    title = NotNullRestrictedCharField()
    items = ListField()
    record_type = models.CharField(
        default=NEW, max_length=5, choices=RECORD_TYPE_CHOICES
    )
    record_status = models.PositiveSmallIntegerField(
        default=PENDING, choices=RECORD_STATUS_CHOICES
    )


class ItemList(models.Model):
    name = models.CharField(max_length=100)


class Item(models.Model):
    name = models.CharField(max_length=100)
    item_list = models.ForeignKey(
        ItemList, on_delete=models.CASCADE, related_name="items"
    )


class Tagged(models.Model):
    slug = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return self.slug


class Bookmark(models.Model):
    url = models.URLField()
    tags = GenericRelation(Tagged)
