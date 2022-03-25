
from decimal import Decimal
from typing import List

import pytest
from testapp.order import Order, OrderItem, OrderItemDetail, OrderUser, OrderUserFactory, OrderUserProfile

from djantic import ModelSchema


@pytest.mark.django_db
def test_multiple_level_relations():
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

        class Config:
            model = OrderUser

    user = OrderUserFactory.create()

    assert OrderUserSchema.from_django(user).dict() == {
        'id': 1,
        'first_name': '',
        'last_name': None,
        'email': '',
        'profile': {
            'id': 1,
            'address': '',
            'user': 1
        },
        'orders': [
            {
                'id': 1,
                'total_price': Decimal('0.00000'),
                'shipping_address': '',
                'user': 1,
                'items': [
                    {
                        'id': 1,
                        'name': '',
                        'price': Decimal('0.00000'),
                        'quantity': 0,
                        'order': 1,
                        'details': [
                            {
                                'id': 1,
                                'name': '',
                                'value': 0,
                                'quantity': 0,
                                'order_item': 1
                            },
                            {
                                'id': 2,
                                'name': '',
                                'value': 0,
                                'quantity': 0,
                                'order_item': 1
                            }
                        ]
                    },
                    {
                        'details': [
                            {
                                'id': 3,
                                'name': '',
                                'value': 0,
                                'quantity': 0,
                                'order_item': 2
                            },
                            {
                                'id': 4,
                                'name': '',
                                'value': 0,
                                'quantity': 0,
                                'order_item': 2
                            }
                        ],
                        'id': 2,
                        'name': '',
                        'price': Decimal('0.00000'),
                        'quantity': 0,
                        'order': 1
                    }
                ],

            },
            {
                'id': 2,
                'total_price': Decimal('0.00000'),
                'shipping_address': '',
                'user': 1,
                'items': [
                    {
                        'id': 3,
                        'name': '',
                        'price': Decimal('0.00000'),
                        'quantity': 0,
                        'order': 2,
                        'details': [
                            {
                                'id': 5,
                                'name': '',
                                'value': 0,
                                'quantity': 0,
                                'order_item': 3},
                            {
                                'id': 6,
                                'name': '',
                                'value': 0,
                                'quantity': 0,
                                'order_item': 3}
                        ]
                    },
                    {
                        'id': 4,
                        'name': '',
                        'price': Decimal('0.00000'),
                        'quantity': 0,
                        'order': 2,
                        'details': [
                            {
                                'id': 7,
                                'name': '',
                                'value': 0,
                                'quantity': 0,
                                'order_item': 4},
                            {
                                'id': 8,
                                'name': '',
                                'value': 0,
                                'quantity': 0,
                                'order_item': 4}]
                    }
                ]
            }
        ]
    }

    assert OrderUserSchema.schema() == {
        "title": "OrderUserSchema",
        "description": "OrderUser(id, first_name, last_name, email)",
        "type": "object",
        "properties": {
            "profile": {
                "$ref": "#/definitions/OrderUserProfileSchema"
            },
            "orders": {
                "title": "Orders",
                "type": "array",
                "items": {
                    "$ref": "#/definitions/OrderSchema"
                }
            },
            "id": {
                "title": "Id",
                "description": "id",
                "type": "integer"
            },
            "first_name": {
                "title": "First Name",
                "description": "first_name",
                "maxLength": 50,
                "type": "string"
            },
            "last_name": {
                "title": "Last Name",
                "description": "last_name",
                "maxLength": 50,
                "type": "string"
            },
            "email": {
                "title": "Email",
                "description": "email",
                "maxLength": 254,
                "type": "string"
            }
        },
        "required": [
            "profile",
            "orders",
            "first_name",
            "email"
        ],
        "definitions": {
            "OrderUserProfileSchema": {
                "title": "OrderUserProfileSchema",
                "description": "OrderUserProfile(id, address, user)",
                "type": "object",
                "properties": {
                    "id": {
                        "title": "Id",
                        "description": "id",
                        "type": "integer"
                    },
                    "address": {
                        "title": "Address",
                        "description": "address",
                        "maxLength": 255,
                        "type": "string"
                    },
                    "user": {
                        "title": "User",
                        "description": "id",
                        "type": "integer"
                    }
                },
                "required": [
                    "address",
                    "user"
                ]
            },
            "OrderItemDetailSchema": {
                "title": "OrderItemDetailSchema",
                "description": "OrderItemDetail(id, name, value, quantity, order_item)",
                "type": "object",
                "properties": {
                    "id": {
                        "title": "Id",
                        "description": "id",
                        "type": "integer"
                    },
                    "name": {
                        "title": "Name",
                        "description": "name",
                        "maxLength": 30,
                        "type": "string"
                    },
                    "value": {
                        "title": "Value",
                        "description": "value",
                        "default": 0,
                        "type": "integer"
                    },
                    "quantity": {
                        "title": "Quantity",
                        "description": "quantity",
                        "default": 0,
                        "type": "integer"
                    },
                    "order_item": {
                        "title": "Order Item",
                        "description": "id",
                        "type": "integer"
                    }
                },
                "required": [
                    "name",
                    "order_item"
                ]
            },
            "OrderItemSchema": {
                "title": "OrderItemSchema",
                "description": "OrderItem(id, name, price, quantity, order)",
                "type": "object",
                "properties": {
                    "details": {
                        "title": "Details",
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/OrderItemDetailSchema"
                        }
                    },
                    "id": {
                        "title": "Id",
                        "description": "id",
                        "type": "integer"
                    },
                    "name": {
                        "title": "Name",
                        "description": "name",
                        "maxLength": 30,
                        "type": "string"
                    },
                    "price": {
                        "title": "Price",
                        "description": "price",
                        "default": 0,
                        "type": "number"
                    },
                    "quantity": {
                        "title": "Quantity",
                        "description": "quantity",
                        "default": 0,
                        "type": "integer"
                    },
                    "order": {
                        "title": "Order",
                        "description": "id",
                        "type": "integer"
                    }
                },
                "required": [
                    "details",
                    "name",
                    "order"
                ]
            },
            "OrderSchema": {
                "title": "OrderSchema",
                "description": "Order(id, total_price, shipping_address, user)",
                "type": "object",
                "properties": {
                    "items": {
                        "title": "Items",
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/OrderItemSchema"
                        }
                    },
                    "id": {
                        "title": "Id",
                        "description": "id",
                        "type": "integer"
                    },
                    "total_price": {
                        "title": "Total Price",
                        "description": "total_price",
                        "default": 0,
                        "type": "number"
                    },
                    "shipping_address": {
                        "title": "Shipping Address",
                        "description": "shipping_address",
                        "maxLength": 255,
                        "type": "string"
                    },
                    "user": {
                        "title": "User",
                        "description": "id",
                        "type": "integer"
                    }
                },
                "required": [
                    "items",
                    "shipping_address",
                    "user"
                ]
            }
        }
    }
