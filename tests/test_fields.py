import pytest

from testapp.models import Record, Configuration
from pydantic_django import PydanticDjangoModel


@pytest.mark.django_db
def test_custom_field():
    """
    Test a model using custom field subclasses.
    """

    class RecordSchema(PydanticDjangoModel):
        class Config:
            model = Record

    assert RecordSchema.schema() == {
        "title": "RecordSchema",
        "description": "A generic record model.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "title": {"title": "Title", "maxLength": 20, "type": "string"},
            "items": {
                "title": "Items",
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

    class ConfigurationSchema(PydanticDjangoModel):
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
                "anyOf": [
                    {"type": "string", "format": "json-string"},
                    {"type": "object"},
                    {"type": "array", "items": {}},
                ],
            },
            "changelog": {
                "title": "Changelog",
                "anyOf": [
                    {"type": "string", "format": "json-string"},
                    {"type": "object"},
                    {"type": "array", "items": {}},
                ],
            },
            "metadata": {
                "title": "Metadata",
                "anyOf": [
                    {"type": "string", "format": "json-string"},
                    {"type": "object"},
                    {"type": "array", "items": {}},
                ],
            },
        },
    }
