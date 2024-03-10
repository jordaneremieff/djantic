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


@pytest.mark.skip
@pytest.mark.django_db
def test_m2m():
    """
    Test forward m2m relationships.
    """

    class ArticleSchema(ModelSchema):
        model_config = ConfigDict(model=Article)

    assert ArticleSchema.model_json_schema() == {
        "title": "ArticleSchema",
        "description": "A news article.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "headline": {
                "title": "Headline",
                "description": "headline",
                "maxLength": 100,
                "type": "string",
            },
            "pub_date": {
                "title": "Pub Date",
                "description": "pub_date",
                "type": "string",
                "format": "date",
            },
            "publications": {
                "title": "Publications",
                "description": "id",
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
        model_config = ConfigDict(model=Article)

    assert ArticleWithPublicationListSchema.model_json_schema() == {
        "title": "ArticleWithPublicationListSchema",
        "description": "A news article.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "headline": {
                "title": "Headline",
                "description": "headline",
                "maxLength": 100,
                "type": "string",
            },
            "pub_date": {
                "title": "Pub Date",
                "description": "pub_date",
                "type": "string",
                "format": "date",
            },
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
                    "article_set": {
                        "title": "Article Set",
                        "description": "id",
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": {"type": "integer"},
                        },
                    },
                    "id": {"title": "Id", "description": "id", "type": "integer"},
                    "title": {
                        "title": "Title",
                        "description": "title",
                        "maxLength": 30,
                        "type": "string",
                    },
                },
                "required": ["title"],
            }
        },
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


@pytest.mark.skip
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
        "title": "MessageSchema",
        "description": "A message posted in a thread.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "content": {"title": "Content", "description": "content", "type": "string"},
            "created_at": {
                "title": "Created At",
                "description": "created_at",
                "type": "string",
                "format": "date-time",
            },
            "thread": {"title": "Thread", "description": "id", "type": "integer"},
        },
        "required": ["content", "created_at", "thread"],
    }

    class MessageWithThreadSchema(ModelSchema):
        thread: ThreadSchema
        model_config = ConfigDict(model=Message)

    assert MessageWithThreadSchema.model_json_schema() == {
        "title": "MessageWithThreadSchema",
        "description": "A message posted in a thread.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "content": {"title": "Content", "description": "content", "type": "string"},
            "created_at": {
                "title": "Created At",
                "description": "created_at",
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
                        "description": "id",
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": {"type": "integer"},
                        },
                    },
                    "id": {"title": "Id", "description": "id", "type": "integer"},
                    "title": {
                        "title": "Title",
                        "description": "title",
                        "maxLength": 30,
                        "type": "string",
                    },
                },
                "required": ["title"],
            }
        },
    }

    class ThreadWithMessageListSchema(ModelSchema):
        messages: List[MessageSchema]
        model_config = ConfigDict(model=Thread)

    assert ThreadWithMessageListSchema.model_json_schema() == {
        "title": "ThreadWithMessageListSchema",
        "description": "A thread of messages.",
        "type": "object",
        "properties": {
            "messages": {
                "title": "Messages",
                "type": "array",
                "items": {"$ref": "#/definitions/MessageSchema"},
            },
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "title": {
                "title": "Title",
                "description": "title",
                "maxLength": 30,
                "type": "string",
            },
        },
        "required": ["messages", "title"],
        "definitions": {
            "MessageSchema": {
                "title": "MessageSchema",
                "description": "A message posted in a thread.",
                "type": "object",
                "properties": {
                    "id": {"title": "Id", "description": "id", "type": "integer"},
                    "content": {
                        "title": "Content",
                        "description": "content",
                        "type": "string",
                    },
                    "created_at": {
                        "title": "Created At",
                        "description": "created_at",
                        "type": "string",
                        "format": "date-time",
                    },
                    "thread": {
                        "title": "Thread",
                        "description": "id",
                        "type": "integer",
                    },
                },
                "required": ["content", "created_at", "thread"],
            }
        },
    }

