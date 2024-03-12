import datetime
from typing import Dict, List, Optional

import pytest
from pydantic import Field
from testapp.models import (
    Article,
    Bookmark,
    Case,
    Expert,
    Item,
    Message,
    Profile,
    Publication,
    Tagged,
    Thread,
    User,
)

from pydantic import ConfigDict
from djantic import ModelSchema


@pytest.mark.django_db
def test_m2m():
    """
    Test forward m2m relationships.
    """

    class ArticleSchema(ModelSchema):
        model_config = ConfigDict(model=Article)

    assert ArticleSchema.model_json_schema() == {
        "description": "A news article.",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "headline": {
                "description": "headline",
                "maxLength": 100,
                "title": "Headline",
                "type": "string",
            },
            "pub_date": {
                "description": "pub_date",
                "format": "date",
                "title": "Pub Date",
                "type": "string",
            },
            "publications": {
                "description": "id",
                "items": {
                    "additionalProperties": {"type": "integer"},
                    "type": "object",
                },
                "title": "Publications",
                "type": "array",
            },
        },
        "required": ["headline", "pub_date", "publications"],
        "title": "ArticleSchema",
        "type": "object",
    }

    class PublicationSchema(ModelSchema):
        class Config:
            model = Publication

    class ArticleWithPublicationListSchema(ModelSchema):
        publications: List[PublicationSchema]
        model_config = ConfigDict(model=Article)

    assert ArticleWithPublicationListSchema.model_json_schema() == {
        "$defs": {
            "PublicationSchema": {
                "description": "A news publication.",
                "properties": {
                    "article_set": {
                        "default": None,
                        "description": "id",
                        "items": {
                            "additionalProperties": {"type": "integer"},
                            "type": "object",
                        },
                        "title": "Article Set",
                        "type": "array",
                    },
                    "id": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "description": "id",
                        "title": "Id",
                    },
                    "title": {
                        "description": "title",
                        "maxLength": 30,
                        "title": "Title",
                        "type": "string",
                    },
                },
                "required": ["title"],
                "title": "PublicationSchema",
                "type": "object",
            }
        },
        "description": "A news article.",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "headline": {
                "description": "headline",
                "maxLength": 100,
                "title": "Headline",
                "type": "string",
            },
            "pub_date": {
                "description": "pub_date",
                "format": "date",
                "title": "Pub Date",
                "type": "string",
            },
            "publications": {
                "items": {"$ref": "#/$defs/PublicationSchema"},
                "title": "Publications",
                "type": "array",
            },
        },
        "required": ["headline", "pub_date", "publications"],
        "title": "ArticleWithPublicationListSchema",
        "type": "object",
    }

    article = Article.objects.create(
        headline="My Headline", pub_date=datetime.date(2021, 3, 20)
    )
    publication = Publication.objects.create(title="My Publication")
    article.publications.add(publication)

    schema = ArticleWithPublicationListSchema.from_django(article)
    assert schema.dict() == {
        "id": 1,
        "headline": "My Headline",
        "pub_date": datetime.date(2021, 3, 20),
        "publications": [
            {"article_set": [{"id": 1}], "id": 1, "title": "My Publication"}
        ],
    }


