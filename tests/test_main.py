import pytest

from testapp.models import User

from pydantic_django import PydanticDjangoModel
from pydantic_django.main import PydanticDjangoError


@pytest.mark.django_db
def test_config_errors():
    """
    Test the model config error exceptions.
    """

    with pytest.raises(
        PydanticDjangoError, match="(Is `Config.model` a valid Django model class?)"
    ):

        class PydanticBadModel(PydanticDjangoModel):
            class Config:
                model = "Ok"

    with pytest.raises(
        PydanticDjangoError,
        match="Only one of 'include' or 'exclude' should be set in configuration.",
    ):

        class PydanticIncludeExclude(PydanticDjangoModel):
            class Config:
                model = User
                include = ["id"]
                exclude = ["first_name"]
