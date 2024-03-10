import pytest
from pydantic.errors import PydanticUserError
from testapp.models import User

from pydantic import ConfigDict
from djantic import ModelSchema


@pytest.mark.django_db
def test_config_errors():
    """
    Test the model config error exceptions.
    """

    with pytest.raises(PydanticUserError, match="(Is `Config` class defined?)"):

        class InvalidModelErrorSchema(ModelSchema):
            pass

    with pytest.raises(
        PydanticUserError, match="(Is `Config.model` a valid Django model class?)"
    ):

        class InvalidModelErrorSchema2(ModelSchema):
            model_config = ConfigDict(model="Ok")

    with pytest.raises(
        PydanticUserError,
        match="Only one of 'include' or 'exclude' should be set in configuration.",
    ):

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
        model_config = ConfigDict(model=User, include=["id"])

    assert UserSchema.get_field_names() == [
        "profile",
        "first_name",
        "last_name",
        "email",
        "created_at",
        "updated_at",
    ]