@pytest.mark.django_db
def test_foreign_key():
    """
    Test forward foreign-key relationships.
    """

    class ThreadSchema(ModelSchema):
        model_config = ConfigDict(model=Thread)

    class MessageSchema(ModelSchema):
        model_config = ConfigDict(model=Message)

    assert MessageSchema.model_json_schema() == {
        "description": "A message posted in a thread.",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "content": {"description": "content", "title": "Content", "type": "string"},
            "created_at": {
                "description": "created_at",
                "format": "date-time",
                "title": "Created At",
                "type": "string",
            },
            "thread": {"description": "id", "title": "Thread", "type": "integer"},
        },
        "required": ["content", "created_at", "thread"],
        "title": "MessageSchema",
        "type": "object",
    }

    class MessageWithThreadSchema(ModelSchema):
        thread: ThreadSchema
        model_config = ConfigDict(model=Message)

    assert MessageWithThreadSchema.model_json_schema() == {
        "$defs": {
            "ThreadSchema": {
                "description": "A thread of messages.",
                "properties": {
                    "messages": {
                        "default": None,
                        "description": "id",
                        "items": {
                            "additionalProperties": {"type": "integer"},
                            "type": "object",
                        },
                        "title": "Messages",
                        "type": "array",
                    },
                    "id": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "description": "id",
                        "title": "Id",
                    },
                    "title": {
                        "description": "title",
                        "maxLength": 30,
                        "title": "Title",
                        "type": "string",
                    },
                },
                "required": ["title"],
                "title": "ThreadSchema",
                "type": "object",
            }
        },
        "description": "A message posted in a thread.",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "content": {"description": "content", "title": "Content", "type": "string"},
            "created_at": {
                "description": "created_at",
                "format": "date-time",
                "title": "Created At",
                "type": "string",
            },
            "thread": {"$ref": "#/$defs/ThreadSchema"},
        },
        "required": ["content", "created_at", "thread"],
        "title": "MessageWithThreadSchema",
        "type": "object",
    }

    class ThreadWithMessageListSchema(ModelSchema):
        messages: List[MessageSchema]
        model_config = ConfigDict(model=Thread)

    assert ThreadWithMessageListSchema.model_json_schema() == {
        "$defs": {
            "MessageSchema": {
                "description": "A message posted in a thread.",
                "properties": {
                    "id": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "description": "id",
                        "title": "Id",
                    },
                    "content": {
                        "description": "content",
                        "title": "Content",
                        "type": "string",
                    },
                    "created_at": {
                        "description": "created_at",
                        "format": "date-time",
                        "title": "Created At",
                        "type": "string",
                    },
                    "thread": {
                        "description": "id",
                        "title": "Thread",
                        "type": "integer",
                    },
                },
                "required": ["content", "created_at", "thread"],
                "title": "MessageSchema",
                "type": "object",
            }
        },
        "description": "A thread of messages.",
        "properties": {
            "messages": {
                "items": {"$ref": "#/$defs/MessageSchema"},
                "title": "Messages",
                "type": "array",
            },
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "title": {
                "description": "title",
                "maxLength": 30,
                "title": "Title",
                "type": "string",
            },
        },
        "required": ["messages", "title"],
        "title": "ThreadWithMessageListSchema",
        "type": "object",
    }


