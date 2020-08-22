from django.contrib.postgres.fields import JSONField
from django.db import models


class CustomFieldMixin:
    pass


class RestrictedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 20
        super().__init__(*args, **kwargs)


class NotNullRestrictedCharField(RestrictedCharField):
    def __init__(self, *args, **kwargs):
        kwargs["null"] = False
        kwargs["blank"] = False
        super().__init__(*args, **kwargs)


class ListField(CustomFieldMixin, JSONField):
    def __init__(self, *args, **kwargs):
        kwargs["default"] = list
        super().__init__(*args, **kwargs)
