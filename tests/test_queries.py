import pytest

from testapp.models import User, Profile

from pydantic_django import PydanticDjangoModel


@pytest.mark.django_db
def test_query_create():
    """
    Test creating and saving an object to populate a new model.
    """

    class PydanticUser(PydanticDjangoModel):
        class Config:
            model = User
            include = ["id", "first_name", "last_name", "email"]

    pydantic_user = PydanticUser.create(
        first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com"
    )

    assert (
        pydantic_user.schema()
        == {
            "title": "PydanticUser",
            "description": "A user of the application.",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "type": "integer"},
                "first_name": {
                    "title": "First Name",
                    "maxLength": 50,
                    "type": "string",
                },
                "last_name": {"title": "Last Name", "maxLength": 50, "type": "string"},
                "email": {"title": "Email", "maxLength": 254, "type": "string"},
            },
            "required": ["first_name", "email"],
        }
        == PydanticUser.schema()
    )
    assert pydantic_user.dict() == {
        "email": "jordan@eremieff.com",
        "first_name": "Jordan",
        "id": 1,
        "last_name": "Eremieff",
    }

    user = User.objects.get(id=pydantic_user.instance.id)
    assert PydanticUser.from_django(user).dict() == pydantic_user.dict()


@pytest.mark.django_db
def test_query_get():
    """
    Test retrieving an existing object to populate a new model.
    """

    user = User.objects.create(
        first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com"
    )

    class PydanticUser(PydanticDjangoModel):
        class Config:
            model = User
            include = ["id", "first_name"]

    pydantic_user = PydanticUser.get(id=user.id)
    assert pydantic_user.schema() == {
        "title": "PydanticUser",
        "description": "A user of the application.",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "first_name": {"title": "First Name", "maxLength": 50, "type": "string"},
        },
        "required": ["first_name"],
    }
    assert pydantic_user.dict() == {"first_name": "Jordan", "id": 1}


@pytest.mark.django_db
def test_query_save():
    """
    Test saving changes to an instance and updating the model.
    """
    user = User.objects.create(
        first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com"
    )

    class PydanticUser(PydanticDjangoModel):
        class Config:
            model = User
            include = ["id", "first_name", "last_name"]

    pydantic_user = PydanticUser.get(id=user.id)
    pydantic_user.instance.last_name = "Test"
    pydantic_user.save()
    assert pydantic_user.dict() == {
        "first_name": "Jordan",
        "id": 1,
        "last_name": "Test",
    }


@pytest.mark.django_db
def test_instance_refresh():
    """
    Test refreshing an instance from the database and updating the model.
    """
    user = User.objects.create(
        first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com"
    )

    class PydanticUser(PydanticDjangoModel):
        class Config:
            model = User
            include = ["id", "email", "profile"]

    pydantic_user = PydanticUser.get(id=user.id)

    assert not pydantic_user.dict()["profile"]
    assert pydantic_user.dict()["email"] == "jordan@eremieff.com"

    profile = Profile.objects.create(
        user=user, website="https://github.com/jordaneremieff", location="Australia"
    )
    user.email = "hello@example.com"
    user.save()

    pydantic_user.refresh()

    assert pydantic_user.dict()["profile"] == profile.pk
    assert pydantic_user.dict()["email"] == "hello@example.com"


@pytest.mark.django_db
def test_instance_delete():
    """
    Test deleting an instance and clearing the model.
    """
    user = User.objects.create(
        first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com"
    )

    class PydanticUser(PydanticDjangoModel):
        class Config:
            model = User

    pydantic_user = PydanticUser.get(id=user.id)
    assert pydantic_user.dict()["id"] == user.id
    pydantic_user.delete()
    assert not pydantic_user.dict()
