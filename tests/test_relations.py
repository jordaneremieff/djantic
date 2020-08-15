from typing import List

import pytest

from testapp.models import User, Profile, Thread, Message, Publication, Article

from pydantic_django import PydanticDjangoModel


@pytest.mark.django_db
def test_m2m():
    """
    Test forward m2m relationships.
    """

    class ArticleSchema(PydanticDjangoModel):
        class Config:
            model = Article

    assert ArticleSchema.schema() == {
        "title": "ArticleSchema",
        "description": "A news article.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "headline": {"title": "Headline", "maxLength": 100, "type": "string"},
            "pub_date": {"title": "Pub Date", "type": "string", "format": "date"},
            "publications": {
                "title": "Publications",
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                },
            },
        },
        "required": ["headline", "pub_date", "publications"],
    }

    class PublicationSchema(PydanticDjangoModel):
        class Config:
            model = Publication

    class ArticleWithPublicationListSchema(PydanticDjangoModel):

        publications: List[PublicationSchema]

        class Config:
            model = Article

    assert ArticleWithPublicationListSchema.schema() == {
        "title": "ArticleWithPublicationListSchema",
        "description": "A news article.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "headline": {"title": "Headline", "maxLength": 100, "type": "string"},
            "pub_date": {"title": "Pub Date", "type": "string", "format": "date"},
            "publications": {
                "title": "Publications",
                "type": "array",
                "items": {"$ref": "#/definitions/PublicationSchema"},
            },
        },
        "required": ["headline", "pub_date", "publications"],
        "definitions": {
            "PublicationSchema": {
                "title": "PublicationSchema",
                "description": "A news publication.",
                "type": "object",
                "properties": {
                    "article": {
                        "title": "Article",
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": {"type": "integer"},
                        },
                    },
                    "id": {"title": "Id", "type": "integer"},
                    "title": {"title": "Title", "maxLength": 30, "type": "string"},
                },
                "required": ["title"],
            }
        },
    }


@pytest.mark.django_db
def test_foreign_key():
    """
    Test forward foreign-key relationships.
    """

    class ThreadSchema(PydanticDjangoModel):
        class Config:
            model = Thread

    class MessageSchema(PydanticDjangoModel):
        class Config:
            model = Message

    assert MessageSchema.schema() == {
        "title": "MessageSchema",
        "description": "A message posted in a thread.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "content": {"title": "Content", "type": "string"},
            "created_at": {
                "title": "Created At",
                "type": "string",
                "format": "date-time",
            },
            "thread": {"title": "Thread", "type": "integer"},
        },
        "required": ["content", "created_at", "thread"],
    }

    class MessageWithThreadSchema(PydanticDjangoModel):

        thread: ThreadSchema

        class Config:
            model = Message

    assert MessageWithThreadSchema.schema() == {
        "title": "MessageWithThreadSchema",
        "description": "A message posted in a thread.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "content": {"title": "Content", "type": "string"},
            "created_at": {
                "title": "Created At",
                "type": "string",
                "format": "date-time",
            },
            "thread": {"$ref": "#/definitions/ThreadSchema"},
        },
        "required": ["content", "created_at", "thread"],
        "definitions": {
            "ThreadSchema": {
                "title": "ThreadSchema",
                "description": "A thread of messages.",
                "type": "object",
                "properties": {
                    "messages": {
                        "title": "Messages",
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": {"type": "integer"},
                        },
                    },
                    "id": {"title": "Id", "type": "integer"},
                    "title": {"title": "Title", "maxLength": 30, "type": "string"},
                },
                "required": ["title"],
            }
        },
    }


@pytest.mark.django_db
def test_foreign_key_reverse():
    """
    Test reverse foreign-key relationships.
    """

    class MessageSchema(PydanticDjangoModel):
        class Config:
            model = Message

    class ThreadSchema(PydanticDjangoModel):
        class Config:
            model = Thread

    assert ThreadSchema.schema() == {
        "title": "ThreadSchema",
        "description": "A thread of messages.",
        "type": "object",
        "properties": {
            "messages": {
                "title": "Messages",
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                },
            },
            "id": {"title": "Id", "type": "integer"},
            "title": {"title": "Title", "maxLength": 30, "type": "string"},
        },
        "required": ["title"],
    }

    class ThreadWithMessageListSchema(PydanticDjangoModel):
        messages: List[MessageSchema]

        class Config:
            model = Thread

    assert ThreadWithMessageListSchema.schema() == {
        "title": "ThreadWithMessageListSchema",
        "description": "A thread of messages.",
        "type": "object",
        "properties": {
            "messages": {
                "title": "Messages",
                "type": "array",
                "items": {"$ref": "#/definitions/MessageSchema"},
            },
            "id": {"title": "Id", "type": "integer"},
            "title": {"title": "Title", "maxLength": 30, "type": "string"},
        },
        "required": ["messages", "title"],
        "definitions": {
            "MessageSchema": {
                "title": "MessageSchema",
                "description": "A message posted in a thread.",
                "type": "object",
                "properties": {
                    "id": {"title": "Id", "type": "integer"},
                    "content": {"title": "Content", "type": "string"},
                    "created_at": {
                        "title": "Created At",
                        "type": "string",
                        "format": "date-time",
                    },
                    "thread": {"title": "Thread", "type": "integer"},
                },
                "required": ["content", "created_at", "thread"],
            }
        },
    }