@pytest.mark.skip
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
        "title": "ProfileSchema",
        "description": "A user's profile.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "user": {"title": "User", "description": "id", "type": "integer"},
            "website": {
                "title": "Website",
                "description": "website",
                "default": "",
                "maxLength": 200,
                "type": "string",
            },
            "location": {
                "title": "Location",
                "description": "location",
                "default": "",
                "maxLength": 100,
                "type": "string",
            },
        },
        "required": ["user"],
    }

    class ProfileWithUserSchema(ModelSchema):
        user: UserSchema
        model_config = ConfigDict(model=Profile)

    assert ProfileWithUserSchema.model_json_schema() == {
        "title": "ProfileWithUserSchema",
        "description": "A user's profile.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "user": {"$ref": "#/definitions/UserSchema"},
            "website": {
                "title": "Website",
                "description": "website",
                "default": "",
                "maxLength": 200,
                "type": "string",
            },
            "location": {
                "title": "Location",
                "description": "location",
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
                    "profile": {
                        "title": "Profile",
                        "description": "id",
                        "type": "integer",
                    },
                    "id": {"title": "Id", "description": "id", "type": "integer"},
                    "first_name": {
                        "title": "First Name",
                        "description": "first_name",
                        "maxLength": 50,
                        "type": "string",
                    },
                    "last_name": {
                        "title": "Last Name",
                        "description": "last_name",
                        "maxLength": 50,
                        "type": "string",
                    },
                    "email": {
                        "title": "Email",
                        "description": "email",
                        "maxLength": 254,
                        "type": "string",
                    },
                    "created_at": {
                        "title": "Created At",
                        "description": "created_at",
                        "type": "string",
                        "format": "date-time",
                    },
                    "updated_at": {
                        "title": "Updated At",
                        "description": "updated_at",
                        "type": "string",
                        "format": "date-time",
                    },
                },
                "required": ["first_name", "email", "created_at", "updated_at"],
            }
        },
    }

@pytest.mark.skip
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
        "title": "ProfileSchema",
        "description": "A user's profile.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "user": {"title": "User", "description": "id", "type": "integer"},
            "website": {
                "title": "Website",
                "description": "website",
                "default": "",
                "maxLength": 200,
                "type": "string",
            },
            "location": {
                "title": "Location",
                "description": "location",
                "default": "",
                "maxLength": 100,
                "type": "string",
            },
        },
        "required": ["user"],
    }

    class UserWithProfileSchema(ModelSchema):
        profile: ProfileSchema
        model_config = ConfigDict(model=User)

    assert UserWithProfileSchema.model_json_schema() == {
        "title": "UserWithProfileSchema",
        "description": "A user of the application.",
        "type": "object",
        "properties": {
            "profile": {"$ref": "#/definitions/ProfileSchema"},
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "first_name": {
                "title": "First Name",
                "description": "first_name",
                "maxLength": 50,
                "type": "string",
            },
            "last_name": {
                "title": "Last Name",
                "description": "last_name",
                "maxLength": 50,
                "type": "string",
            },
            "email": {
                "title": "Email",
                "description": "email",
                "maxLength": 254,
                "type": "string",
            },
            "created_at": {
                "title": "Created At",
                "description": "created_at",
                "type": "string",
                "format": "date-time",
            },
            "updated_at": {
                "title": "Updated At",
                "description": "updated_at",
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
                    "id": {"title": "Id", "description": "id", "type": "integer"},
                    "user": {"title": "User", "description": "id", "type": "integer"},
                    "website": {
                        "title": "Website",
                        "description": "website",
                        "default": "",
                        "maxLength": 200,
                        "type": "string",
                    },
                    "location": {
                        "title": "Location",
                        "description": "location",
                        "default": "",
                        "maxLength": 100,
                        "type": "string",
                    },
                },
                "required": ["user"],
            }
        },
    }

@pytest.mark.skip
@pytest.mark.django_db
def test_generic_relation():
    """
    Test generic foreign-key relationships.
    """

    class TaggedSchema(ModelSchema):
        model_config = ConfigDict(model=Tagged)

    assert TaggedSchema.model_json_schema() == {
        "title": "TaggedSchema",
        "description": "Tagged(id, slug, content_type, object_id)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "slug": {
                "title": "Slug",
                "description": "slug",
                "maxLength": 50,
                "type": "string",
            },
            "content_type": {
                "title": "Content Type",
                "description": "id",
                "type": "integer",
            },
            "object_id": {
                "title": "Object Id",
                "description": "object_id",
                "type": "integer",
            },
            "content_object": {
                "title": "Content Object",
                "description": "content_object",
                "type": "integer",
            },
        },
        "required": ["slug", "content_type", "object_id", "content_object"],
    }

    class BookmarkSchema(ModelSchema):
        # FIXME: I added this because for some reason in 2.2 the GenericRelation field
        # ends up required, but in 3 it does not.
        tags: List[Dict[str, int]] = None
        model_config = ConfigDict(model=Bookmark)

    assert BookmarkSchema.model_json_schema() == {
        "title": "BookmarkSchema",
        "description": "Bookmark(id, url)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "url": {
                "title": "Url",
                "description": "url",
                "maxLength": 200,
                "type": "string",
            },
            "tags": {
                "title": "Tags",
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                },
            },
        },
        "required": ["url"],
    }

    class BookmarkWithTaggedSchema(ModelSchema):

        tags: List[TaggedSchema]
        model_config = ConfigDict(model=Bookmark)

    assert BookmarkWithTaggedSchema.model_json_schema() == {
        "title": "BookmarkWithTaggedSchema",
        "description": "Bookmark(id, url)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "url": {
                "title": "Url",
                "description": "url",
                "maxLength": 200,
                "type": "string",
            },
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
                    "id": {"title": "Id", "description": "id", "type": "integer"},
                    "slug": {
                        "title": "Slug",
                        "description": "slug",
                        "maxLength": 50,
                        "type": "string",
                    },
                    "content_type": {
                        "title": "Content Type",
                        "description": "id",
                        "type": "integer",
                    },
                    "object_id": {
                        "title": "Object Id",
                        "description": "object_id",
                        "type": "integer",
                    },
                    "content_object": {
                        "title": "Content Object",
                        "description": "content_object",
                        "type": "integer",
                    },
                },
                "required": ["slug", "content_type", "object_id", "content_object"],
            }
        },
    }

    class ItemSchema(ModelSchema):

        tags: List[TaggedSchema]
        model_config = ConfigDict(model=Item)

    # Test without defining a GenericRelation on the model
    assert ItemSchema.model_json_schema() == {
        "title": "ItemSchema",
        "description": "Item(id, name, item_list)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "name": {
                "title": "Name",
                "description": "name",
                "maxLength": 100,
                "type": "string",
            },
            "item_list": {
                "title": "Item List",
                "description": "id",
                "type": "integer",
            },
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
                    "id": {"title": "Id", "description": "id", "type": "integer"},
                    "slug": {
                        "title": "Slug",
                        "description": "slug",
                        "maxLength": 50,
                        "type": "string",
                    },
                    "content_type": {
                        "title": "Content Type",
                        "description": "id",
                        "type": "integer",
                    },
                    "object_id": {
                        "title": "Object Id",
                        "description": "object_id",
                        "type": "integer",
                    },
                    "content_object": {
                        "title": "Content Object",
                        "description": "content_object",
                        "type": "integer",
                    },
                },
                "required": ["slug", "content_type", "object_id", "content_object"],
            }
        },
    }

