import pytest
from pydantic import ConfigError
from testapp.models import User

from djantic import ModelSchema


@pytest.mark.django_db
def test_config_errors():
    """
    Test the model config error exceptions.
    """

    with pytest.raises(
        ConfigError, match="(Is `Config` class defined?)"
    ):

        class InvalidModelErrorSchema(ModelSchema):
            pass

    with pytest.raises(
        ConfigError, match="(Is `Config.model` a valid Django model class?)"
    ):

        class InvalidModelErrorSchema(ModelSchema):
            class Config:
                model = "Ok"

    with pytest.raises(
        ConfigError,
        match="Only one of 'include' or 'exclude' should be set in configuration.",
    ):

        class IncludeExcludeErrorSchema(ModelSchema):
            class Config:
                model = User
                include = ["id"]
                exclude = ["first_name"]


@pytest.mark.django_db
def test_get_field_names():
    """
    Test retrieving the field names for a model.
    """

    class UserSchema(ModelSchema):
        class Config:
            model = User
            include = ["id"]

    assert UserSchema.get_field_names() == ["id"]

    class UserSchema(ModelSchema):
        class Config:
            model = User
            exclude = ["id"]

    assert UserSchema.get_field_names() == [
        "profile",
        "first_name",
        "last_name",
        "email",
        "created_at",
        "updated_at",
    ]