@pytest.mark.django_db
def test_one_to_one():
    """
    Test forward one-to-one relationships.
    """

    class UserSchema(PydanticDjangoModel):
        class Config:
            model = User

    class ProfileSchema(PydanticDjangoModel):
        class Config:
            model = Profile

    assert ProfileSchema.schema() == {
        "title": "ProfileSchema",
        "description": "A user's profile.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "user": {"title": "User", "type": "integer"},
            "website": {
                "title": "Website",
                "default": "",
                "maxLength": 200,
                "type": "string",
            },
            "location": {
                "title": "Location",
                "default": "",
                "maxLength": 100,
                "type": "string",
            },
        },
        "required": ["user"],
    }

    class ProfileWithUserSchema(PydanticDjangoModel):
        user: UserSchema

        class Config:
            model = Profile

    assert ProfileWithUserSchema.schema() == {
        "title": "ProfileWithUserSchema",
        "description": "A user's profile.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "user": {"$ref": "#/definitions/UserSchema"},
            "website": {
                "title": "Website",
                "default": "",
                "maxLength": 200,
                "type": "string",
            },
            "location": {
                "title": "Location",
                "default": "",
                "maxLength": 100,
                "type": "string",
            },
        },
        "required": ["user"],
        "definitions": {
            "UserSchema": {
                "title": "UserSchema",
                "description": "A user of the application.",
                "type": "object",
                "properties": {
                    "profile": {"title": "Profile", "type": "integer"},
                    "id": {"title": "Id", "type": "integer"},
                    "first_name": {
                        "title": "First Name",
                        "maxLength": 50,
                        "type": "string",
                    },
                    "last_name": {
                        "title": "Last Name",
                        "maxLength": 50,
                        "type": "string",
                    },
                    "email": {"title": "Email", "maxLength": 254, "type": "string"},
                    "created_at": {
                        "title": "Created At",
                        "type": "string",
                        "format": "date-time",
                    },
                    "updated_at": {
                        "title": "Updated At",
                        "type": "string",
                        "format": "date-time",
                    },
                },
                "required": ["first_name", "email", "created_at", "updated_at"],
            }
        },
    }


@pytest.mark.django_db
def test_one_to_one_reverse():
    """
    Test reverse one-to-one relationships.
    """

    class ProfileSchema(PydanticDjangoModel):
        class Config:
            model = Profile

    class UserSchema(PydanticDjangoModel):
        class Config:
            model = User

    assert ProfileSchema.schema() == {
        "title": "ProfileSchema",
        "description": "A user's profile.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "user": {"title": "User", "type": "integer"},
            "website": {
                "title": "Website",
                "default": "",
                "maxLength": 200,
                "type": "string",
            },
            "location": {
                "title": "Location",
                "default": "",
                "maxLength": 100,
                "type": "string",
            },
        },
        "required": ["user"],
    }

    class UserWithProfileSchema(PydanticDjangoModel):
        profile: ProfileSchema

        class Config:
            model = User

    assert UserWithProfileSchema.schema() == {
        "title": "UserWithProfileSchema",
        "description": "A user of the application.",
        "type": "object",
        "properties": {
            "profile": {"$ref": "#/definitions/ProfileSchema"},
            "id": {"title": "Id", "type": "integer"},
            "first_name": {"title": "First Name", "maxLength": 50, "type": "string"},
            "last_name": {"title": "Last Name", "maxLength": 50, "type": "string"},
            "email": {"title": "Email", "maxLength": 254, "type": "string"},
            "created_at": {
                "title": "Created At",
                "type": "string",
                "format": "date-time",
            },
            "updated_at": {
                "title": "Updated At",
                "type": "string",
                "format": "date-time",
            },
        },
        "required": ["profile", "first_name", "email", "created_at", "updated_at"],
        "definitions": {
            "ProfileSchema": {
                "title": "ProfileSchema",
                "description": "A user's profile.",
                "type": "object",
                "properties": {
                    "id": {"title": "Id", "type": "integer"},
                    "user": {"title": "User", "type": "integer"},
                    "website": {
                        "title": "Website",
                        "default": "",
                        "maxLength": 200,
                        "type": "string",
                    },
                    "location": {
                        "title": "Location",
                        "default": "",
                        "maxLength": 100,
                        "type": "string",
                    },
                },
                "required": ["user"],
            }
        },
    }
