import datetime
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from testapp.models import User, Profile, Configuration

from pydantic import ConfigDict, AliasGenerator
from djantic import ModelSchema


@pytest.mark.django_db
def test_description():
    """
    Test setting the schema description to the docstring of the Pydantic model.
    """

    class ProfileSchema(ModelSchema):
        """
        Pydantic profile docstring.
        """

        model_config = ConfigDict(model=Profile)

    assert (
        ProfileSchema.model_json_schema()["description"]
        == "Pydantic profile docstring."
    )

    class UserSchema(ModelSchema):
        """
        Pydantic user docstring.
        """

        model_config = ConfigDict(model=User)

    assert UserSchema.model_json_schema()["description"] == "Pydantic user docstring."

    # Default will be the model docstring
    class UserSchema(ModelSchema):
        model_config = ConfigDict(model=User)

    assert UserSchema.model_json_schema()["description"] == "A user of the application."


@pytest.mark.django_db
def test_cache():
    """
    Test model_json_schema
    """

    class UserSchema(ModelSchema):
        model_config = ConfigDict(model=User, include=["id", "first_name"])

    expected = {
        "description": "A user of the application.",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "first_name": {
                "description": "first_name",
                "maxLength": 50,
                "title": "First Name",
                "type": "string",
            },
        },
        "required": ["first_name"],
        "title": "UserSchema",
        "type": "object",
    }

    assert UserSchema.model_json_schema() == expected


@pytest.mark.django_db
def test_include_exclude():
    """
    Test include and exclude rules in the model config.
    """

    all_user_fields = [field.name for field in User._meta.get_fields()]

    class UserSchema(ModelSchema):
        """
        All fields are included by default.
        """

        model_config = ConfigDict(model=User)

    assert set(UserSchema.model_json_schema()["properties"].keys()) == set(
        all_user_fields
    )

    class UserSchema(ModelSchema):
        """
        All fields are included explicitly.
        """

        model_config = ConfigDict(model=User)

    assert set(UserSchema.model_json_schema()["properties"].keys()) == set(
        all_user_fields
    )

    class UserSchema(ModelSchema):
        """
        Only 'first_name' and 'email' are included.
        """

        last_name: str  # Fields annotations follow the same config rules
        model_config = ConfigDict(model=User, include=["first_name", "email"])

    included = UserSchema.model_json_schema()["properties"].keys()
    assert set(included) == set(UserSchema.model_config["include"])
    assert set(included) == set(["first_name", "email"])

    class UserSchema(ModelSchema):
        """
        Only 'id' and 'profile' are not excluded.
        """

        first_name: str
        last_name: str
        model_config = ConfigDict(
            model=User,
            exclude=["first_name", "last_name", "email", "created_at", "updated_at"],
        )

    not_excluded = UserSchema.model_json_schema()["properties"].keys()
    assert set(not_excluded) == set(
        [
            field
            for field in all_user_fields
            if field not in UserSchema.model_config["exclude"]
        ]
    )
    assert set(not_excluded) == set(["profile", "id"])


@pytest.mark.django_db
def test_annotations():
    """
    Test annotating fields.
    """

    class UserSchema(ModelSchema):
        """
        Test required, optional, and function fields.

        'first_name' is required in Django model, but optional in schema
        'last_name' is optional in Django model, but required in schema
        """

        first_name: Optional[str]
        last_name: str
        model_config = ConfigDict(model=User, include=["first_name", "last_name"])

    assert UserSchema.model_json_schema()["required"] == ["last_name"]

    updated_at_dt = datetime.datetime(2020, 12, 31, 0, 0)

    class UserSchema(ModelSchema):
        """
        Test field functions and factory defaults.
        """

        first_name: str = Field(default="Hello")
        last_name: str = Field(..., min_length=1, max_length=50)
        email: str = Field(default_factory=lambda: "jordan@eremieff.com")
        created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
        updated_at: datetime.datetime = updated_at_dt
        model_config = ConfigDict(model=User)

    schema = UserSchema.model_json_schema()

    props = schema["properties"]
    assert "default" in props["created_at"]
    assert props["email"]["default"] == "jordan@eremieff.com"
    assert props["first_name"]["default"] == "Hello"
    assert props["updated_at"]["default"] == updated_at_dt.strftime("%Y-%m-%dT00:00:00")
    assert set(schema["required"]) == set(["last_name"])


@pytest.mark.skip(reason="Dumping by alias for model json schema seems to not work")
def test_by_alias_generator():
    class UserSchema(ModelSchema):
        """
        Test alias generator.
        """

        model_config = ConfigDict(
            model=User,
            include=["first_name", "last_name"],
            alias_generator=AliasGenerator(serialization_alias=(lambda x: x.upper())),
        )

    assert UserSchema.model_json_schema(by_alias=True) == {
        "title": "UserSchema",
        "description": "Test alias generator.",
        "type": "object",
        "properties": {
            "FIRST_NAME": {
                "title": "First Name",
                "description": "first_name",
                "maxLength": 50,
                "type": "string",
            },
            "LAST_NAME": {
                "title": "Last Name",
                "description": "last_name",
                "maxLength": 50,
                "type": "string",
            },
        },
        "required": ["FIRST_NAME"],
    }
    assert set(UserSchema.model_json_schema()["properties"].keys()) == set(
        ["FIRST_NAME", "LAST_NAME"]
    )
    assert set(UserSchema.schema(by_alias=False)["properties"].keys()) == set(
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

    class ProfileSchema(ModelSchema):
        """
        Django model relation as a sub-model.
        """

        model_config = ConfigDict(model=Profile, include=["id"])

    class UserSchema(ModelSchema):
        sign_up: SignUp
        profile: ProfileSchema
        model_config = ConfigDict(model=User, include=["id", "sign_up", "profile"])

    assert set(UserSchema.model_json_schema()["$defs"].keys()) == set(
        ["ProfileSchema", "SignUp"]
    )

    class Notification(BaseModel):
        """
        Pydantic model as the main model.
        """

        user: UserSchema
        content: str
        sent_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    assert set(Notification.model_json_schema()["properties"].keys()) == set(
        ["user", "content", "sent_at"]
    )
    assert set(Notification.model_json_schema()["$defs"].keys()) == set(
        ["ProfileSchema", "SignUp", "UserSchema"]
    )


@pytest.mark.django_db
def test_include_from_annotations():
    """
    Test include="__annotations__" config.
    """

    class ProfileSchema(ModelSchema):
        website: str
        model_config = ConfigDict(model=Profile, include="__annotations__")

    assert ProfileSchema.model_json_schema() == {
        "title": "ProfileSchema",
        "description": "A user's profile.",
        "type": "object",
        "properties": {"website": {"title": "Website", "type": "string"}},
        "required": ["website"],
    }
