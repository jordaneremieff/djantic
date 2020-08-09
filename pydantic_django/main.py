from itertools import chain
from typing import Type, Optional

import django
from pydantic import BaseModel, create_model, validate_model
from pydantic.main import ModelMetaclass

from .types import DjangoField


class PydanticDjangoError(Exception):
    """
    Raised when an exception occurs in the Pydantic Django model.
    """


_is_base_model_class_defined = False


class PydanticDjangoModelMetaclass(ModelMetaclass):
    def __new__(
        mcs: Type["PydanticDjangoModelMetaclass"],
        name: str,
        bases: tuple,
        namespace: dict,
    ) -> "PydanticDjangoModelMetaclass":
        cls = super().__new__(mcs, name, bases, namespace)
        for base in reversed(bases):
            if (
                _is_base_model_class_defined
                and issubclass(base, PydanticDjangoModel)
                and base == PydanticDjangoModel
            ):

                config = namespace["Config"]
                include = getattr(config, "include", None)
                exclude = getattr(config, "exclude", None)

                if include and exclude:
                    raise PydanticDjangoError(
                        "Only one of 'include' or 'exclude' should be set in configuration."
                    )

                annotations = namespace.get("__annotations__", {})
                try:
                    fields = config.model._meta.get_fields()
                except AttributeError as exc:
                    raise PydanticDjangoError(
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
                        python_type, pydantic_field = DjangoField(field)

                    field_values[field_name] = (python_type, pydantic_field)

                cls.__doc__ = namespace.get("__doc__", config.model.__doc__)
                cls.__fields__ = {}
                p_model = create_model(
                    name, __base__=cls, __module__=cls.__module__, **field_values
                )

                setattr(p_model, "instance", None)
                setattr(p_model, "objects", p_model._objects())
                setattr(p_model, "get", p_model._get)
                setattr(p_model, "create", p_model._create)

                return p_model

        return cls


class PydanticDjangoModel(BaseModel, metaclass=PydanticDjangoModelMetaclass):
    def save(self) -> None:
        cls = self.__class__
        p_model = cls.from_django(self.instance, save=True)
        self._ṣet_object(
            __dict__=p_model.__dict__, __fields_set__=p_model.__fields_set__
        )

    def refresh(self) -> None:
        cls = self.__class__
        instance = cls.objects.get(pk=self.instance.pk)
        p_model = cls.from_django(instance)
        self._ṣet_object(
            __dict__=p_model.__dict__, __fields_set__=p_model.__fields_set__
        )

    def delete(self) -> None:
        self.instance.delete()
        cls = self.__class__
        cls.instance = None
        p_model = cls.__new__(cls)
        self._ṣet_object(__dict__=p_model.__dict__)

    def _ṣet_object(self, **kwargs) -> None:
        object.__setattr__(self, "__dict__", kwargs["__dict__"])
        object.__setattr__(self, "__fields_set__", kwargs.get("__fields_set__", {}))

    @classmethod
    def _objects(cls) -> django.db.models.manager.Manager:
        if not cls.__config__.model:
            raise PydanticDjangoError(
                "A valid Django model class must be set on `Config.model`."
            )

        return cls.__config__.model.objects

    @classmethod
    def _create(cls, **kwargs) -> Type["PydanticDjangoModel"]:
        instance = cls.objects.create(**kwargs)

        return cls.from_django(instance)

    @classmethod
    def _get(cls, **kwargs) -> Type["PydanticDjangoModel"]:
        instance = cls.objects.get(**kwargs)

        return cls.from_django(instance)

    @classmethod
    def from_django_qs(
        cls: Type["PydanticDjangoModel"], instance: django.db.models.query.QuerySet
    ) -> Type["PydanticDjangoModel"]:
        raise NotImplementedError("TODO...")

    @classmethod
    def from_django(
        cls: Type["PydanticDjangoModel"],
        instance: django.db.models.Model,
        cache: bool = True,
        save: bool = False,
    ) -> Type["PydanticDjangoModel"]:

        obj_data = {}
        for field in instance._meta.get_fields():
            if not field.concrete and field.auto_created:
                accessor_name = field.get_accessor_name()
                if field.one_to_many:
                    obj_data[accessor_name] = list(
                        getattr(instance, accessor_name).all().values("pk")
                    )
                elif field.one_to_one:
                    _obj = getattr(instance, accessor_name, None)
                    if _obj:
                        obj_data[accessor_name] = _obj.pk
            else:
                obj_data[field.name] = field.value_from_object(instance)

        values, fields_set, validation_error = validate_model(cls, obj_data)
        if validation_error:
            raise validation_error

        p_model = cls.__new__(cls)
        object.__setattr__(p_model, "__dict__", values)
        object.__setattr__(p_model, "__fields_set__", fields_set)

        if save:
            instance.save()
        if cache:
            cls.instance = instance

        return p_model


_is_base_model_class_defined = True
