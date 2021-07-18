# Djantic

[![PyPI version](https://badge.fury.io/py/djantic.svg)](https://badge.fury.io/py/djantic)

**Documentation**: https://jordaneremieff.github.io/djantic/

**Requirements**: Python 3.7+, Django 3.0+

[Pydantic](https://pydantic-docs.helpmanual.io/) models for [Django](https://www.djangoproject.com/).

This project should be considered a work-in-progress. It should be okay to use, but no specific version support has been determined ([#16](https://github.com/jordaneremieff/djantic/issues/16)) and the *default* model generation behaviour may change across releases.

Please use the issues [tracker](https://github.com/jordaneremieff/djantic/issues) to report any bugs, or if something seems incorrect.

## Quickstart

Install using pip:

```shell
pip install djantic
```

### Generating schemas from models

Configure a custom `ModelSchema` class for a Django model to generate a Pydantic model. This will allow using the Django model information with Pydantic model methods:

```python
from users.models import User
from djantic import ModelSchema

class UserSchema(ModelSchema):
    class Config:
        model = User
        
print(UserSchema.schema())

```

**Output:**

```python
{
        "title": "UserSchema",
        "description": "A user of the application.",
        "type": "object",
        "properties": {
            "profile": {"title": "Profile", "description": "None", "type": "integer"},
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
```

See https://pydantic-docs.helpmanual.io/usage/models/ for more.

### Loading and exporting model data

Use the `from_django` method on a model schema class to load a Django model instance into a schema class:


```python
user = User.objects.create(
    first_name="Jordan", 
    last_name="Eremieff", 
    email="jordan@eremieff.com"
)

user_schema = UserSchema.from_django(user)
print(user_schema.json(indent=2))

```

**Output:**

```json
{
    "profile": null,
    "id": 1,
    "first_name": "Jordan",
    "last_name": "Eremieff",
    "email": "jordan@eremieff.com",
    "created_at": "2020-08-15T16:50:30.606345+00:00",
    "updated_at": "2020-08-15T16:50:30.606452+00:00"
}
```

See https://pydantic-docs.helpmanual.io/usage/exporting_models/ for more.