@pytest.mark.django_db
def test_one_to_one():
    """
    Test forward one-to-one relationships.
    """

    class UserSchema(ModelSchema):
        model_config = ConfigDict(model=User)

    class ProfileSchema(ModelSchema):
        model_config = ConfigDict(model=Profile)

    assert ProfileSchema.model_json_schema() == {
        "description": "A user's profile.",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "user": {"description": "id", "title": "User", "type": "integer"},
            "website": {
                "default": "",
                "description": "website",
                "maxLength": 200,
                "title": "Website",
                "type": "string",
            },
            "location": {
                "default": "",
                "description": "location",
                "maxLength": 100,
                "title": "Location",
                "type": "string",
            },
        },
        "required": ["user"],
        "title": "ProfileSchema",
        "type": "object",
    }

    class ProfileWithUserSchema(ModelSchema):
        user: UserSchema
        model_config = ConfigDict(model=Profile)

    assert ProfileWithUserSchema.model_json_schema() == {
        "$defs": {
            "UserSchema": {
                "description": "A user of the application.",
                "properties": {
                    "profile": {
                        "default": None,
                        "description": "id",
                        "title": "Profile",
                        "type": "integer",
                    },
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
                    "last_name": {
                        "anyOf": [
                            {"maxLength": 50, "type": "string"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "description": "last_name",
                        "title": "Last Name",
                    },
                    "email": {
                        "description": "email",
                        "maxLength": 254,
                        "title": "Email",
                        "type": "string",
                    },
                    "created_at": {
                        "description": "created_at",
                        "format": "date-time",
                        "title": "Created At",
                        "type": "string",
                    },
                    "updated_at": {
                        "description": "updated_at",
                        "format": "date-time",
                        "title": "Updated At",
                        "type": "string",
                    },
                },
                "required": ["first_name", "email", "created_at", "updated_at"],
                "title": "UserSchema",
                "type": "object",
            }
        },
        "description": "A user's profile.",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "user": {"$ref": "#/$defs/UserSchema"},
            "website": {
                "default": "",
                "description": "website",
                "maxLength": 200,
                "title": "Website",
                "type": "string",
            },
            "location": {
                "default": "",
                "description": "location",
                "maxLength": 100,
                "title": "Location",
                "type": "string",
            },
        },
        "required": ["user"],
        "title": "ProfileWithUserSchema",
        "type": "object",
    }


@pytest.mark.django_db
def test_one_to_one_reverse():
    """
    Test reverse one-to-one relationships.
    """

    class ProfileSchema(ModelSchema):
        model_config = ConfigDict(model=Profile)

    class UserSchema(ModelSchema):
        model_config = ConfigDict(model=User)

    assert ProfileSchema.model_json_schema() == {
        "description": "A user's profile.",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "user": {"description": "id", "title": "User", "type": "integer"},
            "website": {
                "default": "",
                "description": "website",
                "maxLength": 200,
                "title": "Website",
                "type": "string",
            },
            "location": {
                "default": "",
                "description": "location",
                "maxLength": 100,
                "title": "Location",
                "type": "string",
            },
        },
        "required": ["user"],
        "title": "ProfileSchema",
        "type": "object",
    }

    class UserWithProfileSchema(ModelSchema):
        profile: ProfileSchema
        model_config = ConfigDict(model=User)

    assert UserWithProfileSchema.model_json_schema() == {
        "$defs": {
            "ProfileSchema": {
                "description": "A user's profile.",
                "properties": {
                    "id": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "description": "id",
                        "title": "Id",
                    },
                    "user": {"description": "id", "title": "User", "type": "integer"},
                    "website": {
                        "default": "",
                        "description": "website",
                        "maxLength": 200,
                        "title": "Website",
                        "type": "string",
                    },
                    "location": {
                        "default": "",
                        "description": "location",
                        "maxLength": 100,
                        "title": "Location",
                        "type": "string",
                    },
                },
                "required": ["user"],
                "title": "ProfileSchema",
                "type": "object",
            }
        },
        "description": "A user of the application.",
        "properties": {
            "profile": {"$ref": "#/$defs/ProfileSchema"},
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
            "last_name": {
                "anyOf": [{"maxLength": 50, "type": "string"}, {"type": "null"}],
                "default": None,
                "description": "last_name",
                "title": "Last Name",
            },
            "email": {
                "description": "email",
                "maxLength": 254,
                "title": "Email",
                "type": "string",
            },
            "created_at": {
                "description": "created_at",
                "format": "date-time",
                "title": "Created At",
                "type": "string",
            },
            "updated_at": {
                "description": "updated_at",
                "format": "date-time",
                "title": "Updated At",
                "type": "string",
            },
        },
        "required": ["profile", "first_name", "email", "created_at", "updated_at"],
        "title": "UserWithProfileSchema",
        "type": "object",
    }


