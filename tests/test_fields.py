import pytest

from testapp.models import Record, Configuration, Preference, Searchable
from djantic import ModelSchema


@pytest.mark.django_db
def test_unhandled_field_type():
    class SearchableSchema(ModelSchema):
        class Config:
            model = Searchable

    assert SearchableSchema.schema() == {
        "title": "SearchableSchema",
        "description": "Searchable(id, title, search_vector)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "title": {
                "title": "Title",
                "description": "title",
                "maxLength": 255,
                "type": "string",
            },
            "search_vector": {
                "title": "Search Vector",
                "description": "search_vector",
                "type": "string",
            },
        },
        "required": ["title"],
    }

    searchable = Searchable.objects.create(title="My content")
    assert SearchableSchema.from_django(searchable).dict() == {
        "id": 1,
        "title": "My content",
        "search_vector": None,
    }


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
                "allOf": [{"$ref": "#/definitions/RecordSchemaRecordTypeEnum"}],
            },
            "record_status": {
                "title": "Record Status",
                "description": "record_status",
                "default": 0,
                "allOf": [{"$ref": "#/definitions/RecordSchemaRecordStatusEnum"}],
            },
        },
        "definitions": {
            "RecordSchemaRecordTypeEnum": {
                "title": "RecordSchemaRecordTypeEnum",
                "description": "An enumeration.",
                "enum": ["NEW", "OLD"],
            },
            "RecordSchemaRecordStatusEnum": {
                "title": "RecordSchemaRecordStatusEnum",
                "description": "An enumeration.",
                "enum": [0, 1, 2],
            },
        },
    }


@pytest.mark.django_db
def test_enum_choices():
    class PreferenceSchema(ModelSchema):
        class Config:
            model = Preference
            use_enum_values = True

    assert PreferenceSchema.schema() == {
        "title": "PreferenceSchema",
        "description": "Preference(id, name, preferred_food, preferred_group)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "name": {
                "title": "Name",
                "description": "name",
                "maxLength": 128,
                "type": "string",
            },
            "preferred_food": {
                "title": "Preferred Food",
                "description": "preferred_food",
                "default": "ba",
                "allOf": [{"$ref": "#/definitions/PreferenceSchemaPreferredFoodEnum"}],
            },
            "preferred_group": {
                "title": "Preferred Group",
                "description": "preferred_group",
                "default": 1,
                "allOf": [{"$ref": "#/definitions/PreferenceSchemaPreferredGroupEnum"}],
            },
        },
        "required": ["name"],
        "definitions": {
            "PreferenceSchemaPreferredFoodEnum": {
                "title": "PreferenceSchemaPreferredFoodEnum",
                "description": "An enumeration.",
                "enum": ["ba", "ap"],
            },
            "PreferenceSchemaPreferredGroupEnum": {
                "title": "PreferenceSchemaPreferredGroupEnum",
                "description": "An enumeration.",
                "enum": [1, 2],
            },
        },
    }

    preference = Preference.objects.create(name="Jordan")
    assert PreferenceSchema.from_django(preference).dict() == {
        "id": 1,
        "name": "Jordan",
        "preferred_food": "ba",
        "preferred_group": 1,
    }


@pytest.mark.django_db
def test_enum_choices_generates_unique_enums():
    class PreferenceSchema(ModelSchema):
        class Config:
            model = Preference
            use_enum_values = True

    class PreferenceSchema2(ModelSchema):
        class Config:
            model = Preference
            use_enum_values = True

    assert str(PreferenceSchema2.__fields__["preferred_food"].type_) != str(
        PreferenceSchema.__fields__["preferred_food"].type_
    )
