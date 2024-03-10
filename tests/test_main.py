import pytest
from pydantic.errors import PydanticUserError
from testapp.models import User

from pydantic import ConfigDict
from djantic import ModelSchema


@pytest.mark.django_db
def test_model_config_contains_valid_model():
    error_msg = r"(Is `model_config\[\"model\"\]` a valid Django model class?)"
    with pytest.raises(PydanticUserError, match=error_msg):

        class InvalidModelErrorSchema2(ModelSchema):
            model_config = ConfigDict(model="Ok")


@pytest.mark.django_db
def test_include_and_exclude_mutually_exclusive():
    error_msg = "Only one of 'include' or 'exclude' should be set in configuration."
    with pytest.raises(PydanticUserError, match=error_msg):

        class IncludeExcludeErrorSchema(ModelSchema):
            model_config = ConfigDict(
                model=User, include=["id"], exclude=["first_name"]
            )


@pytest.mark.django_db
def test_get_field_names():
    """
    Test retrieving the field names for a model.
    """

    class UserSchema(ModelSchema):
        model_config = ConfigDict(model=User, include=["id"])

    assert UserSchema.get_field_names() == ["id"]

    class UserSchema(ModelSchema):
        model_config = ConfigDict(model=User, exclude=["id"])

    assert UserSchema.get_field_names() == [
        "profile",
        "first_name",
        "last_name",
        "email",
        "created_at",
        "updated_at",
    ]
