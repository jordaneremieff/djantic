from functools import reduce
from itertools import chain
from typing import Any, Dict, List, Optional, no_type_check

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Manager, Model
from django.db.models.fields.files import ImageFieldFile
from django.db.models.fields.reverse_related import (ForeignObjectRel,
                                                     OneToOneRel)
from django.utils.encoding import force_str
from django.utils.functional import Promise
from pydantic import BaseModel, ConfigError, create_model
from pydantic.main import ModelMetaclass
from pydantic.utils import GetterDict

from .fields import ModelSchemaField

_is_base_model_class_defined = False


class ModelSchemaJSONEncoder(DjangoJSONEncoder):
    @no_type_check
    def default(self, obj):  # pragma: nocover
        if isinstance(obj, Promise):
            return force_str(obj)

        return super().default(obj)


class ModelSchemaMetaclass(ModelMetaclass):
    @no_type_check
    def __new__(
        mcs,
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

                try:
                    config = namespace["Config"]
                except KeyError as exc:
                    raise ConfigError(
                        f"{exc} (Is `Config` class defined?)"
                    )
                    
                include = getattr(config, "include", None)
                exclude = getattr(config, "exclude", None)

                if include and exclude:
                    raise ConfigError(
                        "Only one of 'include' or 'exclude' should be set in "
                        "configuration."
                    )

                annotations = namespace.get("__annotations__", {})

                try:
                    fields = config.model._meta.get_fields()
                except AttributeError as exc:
                    raise ConfigError(
                        f"{exc} (Is `Config.model` a valid Django model class?)"
                    )

                if include is None and exclude is None:
                    cls.__config__.include = [f.name for f in fields]

                field_values = {}
                _seen = set()

                for field in chain(fields, annotations.copy()):
                    if issubclass(field.__class__, ForeignObjectRel) and not issubclass(field.__class__, OneToOneRel):
                        field_name = getattr(field, "related_name", None) or f"{field.name}_set"
                    else:
                        field_name = getattr(field, "name", field)

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
                        python_type, pydantic_field = ModelSchemaField(field, name)

                    field_values[field_name] = (python_type, pydantic_field)

                cls.__doc__ = namespace.get("__doc__", config.model.__doc__)
                cls.__fields__ = {}
                model_schema = create_model(
                    name, __base__=cls, __module__=cls.__module__, **field_values
                )

                return model_schema

        return cls


class ProxyGetterNestedObj(GetterDict):
    def __init__(self, obj: Any, schema_class):
        self._obj = obj
        self.schema_class = schema_class

    def get(self, key: Any, default: Any = None) -> Any:
        if "__" in key:
            # Allow double underscores aliases: `first_name: str = Field(alias="user__first_name")`
            keys_map = key.split("__")
            attr = reduce(lambda a, b: getattr(a, b, default), keys_map, self._obj)
            outer_type_ = self.schema_class.__fields__["user"].outer_type_
        else:
            attr = getattr(self._obj, key)
            outer_type_ = self.schema_class.__fields__[key].outer_type_

        is_manager = issubclass(attr.__class__, Manager)

        if is_manager and outer_type_ == List[Dict[str, int]]:
            attr = list(attr.all().values("id"))
        elif is_manager:
            attr = list(attr.all())
        elif outer_type_ == int and issubclass(type(attr), Model):
            attr = attr.id
        elif issubclass(attr.__class__, ImageFieldFile) and issubclass(outer_type_, str):
            attr = attr.name
        return attr


class ModelSchema(BaseModel, metaclass=ModelSchemaMetaclass):
    class Config:
        orm_mode = True

    @classmethod
    def schema_json(
        cls,
        *,
        by_alias: bool = True,
        encoder_cls: Any = ModelSchemaJSONEncoder,
        **dumps_kwargs: Any,
    ) -> str:

        return cls.__config__.json_dumps(
            cls.schema(by_alias=by_alias), cls=encoder_cls, **dumps_kwargs
        )

    @classmethod
    @no_type_check
    def get_field_names(cls) -> List[str]:
        if hasattr(cls.__config__, "exclude"):
            django_model_fields = cls.__config__.model._meta.get_fields()
            all_fields = [f.name for f in django_model_fields]
            return [
                name for name in all_fields if name not in cls.__config__.exclude
            ]
        return cls.__config__.include

    @classmethod
    def from_orm(cls, *args, **kwargs):
        return cls.from_django(*args, **kwargs)

    @classmethod
    def from_django(cls, objs, many=False, context={}):
        cls.context = context
        if many:
            result_objs = []
            for obj in objs:
                cls.instance = obj
                result_objs.append(super().from_orm(ProxyGetterNestedObj(obj, cls)))
            return result_objs

        cls.instance = objs
        return super().from_orm(ProxyGetterNestedObj(objs, cls))


_is_base_model_class_defined = True
