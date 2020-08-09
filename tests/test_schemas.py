import datetime
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from testapp.models import User, Profile

from pydantic_django import PydanticDjangoModel


@pytest.mark.django_db
def test_description():
    """
    Test setting the schema description to the docstring of the Pydantic model.
    """

    class PydanticProfile(PydanticDjangoModel):
        """
        Pydantic profile docstring.
        """

        class Config:
            model = Profile

    assert PydanticProfile.schema()["description"] == "Pydantic profile docstring."

    class PydanticUser(PydanticDjangoModel):
        """
        Pydantic user docstring.
        """

        class Config:
            model = User

    assert PydanticUser.schema()["description"] == "Pydantic user docstring."

    # Default will be the model docstring
    class PydanticUser(PydanticDjangoModel):
        class Config:
            model = User

    assert PydanticUser.schema()["description"] == "A user of the application."


@pytest.mark.django_db
def test_cache():
    """
    Test the schema cache.
    """

    class PydanticUser(PydanticDjangoModel):
        class Config:
            model = User
            include = ["id", "first_name"]

    expected = {
        "title": "PydanticUser",
        "description": "A user of the application.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "first_name": {"title": "First Name", "maxLength": 50, "type": "string"},
        },
        "required": ["first_name"],
    }

    assert True not in PydanticUser.__schema_cache__
    assert False not in PydanticUser.__schema_cache__
    assert PydanticUser.schema() == expected
    assert True in PydanticUser.__schema_cache__
    assert False not in PydanticUser.__schema_cache__
    assert PydanticUser.schema() == expected


@pytest.mark.django_db
def test_fields():
    """
    Test include and exclude rules in the model config.
    """

    all_user_fields = [field.name for field in User._meta.get_fields()]

    class PydanticUser(PydanticDjangoModel):
        """
        All fields are included by default.
        """

        class Config:
            model = User

    assert set(PydanticUser.schema()["properties"].keys()) == set(all_user_fields)

    class PydanticUser(PydanticDjangoModel):
        """
        All fields are included explicitly.
        """

        class Config:
            model = User

    assert set(PydanticUser.schema()["properties"].keys()) == set(all_user_fields)

    class PydanticUser(PydanticDjangoModel):
        """
        Only 'first_name' and 'email' are included.
        """

        last_name: str  # Fields annotations follow the same config rules

        class Config:
            model = User
            include = ["first_name", "email"]

    included = PydanticUser.schema()["properties"].keys()
    assert set(included) == set(PydanticUser.__config__.include)
    assert set(included) == set(["first_name", "email"])

    class PydanticUser(PydanticDjangoModel):
        """
        Only 'id' and 'profile' are not excluded.
        """

        first_name: str
        last_name: str

        class Config:
            model = User
            exclude = [
                "first_name",
                "last_name",
                "email",
                "created_at",
                "updated_at",
                "groups",
            ]

    not_excluded = PydanticUser.schema()["properties"].keys()
    assert set(not_excluded) == set(
        [
            field
            for field in all_user_fields
            if field not in PydanticUser.__config__.exclude
        ]
    )
    assert set(not_excluded) == set(["profile", "messages", "id"])


@pytest.mark.django_db
def test_annotations():
    """
    Test annotating fields.
    """

    class PydanticUser(PydanticDjangoModel):
        """
        Test required, optional, and function fields.

        'first_name' is required in Django model, but optional in schema
        'last_name' is optional in Django model, but required in schema
        """

        first_name: Optional[str]
        last_name: str

        class Config:
            model = User
            include = ["first_name", "last_name"]

    assert PydanticUser.schema()["required"] == ["last_name"]

    updated_at_dt = datetime.datetime(2020, 12, 31, 0, 0)

    class PydanticUser(PydanticDjangoModel):
        """
        Test field functions and factory defaults.
        """

        first_name: str = Field(default="Hello")
        last_name: str = Field(..., min_length=1, max_length=50)
        email: str = Field(default_factory=lambda: "jordan@eremieff.com")
        created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
        updated_at: datetime.datetime = updated_at_dt

        class Config:
            model = User

    schema = PydanticUser.schema()

    props = schema["properties"]
    assert "default" in props["created_at"]
    assert props["email"]["default"] == "jordan@eremieff.com"
    assert props["first_name"]["default"] == "Hello"
    assert props["updated_at"]["default"] == updated_at_dt.strftime("%Y-%m-%dT00:00:00")
    assert set(schema["required"]) == set(["groups", "last_name"])


@pytest.mark.django_db
def test_json():
    class PydanticUser(PydanticDjangoModel):
        """
        Test JSON schema.
        """

        class Config:
            model = User
            include = ["id", "first_name", "last_name"]

    expected = """{
  "title": "PydanticUser",
  "description": "Test JSON schema.",
  "type": "object",
  "properties": {
    "id": {
      "title": "Id",
      "type": "integer"
    },
    "first_name": {
      "title": "First Name",
      "maxLength": 50,
      "type": "string"
    },
    "last_name": {
      "title": "Last Name",
      "maxLength": 50,
      "type": "string"
    }
  },
  "required": [
    "first_name"
  ]
}"""
    assert expected == PydanticUser.schema_json(indent=2)


def test_by_alias_generator():
    class PydanticUser(PydanticDjangoModel):
        """
        Test alias generator.
        """

        class Config:
            model = User
            include = ["first_name", "last_name"]

            @staticmethod
            def alias_generator(x):
                return x.upper()

    assert PydanticUser.schema() == {
        "title": "PydanticUser",
        "description": "Test alias generator.",
        "type": "object",
        "properties": {
            "FIRST_NAME": {"title": "First Name", "maxLength": 50, "type": "string"},
            "LAST_NAME": {"title": "Last Name", "maxLength": 50, "type": "string"},
        },
        "required": ["FIRST_NAME"],
    }
    assert set(PydanticUser.schema()["properties"].keys()) == set(
        ["FIRST_NAME", "LAST_NAME"]
    )
    assert set(PydanticUser.schema(by_alias=False)["properties"].keys()) == set(
        ["first_name", "last_name"]
    )


def test_sub_model():
    """
    Test compatability with normal Pydantic models.
    """

    class SignUp(BaseModel):
        """
        Pydantic model as the sub-model.
        """

        referral_code: Optional[str]

    class PydanticProfile(PydanticDjangoModel):
        """
        Django model relation as a sub-model.
        """

        class Config:
            model = Profile
            include = ["id"]

    class PydanticUser(PydanticDjangoModel):
        sign_up: SignUp
        profile: PydanticProfile

        class Config:
            model = User
            include = ["id", "sign_up", "profile"]

    assert set(PydanticUser.schema()["definitions"].keys()) == set(
        ["PydanticProfile", "SignUp"]
    )

    class Notification(BaseModel):
        """
        Pydantic model as the main model.
        """

        user: PydanticUser
        content: str
        sent_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    assert set(Notification.schema()["properties"].keys()) == set(
        ["user", "content", "sent_at"]
    )
    assert set(Notification.schema()["definitions"].keys()) == set(
        ["PydanticProfile", "SignUp", "PydanticUser"]
    )
