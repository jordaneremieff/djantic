<h1 style="text-align: center;">
    Djantic
</h1>
<p style="text-align: center;">
    <em><a href="https://pydantic-docs.helpmanual.io/">Pydantic</a> model support for <a href="https://www.djangoproject.com/"> Django</a></em>
</p>
<p style="text-align: center;">
    <a href="https://github.com/jordaneremieff/djantic/actions/workflows/test.yml">
    <img src="https://img.shields.io/github/workflow/status/jordaneremieff/djantic/Test/main" alt="GitHub Workflow Status (Test)" >
    </a>
    <a href="https://pypi.org/project/djantic" target="_blank">
        <img src="https://img.shields.io/pypi/v/djantic" alt="PyPi package">
    </a>
    <a href="https://pypi.org/project/djantic" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/djantic" alt="Supported Python versions">
    </a>
    <a href="https://pypi.org/project/djantic" target="_blank">
        <img src="https://img.shields.io/pypi/djversions/djantic?label=django" alt="Supported Django versions">
    </a>
</p>

---

**Documentation**: https://jordaneremieff.github.io/djantic/

---

Djantic is a library that provides a configurable utility class for automatically creating a Pydantic model instance for any Django model class. It is intended to support all of the underlying Pydantic model functionality such as JSON schema generation and introduces custom behaviour for exporting Django model instance data.

## Quickstart

Install using pip:

```shell
pip install djantic
```

Create a model schema:

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

### Loading and exporting model instances

Use the `from_orm` method on the model schema to load a Django model instance for <a href="https://pydantic-docs.helpmanual.io/usage/exporting_models/">export</a>:

```python
user = User.objects.create(
    first_name="Jordan", 
    last_name="Eremieff", 
    email="jordan@eremieff.com"
)

user_schema = UserSchema.from_orm(user)
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

### Using multiple level relations

Djantic supports multiple level relations. This includes foreign keys, many-to-many, and one-to-one relationships.

Consider the following example Django model and Djantic model schema definitions for a number of related database records:

```python
# models.py
from django.db import models

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

```python
# schemas.py
from djantic import ModelSchema

from orders.models import OrderItemDetail, OrderItem, Order, OrderUserProfile


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

Now let's assume you're interested in exporting the order and profile information for a particular user into a JSON format that contains the details accross all of the related item objects:

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

The model schema definitions are composable and support customization of the output according to the auto-generated fields and any additional annotations.

### Including and excluding fields

The fields exposed in the model instance may be configured using two options: `include` and `exclude`. These represent iterables that should contain a list of field name strings. Only one of these options may be set at the same time, and if neither are set then the default behaviour is to include all of the fields from the Django model.

For example, to include all of the fields from a user model <i>except</i> a field named `email_address`, you would use the `exclude` option:

```python
class UserSchema(ModelSchema):
    class Config:
        exclude = ["email_address"]
```

In addition to this, you may also limit the fields to <i>only</i> include annotations from the model schema class by setting the `include` option to a special string value: `"__annotations__"`.

```python
class ProfileSchema(ModelSchema):
        website: str

        class Config:
            model = Profile
            include = "__annotations__"

    assert ProfileSchema.schema() == {
        "title": "ProfileSchema",
        "description": "A user's profile.",
        "type": "object",
        "properties": {
            "website": {
                "title": "Website",
                "type": "string"
            }
        },
        "required": [
            "website"
        ]
    }
```
