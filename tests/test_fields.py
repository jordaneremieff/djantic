import pytest

from testapp.models import Record, Configuration
from pydantic_django import PydanticDjangoModel


@pytest.mark.django_db
def test_custom_field():
    """
    Test a model using custom field subclasses.
    """

    class PydanticRecord(PydanticDjangoModel):
        class Config:
            model = Record

    assert PydanticRecord.schema() == {
        "title": "PydanticRecord",
        "description": "A generic record model.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "title": {"title": "Title", "maxLength": 20, "type": "string"},
            "items": {"title": "Items", "type": "string", "format": "json-string"},
        },
        "required": ["title"],
    }


@pytest.mark.django_db
def test_postgres_json_field():
    """
    Test generating a schema for multiple Postgres JSON fields.
    """

    class PydanticConfiguration(PydanticDjangoModel):
        class Config:
            model = Configuration
            include = ["permissions", "changelog", "metadata"]

    assert PydanticConfiguration.schema() == {
        "description": "A configuration container.",
        "properties": {
            "changelog": {
                "format": "json-string",
                "title": "Changelog",
                "type": "string",
            },
            "metadata": {
                "format": "json-string",
                "title": "Metadata",
                "type": "string",
            },
            "permissions": {
                "format": "json-string",
                "title": "Permissions",
                "type": "string",
            },
        },
        "title": "PydanticConfiguration",
        "type": "object",
    }