@pytest.mark.django_db
def test_generic_relation():
    """
    Test generic foreign-key relationships.
    """

    class TaggedSchema(ModelSchema):
        model_config = ConfigDict(model=Tagged)

    assert TaggedSchema.model_json_schema() == {
        "description": "Tagged(id, slug, content_type, object_id)",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "slug": {
                "description": "slug",
                "maxLength": 50,
                "title": "Slug",
                "type": "string",
            },
            "content_type": {
                "description": "id",
                "title": "Content Type",
                "type": "integer",
            },
            "object_id": {
                "description": "object_id",
                "title": "Object Id",
                "type": "integer",
            },
            "content_object": {
                "description": "content_object",
                "title": "Content Object",
                "type": "integer",
            },
        },
        "required": ["slug", "content_type", "object_id", "content_object"],
        "title": "TaggedSchema",
        "type": "object",
    }

    class BookmarkSchema(ModelSchema):
        # FIXME: I added this because for some reason in 2.2 the GenericRelation field
        # ends up required, but in 3 it does not.
        tags: List[Dict[str, int]] = None
        model_config = ConfigDict(model=Bookmark)

    assert BookmarkSchema.model_json_schema() == {
        "description": "Bookmark(id, url)",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "url": {
                "description": "url",
                "maxLength": 200,
                "title": "Url",
                "type": "string",
            },
            "tags": {
                "default": None,
                "items": {
                    "additionalProperties": {"type": "integer"},
                    "type": "object",
                },
                "title": "Tags",
                "type": "array",
            },
        },
        "required": ["url"],
        "title": "BookmarkSchema",
        "type": "object",
    }

    class BookmarkWithTaggedSchema(ModelSchema):

        tags: List[TaggedSchema]
        model_config = ConfigDict(model=Bookmark)

    assert BookmarkWithTaggedSchema.model_json_schema() == {
        "$defs": {
            "TaggedSchema": {
                "description": "Tagged(id, slug, content_type, object_id)",
                "properties": {
                    "id": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "description": "id",
                        "title": "Id",
                    },
                    "slug": {
                        "description": "slug",
                        "maxLength": 50,
                        "title": "Slug",
                        "type": "string",
                    },
                    "content_type": {
                        "description": "id",
                        "title": "Content Type",
                        "type": "integer",
                    },
                    "object_id": {
                        "description": "object_id",
                        "title": "Object Id",
                        "type": "integer",
                    },
                    "content_object": {
                        "description": "content_object",
                        "title": "Content Object",
                        "type": "integer",
                    },
                },
                "required": ["slug", "content_type", "object_id", "content_object"],
                "title": "TaggedSchema",
                "type": "object",
            }
        },
        "description": "Bookmark(id, url)",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "url": {
                "description": "url",
                "maxLength": 200,
                "title": "Url",
                "type": "string",
            },
            "tags": {
                "items": {"$ref": "#/$defs/TaggedSchema"},
                "title": "Tags",
                "type": "array",
            },
        },
        "required": ["url", "tags"],
        "title": "BookmarkWithTaggedSchema",
        "type": "object",
    }

    class ItemSchema(ModelSchema):

        tags: List[TaggedSchema]
        model_config = ConfigDict(model=Item)

    # Test without defining a GenericRelation on the model
    assert ItemSchema.model_json_schema() == {
        "$defs": {
            "TaggedSchema": {
                "description": "Tagged(id, slug, content_type, object_id)",
                "properties": {
                    "id": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "description": "id",
                        "title": "Id",
                    },
                    "slug": {
                        "description": "slug",
                        "maxLength": 50,
                        "title": "Slug",
                        "type": "string",
                    },
                    "content_type": {
                        "description": "id",
                        "title": "Content Type",
                        "type": "integer",
                    },
                    "object_id": {
                        "description": "object_id",
                        "title": "Object Id",
                        "type": "integer",
                    },
                    "content_object": {
                        "description": "content_object",
                        "title": "Content Object",
                        "type": "integer",
                    },
                },
                "required": ["slug", "content_type", "object_id", "content_object"],
                "title": "TaggedSchema",
                "type": "object",
            }
        },
        "description": "Item(id, name, item_list)",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "name": {
                "description": "name",
                "maxLength": 100,
                "title": "Name",
                "type": "string",
            },
            "item_list": {"description": "id", "title": "Item List", "type": "integer"},
            "tags": {
                "items": {"$ref": "#/$defs/TaggedSchema"},
                "title": "Tags",
                "type": "array",
            },
        },
        "required": ["name", "item_list", "tags"],
        "title": "ItemSchema",
        "type": "object",
    }


