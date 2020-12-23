from typing import List

import pytest

from testapp.models import (
    User,
    Profile,
    Thread,
    Message,
    Publication,
    Article,
    Item,
    ItemList,
    Tagged,
    Bookmark,
)

from pydantic_django import ModelSchema


@pytest.mark.django_db
def test_m2m():
    """
    Test forward m2m relationships.
    """

    class ArticleSchema(ModelSchema):
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

    class PublicationSchema(ModelSchema):
        class Config:
            model = Publication

    class ArticleWithPublicationListSchema(ModelSchema):

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

    class ThreadSchema(ModelSchema):
        class Config:
            model = Thread

    class MessageSchema(ModelSchema):
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

    class MessageWithThreadSchema(ModelSchema):

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

    class MessageSchema(ModelSchema):
        class Config:
            model = Message

    class ThreadSchema(ModelSchema):
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

    class ThreadWithMessageListSchema(ModelSchema):
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

    class UserSchema(ModelSchema):
        class Config:
            model = User

    class ProfileSchema(ModelSchema):
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

    class ProfileWithUserSchema(ModelSchema):
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

    class ProfileSchema(ModelSchema):
        class Config:
            model = Profile

    class UserSchema(ModelSchema):
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

    class UserWithProfileSchema(ModelSchema):
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


@pytest.mark.django_db
def test_generic_relation():
    """
    Test generic foreign-key relationships.
    """

    class TaggedSchema(ModelSchema):
        class Config:
            model = Tagged

    assert TaggedSchema.schema() == {
        "title": "TaggedSchema",
        "description": "Tagged(id, slug, content_type, object_id)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "slug": {"title": "Slug", "maxLength": 50, "type": "string"},
            "content_type": {"title": "Content Type", "type": "integer"},
            "object_id": {"title": "Object Id", "type": "integer"},
            "content_object": {"title": "Content Object", "type": "integer"},
        },
        "required": ["slug", "content_type", "object_id", "content_object"],
    }

    class BookmarkSchema(ModelSchema):
        class Config:
            model = Bookmark

    assert BookmarkSchema.schema() == {
        "title": "BookmarkSchema",
        "description": "Bookmark(id, url)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "url": {"title": "Url", "maxLength": 200, "type": "string"},
            "tags": {
                "title": "Tags",
                "type": "array",
                "items": {"type": "object", "additionalProperties": {"type": "integer"}},
            },
        },
        "required": ["url"],
    }

    class BookmarkWithTaggedSchema(ModelSchema):

        tags: List[TaggedSchema]

        class Config:
            model = Bookmark

    assert BookmarkWithTaggedSchema.schema() == {
        "title": "BookmarkWithTaggedSchema",
        "description": "Bookmark(id, url)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "url": {"title": "Url", "maxLength": 200, "type": "string"},
            "tags": {
                "title": "Tags",
                "type": "array",
                "items": {"$ref": "#/definitions/TaggedSchema"},
            },
        },
        "required": ["url", "tags"],
        "definitions": {
            "TaggedSchema": {
                "title": "TaggedSchema",
                "description": "Tagged(id, slug, content_type, object_id)",
                "type": "object",
                "properties": {
                    "id": {"title": "Id", "type": "integer"},
                    "slug": {"title": "Slug", "maxLength": 50, "type": "string"},
                    "content_type": {"title": "Content Type", "type": "integer"},
                    "object_id": {"title": "Object Id", "type": "integer"},
                    "content_object": {"title": "Content Object", "type": "integer"},
                },
                "required": ["slug", "content_type", "object_id", "content_object"],
            }
        },
    }

    class ItemSchema(ModelSchema):

        tags: List[TaggedSchema]

        class Config:
            model = Item

    # Test without defining a GenericRelation on the model.
    assert ItemSchema.schema() == {
        "title": "ItemSchema",
        "description": "Item(id, name, item_list)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "name": {"title": "Name", "maxLength": 100, "type": "string"},
            "item_list": {"title": "Item List", "type": "integer"},
            "tags": {
                "title": "Tags",
                "type": "array",
                "items": {"$ref": "#/definitions/TaggedSchema"},
            },
        },
        "required": ["name", "item_list", "tags"],
        "definitions": {
            "TaggedSchema": {
                "title": "TaggedSchema",
                "description": "Tagged(id, slug, content_type, object_id)",
                "type": "object",
                "properties": {
                    "id": {"title": "Id", "type": "integer"},
                    "slug": {"title": "Slug", "maxLength": 50, "type": "string"},
                    "content_type": {"title": "Content Type", "type": "integer"},
                    "object_id": {"title": "Object Id", "type": "integer"},
                    "content_object": {"title": "Content Object", "type": "integer"},
                },
                "required": ["slug", "content_type", "object_id", "content_object"],
            }
        },
    }