@pytest.mark.skip
@pytest.mark.django_db
def test_m2m_reverse():
    class ExpertSchema(ModelSchema):
        model_config = ConfigDict(model=Expert)

    class CaseSchema(ModelSchema):
        model_config = ConfigDict(model=Case)

    assert ExpertSchema.model_json_schema() == {
        "title": "ExpertSchema",
        "description": "Expert(id, name)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "name": {
                "title": "Name",
                "description": "name",
                "maxLength": 128,
                "type": "string",
            },
            "cases": {
                "title": "Cases",
                "description": "id",
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                },
            },
        },
        "required": ["name", "cases"],
    }

    assert CaseSchema.model_json_schema() == {
        "title": "CaseSchema",
        "description": "Case(id, name, details)",
        "type": "object",
        "properties": {
            "related_experts": {
                "title": "Related Experts",
                "description": "id",
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                },
            },
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "name": {
                "title": "Name",
                "description": "name",
                "maxLength": 128,
                "type": "string",
            },
            "details": {"title": "Details", "description": "details", "type": "string"},
        },
        "required": ["name", "details"],
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
        "title": "CaseSchema",
        "description": "Case(id, name, details)",
        "type": "object",
        "properties": {
            "related_experts": {
                "title": "Related Experts",
                "type": "array",
                "items": {"$ref": "#/definitions/CustomExpertSchema"},
            },
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "name": {
                "title": "Name",
                "description": "name",
                "maxLength": 128,
                "type": "string",
            },
            "details": {"title": "Details", "description": "details", "type": "string"},
        },
        "required": ["related_experts", "name", "details"],
        "definitions": {
            "CustomExpertSchema": {
                "title": "CustomExpertSchema",
                "description": "Custom schema",
                "type": "object",
                "properties": {
                    "id": {"title": "Id", "description": "id", "type": "integer"},
                    "name": {"title": "Name", "type": "string"},
                    "cases": {
                        "title": "Cases",
                        "description": "id",
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": {"type": "integer"},
                        },
                    },
                },
                "required": ["cases"],
            }
        },
    }

    case_schema = CaseSchema.from_django(case)
    assert case_schema.dict() == {
        "related_experts": [{"id": 1, "name": "My Expert", "cases": [{"id": 1}]}],
        "id": 1,
        "name": "My Case",
        "details": "Some text data.",
    }

@pytest.mark.skip
@pytest.mark.django_db
def test_alias():
    class ProfileSchema(ModelSchema):
        first_name: str = Field(alias="user__first_name")
        model_config = ConfigDict(model=Profile)

    assert ProfileSchema.model_json_schema() == {
        "title": "ProfileSchema",
        "description": "A user's profile.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "user": {"title": "User", "description": "id", "type": "integer"},
            "website": {
                "title": "Website",
                "description": "website",
                "default": "",
                "maxLength": 200,
                "type": "string",
            },
            "location": {
                "title": "Location",
                "description": "location",
                "default": "",
                "maxLength": 100,
                "type": "string",
            },
            "user__first_name": {"title": "User  First Name", "type": "string"},
        },
        "required": ["user", "user__first_name"],
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