@pytest.mark.django_db
def test_m2m_reverse():
    class ExpertSchema(ModelSchema):
        model_config = ConfigDict(model=Expert)

    class CaseSchema(ModelSchema):
        model_config = ConfigDict(model=Case)

    assert ExpertSchema.model_json_schema() == {
        "description": "Expert(id, name)",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "name": {
                "description": "name",
                "maxLength": 128,
                "title": "Name",
                "type": "string",
            },
            "cases": {
                "description": "id",
                "items": {
                    "additionalProperties": {"type": "integer"},
                    "type": "object",
                },
                "title": "Cases",
                "type": "array",
            },
        },
        "required": ["name", "cases"],
        "title": "ExpertSchema",
        "type": "object",
    }

    assert CaseSchema.model_json_schema() == {
        "description": "Case(id, name, details)",
        "properties": {
            "related_experts": {
                "default": None,
                "description": "id",
                "items": {
                    "additionalProperties": {"type": "integer"},
                    "type": "object",
                },
                "title": "Related Experts",
                "type": "array",
            },
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "name": {
                "description": "name",
                "maxLength": 128,
                "title": "Name",
                "type": "string",
            },
            "details": {"description": "details", "title": "Details", "type": "string"},
        },
        "required": ["name", "details"],
        "title": "CaseSchema",
        "type": "object",
    }
    case = Case.objects.create(name="My Case", details="Some text data.")
    expert = Expert.objects.create(name="My Expert")
    case_schema = CaseSchema.from_django(case)
    expert_schema = ExpertSchema.from_django(expert)
    assert case_schema.dict() == {
        "related_experts": [],
        "id": 1,
        "name": "My Case",
        "details": "Some text data.",
    }
    assert expert_schema.dict() == {"id": 1, "name": "My Expert", "cases": []}

    expert.cases.add(case)
    case_schema = CaseSchema.from_django(case)
    expert_schema = ExpertSchema.from_django(expert)
    assert case_schema.dict() == {
        "related_experts": [{"id": 1}],
        "id": 1,
        "name": "My Case",
        "details": "Some text data.",
    }
    assert expert_schema.dict() == {"id": 1, "name": "My Expert", "cases": [{"id": 1}]}

    class CustomExpertSchema(ModelSchema):
        """Custom schema"""

        name: Optional[str]
        model_config = ConfigDict(model=Expert)

    class CaseSchema(ModelSchema):
        related_experts: List[CustomExpertSchema]
        model_config = ConfigDict(model=Case)

    assert CaseSchema.model_json_schema() == {
        "$defs": {
            "CustomExpertSchema": {
                "description": "Custom schema",
                "properties": {
                    "id": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "description": "id",
                        "title": "Id",
                    },
                    "name": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Name",
                    },
                    "cases": {
                        "description": "id",
                        "items": {
                            "additionalProperties": {"type": "integer"},
                            "type": "object",
                        },
                        "title": "Cases",
                        "type": "array",
                    },
                },
                "required": ["cases"],
                "title": "CustomExpertSchema",
                "type": "object",
            }
        },
        "description": "Case(id, name, details)",
        "properties": {
            "related_experts": {
                "items": {"$ref": "#/$defs/CustomExpertSchema"},
                "title": "Related Experts",
                "type": "array",
            },
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "name": {
                "description": "name",
                "maxLength": 128,
                "title": "Name",
                "type": "string",
            },
            "details": {"description": "details", "title": "Details", "type": "string"},
        },
        "required": ["related_experts", "name", "details"],
        "title": "CaseSchema",
        "type": "object",
    }

    case_schema = CaseSchema.from_django(case)
    assert case_schema.dict() == {
        "related_experts": [{"id": 1, "name": "My Expert", "cases": [{"id": 1}]}],
        "id": 1,
        "name": "My Case",
        "details": "Some text data.",
    }


@pytest.mark.django_db
def test_alias():
    class ProfileSchema(ModelSchema):
        first_name: str = Field(alias="user__first_name")
        model_config = ConfigDict(model=Profile)

    assert ProfileSchema.model_json_schema() == {
        "description": "A user's profile.",
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "user": {"description": "id", "title": "User", "type": "integer"},
            "website": {
                "default": "",
                "description": "website",
                "maxLength": 200,
                "title": "Website",
                "type": "string",
            },
            "location": {
                "default": "",
                "description": "location",
                "maxLength": 100,
                "title": "Location",
                "type": "string",
            },
        },
        "required": ["user", "user__first_name"],
        "title": "ProfileSchema",
        "type": "object",
    }

    user = User.objects.create(first_name="Jack")
    profile = Profile.objects.create(
        user=user, website="www.github.com", location="Europe"
    )
    assert ProfileSchema.from_django(profile).dict() == {
        "first_name": "Jack",
        "id": 1,
        "location": "Europe",
        "user": 1,
        "website": "www.github.com",
    }
