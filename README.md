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

**Requirements**: Python 3.7+, Django 2+

An example of basic [schema](https://pydantic-docs.helpmanual.io/usage/schema/) usage:

```python
class UserSchema(PydanticDjangoModel):
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
        "profile": {"title": "Profile", "type": "integer"},
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
    "required": ["first_name", "email", "created_at", "updated_at"],
}
```

There are a few ways to populate the models with values, the first is using the `from_django` method:

```python
user = User.objects.create(
    first_name="Jordan", 
    last_name="Eremieff", 
    email="jordan@eremieff.com"
)

user_schema = UserSchema.from_django(user)
```

Alternatively, the Pydantic model can be used to create a new object:

```python
user_schema = UserSchema.create(
    first_name="Jordan", 
    last_name="Eremieff", 
    email="jordan@eremieff.com"
)
```

Or retrieve an existing one:

```python
user_schema = UserSchema.get(id=user.id)
```

The object in each case can be validated and [export](https://pydantic-docs.helpmanual.io/usage/exporting_models/) the values in the same way:

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

It can also use standard Python type annotations in conjunction with the fields retrieved automatically from the database, and the configuration class supports `exclude` and `include` options:

```python
class UserSchema(PydanticDjangoModel):
    first_name: Optional[str]
    last_name: str

    class Config:
        model = User
        include = ["first_name", "last_name"]
```

In this example, the first name and last name annotations override the fields that would normally be picked up from the Django model automatically, and the `include` list filters out the other fields from the schema definition.

The `first_name` field here is required in the database and the `last_name` field is optional, but using the type annotations this can be determined for the specific schema:

```python
{
    'description': 'A user of the application.',
    'properties': {
            'first_name': {'title': 'First Name', 'type': 'string'},
            'last_name': {'title': 'Last Name', 'type': 'string'}
            },
    'required': ['last_name'],
    'title': 'UserSchema',
    'type': 'object'
}
```
        
It can do a bit more than this, but you'll have to check out the testing application and test cases as a reference for now.

## Roadmap

- [x] Automatic schema generation from Django models
- [x] Basic queryset interface for CRUD operations
- [x] Include & exclude field filtering
- [x] Default factory support
- [x] Support basic field types
- [x] Sub-model support for forward and reverse relations
- [x] JSON field types
- [x] Support for multi-object querysets
- [x] Support generic relations
- [ ] Postgres field types
- [ ] Look into custom validators and configurations
- [ ] More comprehensive support for Django features
- [ ] HTML schema generation
- [ ] Create a complete application example
- [ ] Look into performance & benchmarking
- [ ] More test coverage & type annotations
