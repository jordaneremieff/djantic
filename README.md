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

### Use multiple level relations

Djantic supports multiple level relations. Given the following models:

```python
class OrderUser(models.Model):
    email = models.EmailField(unique=True)


class OrderUserProfile(models.Model):
    address = models.CharField(max_length=255)
    user = models.OneToOneField(OrderUser, on_delete=models.CASCADE, related_name='profile')


class Order(models.Model):
    total_price = models.DecimalField(max_digits=8, decimal_places=5, default=0)
    user = models.ForeignKey(
        OrderUser, on_delete=models.CASCADE, related_name="orders"
    )


class OrderItem(models.Model):
    price = models.DecimalField(max_digits=8, decimal_places=5, default=0)
    quantity = models.IntegerField(default=0)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )


class OrderItemDetail(models.Model):
    name = models.CharField(max_length=30)
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="details"
    )
```

Inverse ForeignKey relation (or M2M relation) type is a list of the Schema of this related object.

OneToOne relation type is the Schema of this related object.

```python
class OrderItemDetailSchema(ModelSchema):
    class Config:
        model = OrderItemDetail

class OrderItemSchema(ModelSchema):
    details: List[OrderItemDetailSchema]

    class Config:
        model = OrderItem

class OrderSchema(ModelSchema):
    items: List[OrderItemSchema]

    class Config:
        model = Order

class OrderUserProfileSchema(ModelSchema):
    class Config:
        model = OrderUserProfile

class OrderUserSchema(ModelSchema):
    orders: List[OrderSchema]
    profile: OrderUserProfileSchema
```

**Calling:**

```python
user = OrderUser.objects.first()
print(OrderUserSchema.from_orm(user).json(ident=4))
```

**Output:**
```json
{
    "profile": {
        "id": 1,
        "address": "",
        "user": 1
    },
    "orders": [
        {
            "items": [
                {
                    "details": [
                        {
                            "id": 1,
                            "name": "",
                            "order_item": 1
                        }
                    ],
                    "id": 1,
                    "price": 0.0,
                    "quantity": 0,
                    "order": 1
                }
            ],
            "id": 1,
            "total_price": 0.0,
            "user": 1
        }
    ],
    "id": 1,
    "email": ""
}
```