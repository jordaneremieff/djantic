from typing import List

import pytest

from testapp.models import User, Profile, Thread, Message, Tagged, Bookmark, Item

from pydantic_django import ModelSchema


@pytest.mark.django_db
def test_query_create():
    """
    Test creating and saving a Django object to populate the schema model.
    """

    class UserSchema(ModelSchema):
        class Config:
            model = User
            include = ["id", "email"]

    user_schema = UserSchema.create(first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com")

    assert (
        user_schema.schema()
        == {
            "description": "A user of the application.",
            "properties": {
                "email": {"maxLength": 254, "title": "Email", "type": "string"},
                "id": {"title": "Id", "type": "integer"},
            },
            "required": ["email"],
            "title": "UserSchema",
            "type": "object",
        }
        == UserSchema.schema()
    )

    user = User.objects.get(id=user_schema.instance.id)

    assert UserSchema.from_django(user).dict() == user_schema.dict() == {"email": "jordan@eremieff.com", "id": 1}


@pytest.mark.django_db
def test_get_instance():
    """
    Test retrieving an existing Django object to populate the schema model.
    """

    user = User.objects.create(first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com")

    class UserSchema(ModelSchema):
        class Config:
            model = User
            include = ["id", "first_name"]

    user_schema = UserSchema.get(id=user.id)

    assert UserSchema.from_django(user).dict() == user_schema.dict() == {"first_name": "Jordan", "id": 1}


@pytest.mark.django_db
def test_get_instance_with_generic_foreign_key():

    bookmark = Bookmark.objects.create(url="https://www.djangoproject.com/")
    Tagged.objects.create(content_object=bookmark, slug="django")

    class TaggedSchema(ModelSchema):
        class Config:
            model = Tagged

    class BookmarkWithTaggedSchema(ModelSchema):

        tags: List[TaggedSchema]

        class Config:
            model = Bookmark

    bookmark_with_tagged_schema = BookmarkWithTaggedSchema.from_django(bookmark)

    assert bookmark_with_tagged_schema.dict() == {
        "id": 1,
        "tags": [{"content_type": 20, "id": 1, "object_id": 1, "slug": "django"}],
        "url": "https://www.djangoproject.com/",
    }


@pytest.mark.django_db
def test_save_instance():
    """
    Test updating and saving a Django object and updating the schema model.
    """
    user = User.objects.create(first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com")

    class UserSchema(ModelSchema):
        class Config:
            model = User
            include = ["id", "first_name", "last_name"]

    user_schema = UserSchema.get(id=user.id)
    user_schema.instance.last_name = "Lastname"
    user_schema.save()

    user_values_from_db = dict(User.objects.filter(id=user.id).values("id", "first_name", "last_name")[0])
    assert user_schema.dict() == {"first_name": "Jordan", "id": 1, "last_name": "Lastname"} == user_values_from_db


@pytest.mark.django_db
def test_refresh_instance():
    """
    Test refreshing a Django object from the database and updating the schema model.
    """
    user = User.objects.create(first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com")

    class UserSchema(ModelSchema):
        class Config:
            model = User
            include = ["id", "email", "profile"]

    user_schema = UserSchema.get(id=user.id)
    user_schema_values = user_schema.dict()

    assert not user_schema_values["profile"]
    assert user_schema_values["email"] == "jordan@eremieff.com"

    profile = Profile.objects.create(user=user, website="https://github.com/jordaneremieff", location="Australia")
    user.email = "hello@eremieff.com"
    user.save()

    user_schema.refresh()

    user_schema_values = user_schema.dict()

    assert user_schema_values["profile"] == profile.pk
    assert user_schema_values["email"] == "hello@eremieff.com"


@pytest.mark.django_db
def test_delete_instance():
    """
    Test deleting a Django object and clearing the schema model.
    """
    user = User.objects.create(first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com")

    class UserSchema(ModelSchema):
        class Config:
            model = User

    user_schema = UserSchema.get(id=user.id)
    assert user_schema.dict()["id"] == user.id

    user_schema.delete()
    assert not user_schema.dict()


@pytest.mark.django_db
def test_get_queryset_with_reverse_one_to_one():
    """
    Test retrieving a Django queryset with reverse one-to-one relationships.
    """
    user_data = [
        {"first_name": "Jordan", "email": "jordan@eremieff.com"},
        {"first_name": "Sara", "email": "sara@example.com"},
    ]
    for kwargs in user_data:
        user = User.objects.create(**kwargs)
        Profile.objects.create(user=user, location="Australia")

    class UserSchema(ModelSchema):
        class Config:
            model = User
            include = ["id", "email", "first_name", "profile"]

    users = User.objects.all()
    user_schema_qs = UserSchema.from_django(users, many=True)
    assert user_schema_qs.dict() == {
        "users": [
            {
                "email": "jordan@eremieff.com",
                "first_name": "Jordan",
                "id": 1,
                "profile": 1,
            },
            {"email": "sara@example.com", "first_name": "Sara", "id": 2, "profile": 2},
        ]
    }

    # Test when using a declared sub-model
    class ProfileSchema(ModelSchema):
        class Config:
            model = Profile
            include = ["id", "location"]

    class UserWithProfileSchema(ModelSchema):

        profile: ProfileSchema

        class Config:
            model = User
            exclude = ["created_at", "updated_at", "last_name"]

    users = User.objects.all()

    user_with_profile_schema_qs = UserWithProfileSchema.from_django(users, many=True)
    assert user_with_profile_schema_qs.dict() == {
        "users": [
            {
                "email": "jordan@eremieff.com",
                "first_name": "Jordan",
                "id": 1,
                "profile": {"id": 1, "location": "Australia"},
            },
            {
                "email": "sara@example.com",
                "first_name": "Sara",
                "id": 2,
                "profile": {"id": 2, "location": "Australia"},
            },
        ]
    }


@pytest.mark.django_db
def test_get_queryset_with_reverse_foreign_key():
    """
    Test retrieving a Django queryset with reverse foreign-key relationships.
    """

    thread = Thread.objects.create(title="My thread topic")
    thread2 = Thread.objects.create(title="Another topic")
    for content in ("I agree.", "I disagree!", "lol"):
        Message.objects.create(content=content, thread=thread)
        Message.objects.create(content=content, thread=thread2)

    threads = Thread.objects.all()

    class MessageSchema(ModelSchema):
        class Config:
            model = Message
            include = ["id", "content"]

    class ThreadSchema(ModelSchema):
        class Config:
            model = Thread

    thread_schema_qs = ThreadSchema.from_django(threads, many=True)
    assert thread_schema_qs.dict() == {
        "threads": [
            {
                "messages": [{"id": 2}, {"id": 4}, {"id": 6}],
                "id": 2,
                "title": "Another topic",
            },
            {
                "messages": [{"id": 1}, {"id": 3}, {"id": 5}],
                "id": 1,
                "title": "My thread topic",
            },
        ]
    }

    # Test when using a declared sub-model
    class ThreadWithMessageListSchema(ModelSchema):
        messages: List[MessageSchema]

        class Config:
            model = Thread
            exclude = ["created_at", "updated_at"]

    thread_with_message_list_schema_qs = ThreadWithMessageListSchema.from_django(threads, many=True)

    assert thread_with_message_list_schema_qs.dict() == {
        "threads": [
            {
                "messages": [
                    {"id": 2, "content": "I agree."},
                    {"id": 4, "content": "I disagree!"},
                    {"id": 6, "content": "lol"},
                ],
                "id": 2,
                "title": "Another topic",
            },
            {
                "messages": [
                    {"id": 1, "content": "I agree."},
                    {"id": 3, "content": "I disagree!"},
                    {"id": 5, "content": "lol"},
                ],
                "id": 1,
                "title": "My thread topic",
            },
        ]
    }
