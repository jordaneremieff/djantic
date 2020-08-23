import pytest

from testapp.models import User

from pydantic import ConfigError
from pydantic_django import PydanticDjangoModel


@pytest.mark.django_db
def test_config_errors():
    """
    Test the model config error exceptions.
    """

    with pytest.raises(
        ConfigError, match="(Is `Config.model` a valid Django model class?)"
    ):

        class InvalidModelErrorSchema(PydanticDjangoModel):
            class Config:
                model = "Ok"

    with pytest.raises(
        ConfigError,
        match="Only one of 'include' or 'exclude' should be set in configuration.",
    ):

        class IncludeExcludeErrorSchema(PydanticDjangoModel):
            class Config:
                model = User
                include = ["id"]
                exclude = ["first_name"]
