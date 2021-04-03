from typing import List

import pytest

from testapp.models import User, Profile, Thread, Message, Tagged, Bookmark

from pydantic_django import ModelSchema


@pytest.mark.django_db
def test_get_instance():
    """
    Test retrieving an existing Django object to populate the schema model.
    """

    user = User.objects.create(
        first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com"
    )

    class UserSchema(ModelSchema):
        class Config:
            model = User
            include = ["id", "first_name"]

    assert UserSchema.from_django(user).dict() == {"first_name": "Jordan", "id": 1}


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
    assert user_schema_qs == [
        {
            "email": "jordan@eremieff.com",
            "first_name": "Jordan",
            "id": 1,
            "profile": 1,
        },
        {"email": "sara@example.com", "first_name": "Sara", "id": 2, "profile": 2},
    ]

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
    assert user_with_profile_schema_qs == [
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


@pytest.mark.django_db
def test_get_queryset_with_foreign_key():
    """
    Test retrieving a Django queryset with foreign-key relationships.
    """

    thread = Thread.objects.create(title="My thread topic")
    thread2 = Thread.objects.create(title="Another topic")
    for content in ("I agree.", "I disagree!", "lol"):
        message_one = Message.objects.create(content=content, thread=thread)
        Message.objects.create(content=content, thread=thread2)

    class MessageSchema(ModelSchema):
        class Config:
            model = Message
            exclude = ["created_at"]

    schema = MessageSchema.from_django(message_one)
    assert schema.dict() == {"id": 5, "content": "lol", "thread": 1}

    class ThreadSchema(ModelSchema):
        class Config:
            model = Thread
            exclude = ["created_at"]

    class MessageWithThreadSchema(ModelSchema):
        thread: ThreadSchema

        class Config:
            model = Message
            exclude = ["created_at"]

    schema = MessageWithThreadSchema.from_django(message_one)
    assert schema.dict() == {
        "id": 5,
        "content": "lol",
        "thread": {
            "messages": [{"id": 1}, {"id": 3}, {"id": 5}],
            "id": 1,
            "title": "My thread topic",
        },
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
    assert thread_schema_qs == [
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

    # Test when using a declared sub-model
    class ThreadWithMessageListSchema(ModelSchema):
        messages: List[MessageSchema]

        class Config:
            model = Thread
            exclude = ["created_at", "updated_at"]

    thread_with_message_list_schema_qs = ThreadWithMessageListSchema.from_django(
        threads, many=True
    )

    assert thread_with_message_list_schema_qs == [
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


@pytest.mark.django_db
def test_get_queryset_with_generic_foreign_key():

    bookmark = Bookmark.objects.create(url="https://github.com")
    bookmark.tags.create(slug="tag-1")
    bookmark.tags.create(slug="tag-2")

    class TaggedSchema(ModelSchema):
        class Config:
            model = Tagged

    class BookmarkSchema(ModelSchema):
        class Config:
            model = Bookmark

    schema = BookmarkSchema.from_django(bookmark)
    schema.dict() == {
        "id": 1,
        "url": "https://github.com",
        "tags": [{"pk": 1}, {"pk": 2}],
    }
