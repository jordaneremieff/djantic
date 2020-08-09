import pytest

from testapp.models import Configuration

from pydantic_django import PydanticDjangoModel


@pytest.mark.django_db
def test_json_field():
    """
    Test generating a schema for multiple JSONField types.
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
