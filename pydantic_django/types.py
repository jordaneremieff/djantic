from typing import Any, Dict, Optional, List
from decimal import Decimal
from datetime import date, time, datetime, timedelta
from uuid import UUID
from ipaddress import _BaseAddress, IPv4Address, IPv6Address

from pydantic import errors, IPvAnyAddress, Json
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


class GenericIPAddressField(_BaseAddress):

    protocol: Optional[str] = "both"

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type="string", format=cls.protocol)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v) -> str:
        if cls.protocol == "both":
            try:
                return str(IPvAnyAddress(v))
            except ValueError:
                raise errors.IPvAnyAddressError()

        if cls.protocol == "ipv4":
            try:
                return str(IPv4Address(v))
            except ValueError:
                raise errors.IPv4AddressError()

        if cls.protocol == "ipv6":
            try:
                return str(IPv6Address(v))
            except ValueError:
                raise errors.IPv6AddressError()


FIELD_TYPES = {
    "GenericIPAddressField": GenericIPAddressField,
    "TextField": str,
    "BooleanField": bool,
    "BinaryField": bytes,
    "DateField": date,
    "DateTimeField": datetime,
    "DurationField": timedelta,
    "TimeField": time,
    "DecimalField": Decimal,
    "FloatField": float,
    "UUIDField": UUID,
    "JSONField": Json,
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

# ForeignKey", "ManyToManyField", "OneToOneField"


def DjangoField(field):
    default = ...
    default_factory = None
    description = None
    title = None
    max_length = None
    # min_length = None
    if field.is_relation:
        internal_type = field.related_model._meta.pk.get_internal_type()
        if not field.concrete and field.auto_created:  # Reverse relation

            default = None
        elif field.null:
            default = None

        python_type = FIELD_TYPES.get(internal_type, int)

        if field.one_to_many or field.many_to_many:
            python_type = List[python_type]

        field = field.target_field

    else:
        internal_type = field.get_internal_type()
        if internal_type in STR_TYPES:
            python_type = str
            max_length = field.max_length

        elif internal_type in INT_TYPES:
            python_type = int
        else:
            python_type = FIELD_TYPES[internal_type]

        deconstructed = field.deconstruct()
        field_options = deconstructed[3] or {}
        blank = field_options.pop("blank", False)
        null = field_options.pop("null", False)
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
            description=description,
            max_length=max_length,
            # **extra,
        ),
    )
