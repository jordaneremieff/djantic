# Usage

The main functionality this library intends to provide is a means to automatically generate Pydantic models based on Django ORM model definitions. Most of the Pydantic [model properties](https://pydantic-docs.helpmanual.io/usage/models/#model-properties) are expected to work with the generated model schemas.

In addition to this, the model schemas provide a `from_django` method for loading Django object instance data to be used with Pydantic's [model export](https://pydantic-docs.helpmanual.io/usage/exporting_models/) methods.

## Creating a model schema

The `ModelSchema` class can be used to generate a Pydantic model that maps to a Django model's fields automatically, and they also support customization using type annotations and field configurations.

Consider the following model definition for a user in Django:


```python
from django.db import models 

class User(models.Model):
    """
    A user of the application.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

```

A custom `ModelSchema` class could then be configured for this model:

```python
from djantic import ModelSchema
from myapp.models import User

class UserSchema(ModelSchema):
    class Config:
        model = User

```

Once defined, the `UserSchema` can be used to perform various functions on the underlying Django model object, such as generating JSON schemas or exporting serialized instance data.

### Basic schema usage

The `UserSchema` above can be used to generate a JSON schema using Pydantic's [schema](https://pydantic-docs.helpmanual.io/usage/schema/) method:

```python
print(UserSchema.schema())
```

Output:

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

By default, all of the fields in a Django model will be included in the model schema produced using the details of each field's configuration.

### Customizing the schema

By default, the docstrings and help text of the Django model definition is used to populate the various titles and descriptive text and constraints in the schema outputs. 

However, the model schema class itself can be used to override this behaviour:

```python
from pydantic import Field, constr
from djantic import ModelSchema
from myapp.models import User

class UserSchema(ModelSchema):
    """
    My custom model schema.
    """
    first_name: str = Field(
        None,
        title="The user's first name",
        description="This is the user's first name",
    )
    last_name: constr(strip_whitespace=True)

    class Config:
        model = User
        title = "My user schema"
```

Output:

```python
{
    "title": "My user schema",
    "description": "My custom model schema.",
    "type": "object",
    "properties": {
        "id": {"title": "Id", "description": "id", "type": "integer"},
        "first_name": {
            "title": "The user's first name",
            "description": "This is the user's first name",
            "type": "string",
        },
        "last_name": {"title": "Last Name", "type": "string"},
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
    "required": ["first_name", "last_name", "email", "created_at", "updated_at"],
}
```

Model schemas also support using standard Python type annotations and field inclusion/exclusion configurations to customize the schemas beyond the definitions inferred from the Django model.

For example, the `last_name` field in the Django model is considered optional because of the `null=True` and `blank=True` parameters in the field definition, and the `first_name` field is required. 

These details can be modified by defining specific field rules using type annotations, and the schema fields can limited using the `include` (or `exclude`) configuration setting:

```python
class UserSchema(ModelSchema):
    first_name: Optional[str]
    last_name: str

    class Config:
        model = User
        include = ["first_name", "last_name"]

```

Output:

```python
{
    "description": "A user of the application.",
    "properties": {
        "first_name": {"title": "First Name", "type": "string"},
        "last_name": {"title": "Last Name", "type": "string"},
    },
    "required": ["last_name"],
    "title": "UserSchema",
    "type": "object",
}
```

## Handling related objects

Database relations (many to one, one to one, many to many) are also supported in the schema definition. Generic relations are also supported, but not extensively tested.

Consider the initial `User` model in [creating a schema](/schemas/#creating-a-schema), but with the addition of a `Profile` model containing a one to one relationship:

```python
from django.db import models 

class User(models.Model):
    """
    A user of the application.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Profile(models.Model):
    """
    A user's profile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    website = models.URLField(default="", blank=True)
    location = models.CharField(max_length=100, default="", blank=True)

```

The new `Profile` relationship would be available to the generated model schema:

```python
from djantic import ModelSchema
from myapp.models import User

class UserSchema(ModelSchema):
    class Config:
        model = User
        include = ["id", "email", "profile"]

print(UserSchema.schema())
```

Output:

```python
{
    "title": "UserSchema",
    "description": "A user of the application.",
    "type": "object",
    "properties": {
        "profile": {"title": "Profile", "description": "id", "type": "integer"},
        "id": {"title": "Id", "description": "id", "type": "integer"},
        "email": {
            "title": "Email",
            "description": "email",
            "maxLength": 254,
            "type": "string",
        },
    },
    "required": ["email"],
}
```

***Note***: The initial `UserSchema` example in [creating a schema](/schemas/#creating-a-schema) could be used without modification. The `include` list here is used to reduce the example output and is not required for relations support.

#### Related schema models

The auto-generated `profile` definition can be expanded using an additional model schema set on the user schema:


```python
class ProfileSchema(ModelSchema):
    class Config:
        model = Profile

class UserSchema(ModelSchema):
    profile: ProfileSchema

    class Config:
        model = User
        include = ["id", "profile"]

print(UserSchema.schema())
```

Output:

```python
{
    "title": "UserSchema",
    "description": "A user of the application.",
    "type": "object",
    "properties": {
        "profile": {"$ref": "#/definitions/ProfileSchema"},
        "id": {"title": "Id", "description": "id", "type": "integer"},
    },
    "required": ["profile"],
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

```

These schema relationships also work in reverse:

```python
class UserSchema(ModelSchema):
    class Config:
        model = User
        include = ["id", "email"]

class ProfileSchemaWithUser(ModelSchema):
    user: UserSchema

    class Config:
        model = Profile
        include = ["id", "user"]

print(ProfileSchemaWithUser.schema())
```

Output:

```python
{
    "title": "ProfileSchemaWithUser",
    "description": "A user's profile.",
    "type": "object",
    "properties": {
        "id": {"title": "Id", "description": "id", "type": "integer"},
        "user": {"$ref": "#/definitions/UserSchema"},
    },
    "required": ["user"],
    "definitions": {
        "UserSchema": {
            "title": "UserSchema",
            "description": "A user of the application.",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "description": "id", "type": "integer"},
                "email": {
                    "title": "Email",
                    "description": "email",
                    "maxLength": 254,
                    "type": "string",
                },
            },
            "required": ["email"],
        }
    },
}
```

The above behaviour works similarly to one to many and many to many relations. You can see more examples in the [tests](https://github.com/jordaneremieff/pydantic-django/blob/main/tests/test_relations.py).

## Exporting model data

Model schemas support a `from_django` method that allows loading Django model instances for export using the generated schema. This method is similar to Pydantic's builtin [from_orm](https://pydantic-docs.helpmanual.io/usage/models/#orm-mode-aka-arbitrary-class-instances), but very specific to Django's ORM.

It is intended to provide support for all of Pydantic's [model export](https://pydantic-docs.helpmanual.io/usage/exporting_models/) methods.


### Basic export usage

Create one or more Django model instances to be used when populating the model schema:

```python
user = User.objects.create(
    first_name="Jordan", last_name="Eremieff", email="jordan@eremieff.com"
)
profile = Profile.objects.create(user=user, website="https://github.com", location="AU")
```

Then use the `from_django` method to load this object:

```python
from djantic import ModelSchema
from myapp.models import User

class ProfileSchema(ModelSchema):
    class Config:
        model = Profile
        exclude = ["user"]

class UserSchema(ModelSchema):
    profile: ProfileSchema

    class Config:
        model = User

user = User.objects.get(id=1)
obj = UserSchema.from_django(user)
```

Now that the instance is loaded, it can be used with the various export methods to produce different outputs according to the schema definition. These outputs will be validated against the schema rules:

#### model.dict()

```python
print(obj.dict())
```

Output:

```python
    {
    "profile": {"id": 1, "website": "https://github.com", "location": "AU"},
    "id": 1,
    "first_name": "Jordan",
    "last_name": "Eremieff",
    "email": "jordan@eremieff.com",
    "created_at": datetime.datetime(2021, 4, 4, 8, 47, 39, 567410, tzinfo=<UTC>),
    "updated_at": datetime.datetime(2021, 4, 4, 8, 47, 39, 567455, tzinfo=<UTC>)
}
```

#### model.json()

```python
print(obj.json(indent=2))
```


Output:

```json
{
  "profile": {
    "id": 1,
    "website": "https://github.com",
    "location": "AU"
  },
  "id": 1,
  "first_name": "Jordan",
  "last_name": "Eremieff",
  "email": "jordan@eremieff.com",
  "created_at": "2021-04-04T08:47:39.567410+00:00",
  "updated_at": "2021-04-04T08:47:39.567455+00:00"
}
```

***Note***: There is more here that should be documented (and tested).
