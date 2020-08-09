# Pydantic-Django

An attempt to implement a [Pydantic](https://pydantic-docs.helpmanual.io/) model interface for [Django](https://www.djangoproject.com/) ORM. The goal of this project is to support all of Pydantic's features to provide as many (useful) conveniences for Django models as possible.

**Important**: this project should be considered an ***experimental*** work-in-progress. The current API design and behaviour is not finalised, specific version support is not yet determined, and there is still a lot of things to test yet.

Also, I typically haven't used metaclasses/classes like this previously, so there may be some details in the implementation to refine. 

Seems to work okay so far. :)

## Installation

```
pip install pydantic-django
```

## Usage

**Requirements**: Python 3.7+, Django 3

An example of basic serialization case:

```python
from users.models import User
from pydantic_django import PydanticDjangoModel

class PydanticUser(PydanticDjangoModel):
    """An example user schema."""

    class Config:
        model = User

schema = PydanticUser.schema()
```

A schema call would return something like this:

```python
{
    'description': 'An example user schema.',
    'properties': {
        'created_at': {'format': 'date-time', 'title': 'Created At', 'type': 'string'},
        'email': {'maxLength': 254, 'title': 'Email', 'type': 'string'},
        'first_name': {'maxLength': 50, 'title': 'First Name', 'type': 'string'},
        'groups': {'items': {'type': 'integer'}, 'title': 'Id', 'type': 'array'},
        'id': {'title': 'Id', 'type': 'integer'},
        'last_name': {'maxLength': 50, 'title': 'Last Name', 'type': 'string'},
        'messages': {'items': {'type': 'integer'}, 'title': 'Id', 'type': 'array'},
        'profile': {'title': 'Id', 'type': 'integer'},
        'updated_at': {'format': 'date-time', 'title': 'Updated At', 'type': 'string'},
    },
    'required': ['first_name', 'email', 'created_at', 'updated_at', 'groups'],
    'title': 'PydanticUser',
    'type': 'object',
}
```

There are a few ways to populate the models with values, the first is using the `from_django` method:

```python
user = User.objects.create(
    first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com"
)

pydantic_user = PydanticUser.from_django(user)
```

Alternatively, the Pydantic model can be used to create a new object:

```python
pydantic_user = PydanticUser.create(first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com")
```

Or retrieve an existing one:

```python
pydantic_user = PydanticUser.get(id=user.id)
```

The object in each case can be validated and export the values in the same way:

```python
user_json = pydantic_user.json()
```

To produce a result such as:

```json
{"profile": null, "messages": [], "id": 1, "first_name": "Jordan", "last_name": "Eremieff", "email": "jordan@eremieff.com", "created_at": "2020-08-09T13:45:04.395787+00:00",
"updated_at": "2020-08-09T13:45:04.395828+00:00", "groups": []}
```

It can do a bit more than this, but you'll have to check out the testing application and test cases as a reference for now.

## Roadmap

- [x] Automatic schema generation from Django models
- [x] Basic queryset interface for CRUD operations
- [x] Include & exclude field filtering
- [x] Default factory support
- [x] Support basic field types
- [x] Sub-model support for forward and reverse relations
- [ ] Postgres field types
- [ ] Support for multi-object querysets
- [ ] More comprehensive support for Django features
- [ ] HTML schema generation
- [ ] Create a complete application example
- [ ] Look into performance & benchmarking
- [ ] More test coverage & type annotations
