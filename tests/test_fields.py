import pytest

from testapp.models import Record, Configuration
from pydantic_django import ModelSchema


@pytest.mark.django_db
def test_custom_field():
    """
    Test a model using custom field subclasses.
    """

    class RecordSchema(ModelSchema):
        class Config:
            model = Record
            include = ["id", "title", "items"]

    assert RecordSchema.schema() == {
        "title": "RecordSchema",
        "description": "A generic record model.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "title": {
                "title": "Title",
                "description": "title",
                "maxLength": 20,
                "type": "string",
            },
            "items": {
                "title": "Items",
                "description": "items",
                "anyOf": [
                    {"type": "string", "format": "json-string"},
                    {"type": "object"},
                    {"type": "array", "items": {}},
                ],
            },
        },
        "required": ["title"],
    }


@pytest.mark.django_db
def test_postgres_json_field():
    """
    Test generating a schema for multiple Postgres JSON fields.
    """

    class ConfigurationSchema(ModelSchema):
        class Config:
            model = Configuration
            include = ["permissions", "changelog", "metadata"]

    assert ConfigurationSchema.schema() == {
        "title": "ConfigurationSchema",
        "description": "A configuration container.",
        "type": "object",
        "properties": {
            "permissions": {
                "title": "Permissions",
                "description": "permissions",
                "anyOf": [
                    {"type": "string", "format": "json-string"},
                    {"type": "object"},
                    {"type": "array", "items": {}},
                ],
            },
            "changelog": {
                "title": "Changelog",
                "description": "changelog",
                "anyOf": [
                    {"type": "string", "format": "json-string"},
                    {"type": "object"},
                    {"type": "array", "items": {}},
                ],
            },
            "metadata": {
                "title": "Metadata",
                "description": "metadata",
                "anyOf": [
                    {"type": "string", "format": "json-string"},
                    {"type": "object"},
                    {"type": "array", "items": {}},
                ],
            },
        },
    }


@pytest.mark.django_db
def test_lazy_choice_field():
    """
    Test generating a dynamic enum choice field.
    """

    class RecordSchema(ModelSchema):
        class Config:
            model = Record
            include = ["record_type", "record_status"]

    assert RecordSchema.schema() == {
        "title": "RecordSchema",
        "description": "A generic record model.",
        "type": "object",
        "properties": {
            "record_type": {
                "title": "Record Type",
                "description": "record_type",
                "default": "NEW",
                "allOf": [{"$ref": "#/definitions/RecordTypeEnum"}],
            },
            "record_status": {
                "title": "Record Status",
                "description": "record_status",
                "default": 0,
                "allOf": [{"$ref": "#/definitions/RecordStatusEnum"}],
            },
        },
        "definitions": {
            "RecordTypeEnum": {
                "title": "RecordTypeEnum",
                "description": "An enumeration.",
                "enum": ["NEW", "OLD"],
            },
            "RecordStatusEnum": {
                "title": "RecordStatusEnum",
                "description": "An enumeration.",
                "enum": [0, 1, 2],
            },
        },
    }
