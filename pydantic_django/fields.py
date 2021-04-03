from typing import Any, Dict, List, Union
from decimal import Decimal
from datetime import date, time, datetime, timedelta
from enum import Enum
from uuid import UUID

from pydantic import IPvAnyAddress, Json
from pydantic.fields import FieldInfo


INT_TYPES = [
    "AutoField",
    "IntegerField",
    "SmallIntegerField",
    "BigIntegerField",
    "PositiveIntegerField",
    "PositiveSmallIntegerField",
]

STR_TYPES = [
    "CharField",
    "EmailField",
    "URLField",
    "SlugField",
    "TextField",
    "FilePathField",
]


FIELD_TYPES = {
    "GenericIPAddressField": IPvAnyAddress,
    "BooleanField": bool,
    "BinaryField": bytes,
    "DateField": date,
    "DateTimeField": datetime,
    "DurationField": timedelta,
    "TimeField": time,
    "DecimalField": Decimal,
    "FloatField": float,
    "UUIDField": UUID,
    "JSONField": Union[Json, dict, list],  # TODO: Configure this using default
    # "ArrayField",
    # "BigIntegerRangeField",
    # "CICharField",
    # "CIEmailField",
    # "CIText",
    # "CITextField",
    # "DateRangeField",
    # "DateTimeRangeField",
    # "DecimalRangeField",
    # "FloatRangeField",
    # "HStoreField",
    # "IntegerRangeField",
    # "RangeBoundary",
    # "RangeField",
    # "RangeOperators",
}


def ModelSchemaField(field: Any) -> tuple:
    default = ...
    default_factory = None
    description = None
    title = None
    max_length = None
    python_type = None

    if field.is_relation:
        if not field.related_model:
            internal_type = field.model._meta.pk.get_internal_type()
        else:
            internal_type = field.related_model._meta.pk.get_internal_type()
            if not field.concrete and field.auto_created or field.null:
                default = None

        pk_type = FIELD_TYPES.get(internal_type, int)
        if field.one_to_many or field.many_to_many:
            python_type = List[Dict[str, pk_type]]
        else:
            python_type = pk_type

        if field.related_model:
            field = field.target_field

    else:
        internal_type = field.get_internal_type()
        if internal_type in STR_TYPES:
            python_type = str
            if not field.choices:
                max_length = field.max_length

        elif internal_type in INT_TYPES:
            python_type = int
        elif internal_type in FIELD_TYPES:
            python_type = FIELD_TYPES[internal_type]

        # FIXME: Confirm if this is still needed.
        else:  # pragma: nocover
            for field_class in type(field).__mro__:
                get_internal_type = getattr(field_class, "get_internal_type", None)
                if get_internal_type:
                    _internal_type = get_internal_type(field_class())
                    if _internal_type in FIELD_TYPES:
                        python_type = FIELD_TYPES[_internal_type]
                        break

        deconstructed = field.deconstruct()
        field_options = deconstructed[3] or {}
        blank = field_options.pop("blank", False)
        null = field_options.pop("null", False)

        if field.choices:
            enum_choices = {v: k for k, v in field.choices}
            python_type = Enum(
                f"{field.name.title().replace('_', '')}Enum",
                enum_choices,
                module=__name__,
            )

        if field.has_default():
            if callable(field.default):
                default_factory = field.default
            else:
                default = field.default
        elif field.primary_key or blank or null:
            default = None

        description = field.help_text
        title = field.verbose_name.title()

    return (
        python_type,
        FieldInfo(
            default,
            default_factory=default_factory,
            title=title,
            description=str(description) or field.name,
            max_length=max_length,
        ),
    )
