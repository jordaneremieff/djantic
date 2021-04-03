from inspect import isclass
from itertools import chain
from typing import Optional, Union, Any, List

from pydantic import BaseModel, create_model, validate_model, ConfigError
from pydantic.main import ModelMetaclass


import django
from django.utils.functional import Promise
from django.utils.encoding import force_str
from django.core.serializers.json import DjangoJSONEncoder

from .fields import ModelSchemaField


_is_base_model_class_defined = False


class ModelSchemaJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):  # pragma: nocover
        if isinstance(obj, Promise):
            return force_str(obj)
        return super().default(obj)


class ModelSchemaMetaclass(ModelMetaclass):
    def __new__(
        mcs: "ModelSchemaMetaclass",
        name: str,
        bases: tuple,
        namespace: dict,
    ):
        cls = super().__new__(mcs, name, bases, namespace)
        for base in reversed(bases):
            if (
                _is_base_model_class_defined
                and issubclass(base, ModelSchema)
                and base == ModelSchema
            ):

                config = namespace["Config"]
                include = getattr(config, "include", None)
                exclude = getattr(config, "exclude", None)

                if include and exclude:
                    raise ConfigError(
                        "Only one of 'include' or 'exclude' should be set in configuration."
                    )

                annotations = namespace.get("__annotations__", {})
                try:
                    fields = config.model._meta.get_fields()
                except AttributeError as exc:
                    raise ConfigError(
                        f"{exc} (Is `Config.model` a valid Django model class?)"
                    )

                field_values = {}
                _seen = set()

                for field in chain(fields, annotations.copy()):
                    field_name = getattr(
                        field, "name", getattr(field, "related_name", field)
                    )

                    if (
                        field_name in _seen
                        or (include and field_name not in include)
                        or (exclude and field_name in exclude)
                    ):
                        continue

                    _seen.add(field_name)

                    python_type = None
                    pydantic_field = None
                    if field_name in annotations and field_name in namespace:

                        python_type = annotations.pop(field_name)
                        pydantic_field = namespace[field_name]
                        if (
                            hasattr(pydantic_field, "default_factory")
                            and pydantic_field.default_factory
                        ):
                            pydantic_field = pydantic_field.default_factory()
                    elif field_name in annotations:
                        python_type = annotations.pop(field_name)
                        pydantic_field = (
                            None if Optional[python_type] == python_type else Ellipsis
                        )

                    else:
                        python_type, pydantic_field = ModelSchemaField(field)

                    field_values[field_name] = (python_type, pydantic_field)

                cls.__doc__ = namespace.get("__doc__", config.model.__doc__)
                cls.__fields__ = {}
                p_model = create_model(
                    name, __base__=cls, __module__=cls.__module__, **field_values
                )

                setattr(p_model, "instance", None)

                return p_model

        return cls


class ModelSchema(BaseModel, metaclass=ModelSchemaMetaclass):
    @classmethod
    def schema_json(
        cls,
        *,
        by_alias: bool = True,
        encoder_cls=ModelSchemaJSONEncoder,
        **dumps_kwargs: Any,
    ) -> str:

        return cls.__config__.json_dumps(
            cls.schema(by_alias=by_alias), cls=encoder_cls, **dumps_kwargs
        )

    @classmethod
    def get_fields(cls):
        if hasattr(cls.__config__, "include"):
            fields = cls.__config__.include
        elif hasattr(cls.__config__, "exclude"):
            fields = [
                field.name
                for field in cls.__config__.model._meta.get_fields()
                if field not in cls.__config__.exclude
            ]
        else:
            fields = [field.name for field in cls.__config__.model._meta.get_fields()]

        return fields

    @classmethod
    def _get_object_model(cls, obj_data):
        values, fields_set, validation_error = validate_model(cls, obj_data)
        if validation_error:  # pragma: nocover
            raise validation_error

        p_model = cls.__new__(cls)
        object.__setattr__(p_model, "__dict__", values)
        object.__setattr__(p_model, "__fields_set__", fields_set)

        return p_model

    @classmethod
    def from_django(
        cls: "ModelSchema",
        instance: Union[django.db.models.Model, django.db.models.QuerySet],
        many: bool = False,
        cache: bool = True,
    ) -> Union["ModelSchema", List["ModelSchema"]]:

        if not many:
            obj_data = {}

            annotations = cls.__annotations__
            fields = instance._meta.get_fields()
            for field in fields:
                model_cls = None
                model_cls_fields = None
                if (
                    field.name in annotations
                    and isclass(cls.__fields__[field.name].type_)
                    and issubclass(cls.__fields__[field.name].type_, ModelSchema)
                ):
                    model_cls = cls.__fields__[field.name].type_
                    model_cls_fields = model_cls.get_fields()

                if not field.concrete and field.auto_created:
                    accessor_name = field.get_accessor_name()
                    related_obj = getattr(instance, accessor_name, None)
                    if not related_obj:
                        related_obj_data = None
                    elif field.one_to_many:
                        related_qs = related_obj.all()

                        if model_cls:
                            related_obj_data = [
                                model_cls.construct(**obj_vals)
                                for obj_vals in related_qs.values(*model_cls_fields)
                            ]

                        else:
                            related_obj_data = list(related_obj.all().values("id"))

                    elif field.one_to_one:
                        if model_cls:
                            related_obj_data = model_cls.construct(
                                **{
                                    _field: getattr(related_obj, _field)
                                    for _field in model_cls.get_fields()
                                }
                            )
                        else:
                            related_obj_data = related_obj.pk
                    obj_data[accessor_name] = related_obj_data

                elif field.one_to_many or field.many_to_many:
                    related_qs = getattr(instance, field.name)
                    if model_cls:
                        related_fields = [
                            field
                            for field in model_cls_fields
                            if field != "content_object"
                        ]
                        related_obj_data = [
                            model_cls.construct(**obj_vals)
                            for obj_vals in related_qs.values(*related_fields)
                        ]
                    else:
                        related_obj_data = list(related_qs.values("pk"))

                    obj_data[field.name] = related_obj_data

                elif field.many_to_one:
                    related_obj = getattr(instance, field.name)
                    if model_cls:
                        related_obj_data = model_cls.from_django(related_obj).dict()
                    else:
                        related_obj_data = field.value_from_object(instance)
                    obj_data[field.name] = related_obj_data

                else:
                    obj_data[field.name] = field.value_from_object(instance)

            p_model = cls._get_object_model(obj_data)

            if cache:
                cls.instance = instance

            return p_model

        p_model_list = [
            cls.from_django(obj, cache=False, many=False) for obj in instance
        ]

        return p_model_list


_is_base_model_class_defined = True
