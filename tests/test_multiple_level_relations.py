from decimal import Decimal
from typing import List, Optional

import pytest
from pydantic import validator
from testapp.order import (
    Order,
    OrderItem,
    OrderItemDetail,
    OrderUser,
    OrderUserFactory,
    OrderUserProfile,
)

from pydantic import ConfigDict
from djantic import ModelSchema


@pytest.mark.django_db
def test_multiple_level_relations():
    class OrderItemDetailSchema(ModelSchema):
        model_config = ConfigDict(model=OrderItemDetail)

    class OrderItemSchema(ModelSchema):
        details: List[OrderItemDetailSchema]
        model_config = ConfigDict(model=OrderItem)

    class OrderSchema(ModelSchema):
        items: List[OrderItemSchema]
        model_config = ConfigDict(model=Order)

    class OrderUserProfileSchema(ModelSchema):
        model_config = ConfigDict(model=OrderUserProfile)

    class OrderUserSchema(ModelSchema):
        orders: List[OrderSchema]
        profile: OrderUserProfileSchema
        user_cache: Optional[dict]
        model_config = ConfigDict(
            model=OrderUser,
            include=(
                "id",
                "first_name",
                "last_name",
                "email",
                "profile",
                "orders",
                "user_cache",
            ),
        )

        @validator("user_cache", pre=True, always=True)
        def get_user_cache(cls, _):
            return {"has_order": True}

    user = OrderUserFactory.create()

    assert OrderUserSchema.from_django(user).dict() == {
        "profile": {"id": 1, "address": "", "user": 1},
        "orders": [
            {
                "items": [
                    {
                        "details": [
                            {
                                "id": 1,
                                "name": "",
                                "value": 0,
                                "quantity": 0,
                                "order_item": 1,
                            },
                            {
                                "id": 2,
                                "name": "",
                                "value": 0,
                                "quantity": 0,
                                "order_item": 1,
                            },
                        ],
                        "id": 1,
                        "name": "",
                        "price": Decimal("0.00000"),
                        "quantity": 0,
                        "order": 1,
                    },
                    {
                        "details": [
                            {
                                "id": 3,
                                "name": "",
                                "value": 0,
                                "quantity": 0,
                                "order_item": 2,
                            },
                            {
                                "id": 4,
                                "name": "",
                                "value": 0,
                                "quantity": 0,
                                "order_item": 2,
                            },
                        ],
                        "id": 2,
                        "name": "",
                        "price": Decimal("0.00000"),
                        "quantity": 0,
                        "order": 1,
                    },
                ],
                "id": 1,
                "total_price": Decimal("0.00000"),
                "shipping_address": "",
                "user": 1,
            },
            {
                "items": [
                    {
                        "details": [
                            {
                                "id": 5,
                                "name": "",
                                "value": 0,
                                "quantity": 0,
                                "order_item": 3,
                            },
                            {
                                "id": 6,
                                "name": "",
                                "value": 0,
                                "quantity": 0,
                                "order_item": 3,
                            },
                        ],
                        "id": 3,
                        "name": "",
                        "price": Decimal("0.00000"),
                        "quantity": 0,
                        "order": 2,
                    },
                    {
                        "details": [
                            {
                                "id": 7,
                                "name": "",
                                "value": 0,
                                "quantity": 0,
                                "order_item": 4,
                            },
                            {
                                "id": 8,
                                "name": "",
                                "value": 0,
                                "quantity": 0,
                                "order_item": 4,
                            },
                        ],
                        "id": 4,
                        "name": "",
                        "price": Decimal("0.00000"),
                        "quantity": 0,
                        "order": 2,
                    },
                ],
                "id": 2,
                "total_price": Decimal("0.00000"),
                "shipping_address": "",
                "user": 1,
            },
        ],
        "id": 1,
        "first_name": "",
        "last_name": None,
        "email": "",
        "user_cache": {"has_order": True},
    }

    assert OrderUserSchema.model_json_schema() == {
        "$defs": {
            "OrderItemDetailSchema": {
                "description": "OrderItemDetail(id, name, value, quantity, order_item)",
                "properties": {
                    "id": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "description": "id",
                        "title": "Id",
                    },
                    "name": {
                        "description": "name",
                        "maxLength": 30,
                        "title": "Name",
                        "type": "string",
                    },
                    "value": {
                        "default": 0,
                        "description": "value",
                        "title": "Value",
                        "type": "integer",
                    },
                    "quantity": {
                        "default": 0,
                        "description": "quantity",
                        "title": "Quantity",
                        "type": "integer",
                    },
                    "order_item": {
                        "description": "id",
                        "title": "Order Item",
                        "type": "integer",
                    },
                },
                "required": ["name", "order_item"],
                "title": "OrderItemDetailSchema",
                "type": "object",
            },
            "OrderItemSchema": {
                "description": "OrderItem(id, name, price, quantity, order)",
                "properties": {
                    "details": {
                        "items": {"$ref": "#/$defs/OrderItemDetailSchema"},
                        "title": "Details",
                        "type": "array",
                    },
                    "id": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "description": "id",
                        "title": "Id",
                    },
                    "name": {
                        "description": "name",
                        "maxLength": 30,
                        "title": "Name",
                        "type": "string",
                    },
                    "price": {
                        "anyOf": [{"type": "number"}, {"type": "string"}],
                        "default": 0,
                        "description": "price",
                        "title": "Price",
                    },
                    "quantity": {
                        "default": 0,
                        "description": "quantity",
                        "title": "Quantity",
                        "type": "integer",
                    },
                    "order": {"description": "id", "title": "Order", "type": "integer"},
                },
                "required": ["details", "name", "order"],
                "title": "OrderItemSchema",
                "type": "object",
            },
            "OrderSchema": {
                "description": "Order(id, total_price, shipping_address, user)",
                "properties": {
                    "items": {
                        "items": {"$ref": "#/$defs/OrderItemSchema"},
                        "title": "Items",
                        "type": "array",
                    },
                    "id": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "description": "id",
                        "title": "Id",
                    },
                    "total_price": {
                        "anyOf": [{"type": "number"}, {"type": "string"}],
                        "default": 0,
                        "description": "total_price",
                        "title": "Total Price",
                    },
                    "shipping_address": {
                        "description": "shipping_address",
                        "maxLength": 255,
                        "title": "Shipping Address",
                        "type": "string",
                    },
                    "user": {"description": "id", "title": "User", "type": "integer"},
                },
                "required": ["items", "shipping_address", "user"],
                "title": "OrderSchema",
                "type": "object",
            },
            "OrderUserProfileSchema": {
                "description": "OrderUserProfile(id, address, user)",
                "properties": {
                    "id": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "description": "id",
                        "title": "Id",
                    },
                    "address": {
                        "description": "address",
                        "maxLength": 255,
                        "title": "Address",
                        "type": "string",
                    },
                    "user": {"description": "id", "title": "User", "type": "integer"},
                },
                "required": ["address", "user"],
                "title": "OrderUserProfileSchema",
                "type": "object",
            },
        },
        "description": "OrderUser(id, first_name, last_name, email)",
        "properties": {
            "profile": {"$ref": "#/$defs/OrderUserProfileSchema"},
            "orders": {
                "items": {"$ref": "#/$defs/OrderSchema"},
                "title": "Orders",
                "type": "array",
            },
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "id",
                "title": "Id",
            },
            "first_name": {
                "description": "first_name",
                "maxLength": 50,
                "title": "First Name",
                "type": "string",
            },
            "last_name": {
                "anyOf": [{"maxLength": 50, "type": "string"}, {"type": "null"}],
                "default": None,
                "description": "last_name",
                "title": "Last Name",
            },
            "email": {
                "description": "email",
                "maxLength": 254,
                "title": "Email",
                "type": "string",
            },
            "user_cache": {
                "anyOf": [{"type": "object"}, {"type": "null"}],
                "default": None,
                "title": "User Cache",
            },
        },
        "required": ["profile", "orders", "first_name", "email"],
        "title": "OrderUserSchema",
        "type": "object",
    }
