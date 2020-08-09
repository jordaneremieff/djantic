from typing import List

import pytest

from testapp.models import User, Profile, Group, Message

from pydantic_django import PydanticDjangoModel


@pytest.mark.django_db
def test_m2m():
    """
    Test forward m2m relationships.
    """

    class PydanticUser(PydanticDjangoModel):
        class Config:
            model = User
            include = ["id", "groups"]

    assert PydanticUser.schema()["properties"]["groups"] == {
        "items": {"type": "integer"},
        "title": "Id",
        "type": "array",
    }

    class PydanticGroup(PydanticDjangoModel):
        class Config:
            model = Group
            include = ["id", "slug"]

    class PydanticUser(PydanticDjangoModel):

        groups: List[PydanticGroup]

        class Config:
            model = User
            include = ["id", "groups"]

    assert PydanticUser.schema() == {
        "definitions": {
            "PydanticGroup": {
                "description": "A group of users.",
                "properties": {
                    "id": {"title": "Id", "type": "integer"},
                    "slug": {"maxLength": 50, "title": "Slug", "type": "string"},
                },
                "required": ["slug"],
                "title": "PydanticGroup",
                "type": "object",
            }
        },
        "description": "A user of the application.",
        "properties": {
            "groups": {
                "items": {"$ref": "#/definitions/PydanticGroup"},
                "title": "Groups",
                "type": "array",
            },
            "id": {"title": "Id", "type": "integer"},
        },
        "required": ["groups"],
        "title": "PydanticUser",
        "type": "object",
    }


@pytest.mark.django_db
def test_foreign_key():
    """
    Test forward foreign-key relationships.
    """

    class PydanticUser(PydanticDjangoModel):
        """
        Related model for foreign-key relationship.
        """

        class Config:
            model = User
            include = ["id"]

    class PydanticMessage(PydanticDjangoModel):
        """
        Model with a forward foreign-key relationship.
        """

        class Config:
            model = Message
            include = ["id", "user"]

    assert PydanticMessage.schema() == {
        "description": "Model with a forward foreign-key relationship.",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "user": {"title": "Id", "type": "integer"},
        },
        "required": ["user"],
        "title": "PydanticMessage",
        "type": "object",
    }

    class PydanticMessage(PydanticDjangoModel):
        """
        Model with a forward foreign-key relationship and sub-model definition.
        """

        user: PydanticUser

        class Config:
            model = Message
            include = ["id", "user"]

    assert PydanticMessage.schema() == {
        "definitions": {
            "PydanticUser": {
                "description": "Related model for foreign-key relationship.",
                "properties": {"id": {"title": "Id", "type": "integer"}},
                "title": "PydanticUser",
                "type": "object",
            }
        },
        "description": "Model with a forward foreign-key relationship and sub-model definition.",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "user": {"$ref": "#/definitions/PydanticUser"},
        },
        "required": ["user"],
        "title": "PydanticMessage",
        "type": "object",
    }


@pytest.mark.django_db
def test_foreign_key_reverse():
    """
    Test reverse foreign-key relationships.
    """

    class PydanticMessage(PydanticDjangoModel):
        """
        Related model for foreign-key relationship.
        """

        class Config:
            model = Message
            include = ["id"]

    class PydanticUser(PydanticDjangoModel):
        """
        Model with a reverse foreign-key relationship.
        """

        class Config:
            model = User
            include = ["id", "messages"]

    assert PydanticUser.schema() == {
        "description": "Model with a reverse foreign-key relationship.",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "messages": {"items": {"type": "integer"}, "title": "Id", "type": "array"},
        },
        "title": "PydanticUser",
        "type": "object",
    }

    class PydanticUser(PydanticDjangoModel):
        """
        Model with a reverse foreign-key relationship and sub-model definition.
        """

        messages: List[PydanticMessage]

        class Config:
            model = User
            include = ["id", "messages"]

    assert PydanticUser.schema() == {
        "definitions": {
            "PydanticMessage": {
                "description": "Related model for foreign-key relationship.",
                "properties": {"id": {"title": "Id", "type": "integer"}},
                "title": "PydanticMessage",
                "type": "object",
            }
        },
        "description": "Model with a reverse foreign-key relationship and sub-model definition.",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "messages": {
                "items": {"$ref": "#/definitions/PydanticMessage"},
                "title": "Messages",
                "type": "array",
            },
        },
        "required": ["messages"],
        "title": "PydanticUser",
        "type": "object",
    }


@pytest.mark.django_db
def test_one_to_one():
    """
    Test forward one-to-one relationships.
    """

    class PydanticUser(PydanticDjangoModel):
        """
        Related model for one-to-one relationship.
        """

        class Config:
            model = User
            include = ["id", "first_name", "email"]

    class PydanticProfile(PydanticDjangoModel):
        """
        Model with a forward one-to-one relationship.
        """

        class Config:
            model = Profile
            include = ["id"]

    assert PydanticProfile.schema() == {
        "description": "Model with a forward one-to-one relationship.",
        "properties": {"id": {"title": "Id", "type": "integer"}},
        "title": "PydanticProfile",
        "type": "object",
    }

    class PydanticProfile(PydanticDjangoModel):
        """
        Model with a forward one-to-one relationship and sub-model definition.
        """

        user: PydanticUser

        class Config:
            model = Profile
            include = ["user"]

    assert PydanticProfile.schema() == {
        "definitions": {
            "PydanticUser": {
                "description": "Related model for one-to-one relationship.",
                "properties": {
                    "email": {"maxLength": 254, "title": "Email", "type": "string"},
                    "first_name": {
                        "maxLength": 50,
                        "title": "First Name",
                        "type": "string",
                    },
                    "id": {"title": "Id", "type": "integer"},
                },
                "required": ["first_name", "email"],
                "title": "PydanticUser",
                "type": "object",
            }
        },
        "description": "Model with a forward one-to-one relationship and sub-model definition.",
        "properties": {"user": {"$ref": "#/definitions/PydanticUser"}},
        "required": ["user"],
        "title": "PydanticProfile",
        "type": "object",
    }


@pytest.mark.django_db
def test_one_to_one_reverse():
    """
    Test reverse one-to-one relationships.
    """

    class PydanticProfile(PydanticDjangoModel):
        """
        Related model for one-to-one relationship.
        """

        class Config:
            model = Profile
            include = ["id"]

    class PydanticUser(PydanticDjangoModel):
        """
        Model with a reverse one-to-one relationship.
        """

        class Config:
            model = User
            include = ["id", "profile"]

    assert PydanticUser.schema() == {
        "description": "Model with a reverse one-to-one relationship.",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "profile": {"title": "Id", "type": "integer"},
        },
        "title": "PydanticUser",
        "type": "object",
    }

    class PydanticUser(PydanticDjangoModel):
        """
        Model with a reverse one-to-one relationship  and sub-model definition.
        """

        profile: PydanticProfile

        class Config:
            model = User
            include = ["id", "profile"]

    assert PydanticUser.schema() == {
        "definitions": {
            "PydanticProfile": {
                "description": "Related model for one-to-one relationship.",
                "properties": {"id": {"title": "Id", "type": "integer"}},
                "title": "PydanticProfile",
                "type": "object",
            }
        },
        "description": "Model with a reverse one-to-one relationship  and sub-model definition.",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "profile": {"$ref": "#/definitions/PydanticProfile"},
        },
        "required": ["profile"],
        "title": "PydanticUser",
        "type": "object",
    }
