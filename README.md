# Pydantic-Django

**Documentation**: https://jordaneremieff.github.io/pydantic-django/

[Pydantic](https://pydantic-docs.helpmanual.io/) model support for [Django](https://www.djangoproject.com/) ORM.

**Requirements**: Python 3.7+, Django 2+

**Status**: this project should be considered a work-in-progress. It should be okay to use, but no specific version support is guaranteed yet and expected outputs may change as it continues to be developed.

Please use the issues [tracker](https://github.com/jordaneremieff/pydantic-django/issues) for any bug reports.

## Quickstart

Install using pip:

```shell
pip install pydantic-django
```

An example of basic [schema](https://pydantic-docs.helpmanual.io/usage/schema/) usage:

```python
class UserSchema(ModelSchema):
    class Config:
        model = User
        
UserSchema.schema()
```

The schema call above would return something like this:

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

Use the `from_django` method to populate the models with values:

```python
user = User.objects.create(
    first_name="Jordan", 
    last_name="Eremieff", 
    email="jordan@eremieff.com"
)

user_schema = UserSchema.from_django(user)
```

The object values can be validated and serialized using the Pydantic [export](https://pydantic-docs.helpmanual.io/usage/exporting_models/) methods.

```python
user_json = user_schema.json()
```

To produce a result such as:

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
