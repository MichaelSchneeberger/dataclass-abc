from dataclasses import (
    _FIELD,  # type: ignore
    _FIELD_INITVAR,  # type: ignore
    MISSING as _MISSING,
    Field as _Field,
    field as _field,
    dataclass as _dataclass,
)
from typing import TypeVar, Type, Callable

# ensures compatibility with Python 3.10
from typing_extensions import (
    overload as _overload,
    dataclass_transform as _dataclass_transform,
)

__all__ = ["dataclassabc"]
_T = TypeVar("_T")


def resolve_abc_prop(cls):
    """
    Resolves abstract properties in a dataclass by replacing dataclass fields that shadow abstract properties
    with properties. The new properties access the underlying field value through a private attribute named
    '__[field_name]'. This ensures that the dataclass correctly implements the abstract property requirements.

    Example:

    ```python
    from abc import ABC, abstractmethod
    from dataclasses import dataclass
    from dataclassabc import resolve_abc_prop

    # Abstract base class with an abstract property
    class A(ABC):
        @property
        @abstractmethod
        def x(self) -> int:
            pass

    # Dataclass implementing the abstract property
    @resolve_abc_prop
    @dataclass
    class B(A):
        x: int  # This field shadows the abstract property 'x'
    ```

    In this example, the `resolve_abc_prop` decorator ensures that the `x` field in class `B` implements
    the abstract property `x` from class `A`, allowing the dataclass to function correctly without raising
    a `TypeError`.

    :param cls: The dataclass class to which the decorator is applied.
    :return: The modified class with resolved abstract properties.
    """

    non_abstract_prop = {}
    abstract_prop = {}
    class_objects = {}

    for class_obj in cls.__mro__:
        for key, object in class_obj.__dict__.items():
            if isinstance(object, property):
                if getattr(object, "__isabstractmethod__", False):
                    abstract_prop[key] = object
                    class_objects[key] = class_obj
                else:
                    non_abstract_prop[key] = object

    prop_overrides = set()

    for class_obj in cls.__mro__:
        if "__dataclass_fields__" in class_obj.__dict__:
            for key, _ in class_obj.__dict__["__dataclass_fields__"].items():
                if key in abstract_prop:
                    # def get_func(self, key=key):
                    #     return self.__dict__[f"__{key}"]

                    # def set_func(self, val, key=key):
                    #     self.__dict__[f"__{key}"] = val

                    # setattr(cls, key, property(get_func, set_func))

                    # remove the abstract method
                    delattr(class_objects[key], key)
                    prop_overrides.add(key)

                elif key in non_abstract_prop:
                    raise AttributeError(
                        f'field "{key}" shadows non-abstract property "{key}", '
                        f'either turn property "{key}" to an abstract property '
                        f'or rename the field "{key}".'
                    )
    
    if prop_overrides:
        cls.__abstractmethods__ -= prop_overrides

    return cls


@_overload
@_dataclass_transform(field_specifiers=(_Field, _field))
def dataclassabc(
    _cls: None = None,
    /,
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    match_args: bool = True,
    kw_only: bool = False,
    slots: bool = False,
    weakref_slot: bool = False,
) -> Callable[[Type[_T]], Type[_T]]: ...


@_overload
@_dataclass_transform(field_specifiers=(_Field, _field))
def dataclassabc(
    _cls: Type[_T],
    /,
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    match_args: bool = True,
    kw_only: bool = False,
    slots: bool = False,
    weakref_slot: bool = False,
) -> Type[_T]: ...


@_dataclass_transform(field_specifiers=(_Field, _field))
def dataclassabc(
    _cls=None,
    /,
    # *,
    **kwargs,
):
    """
    A decorator that transforms an abstract class into a dataclass, resolving abstract properties that are
    overridden by dataclass fields.

    ```
    class A(ABC):
        @property
        @abstractmethod
        def name(self) -> str:
            ...

    # Apply the dataclassabc decorator to create a dataclass that fulfills the abstract class's contract
    @dataclassabc(frozen=True)
    class B(A):
        name: str  # Implements the abstract property 'name'
    ```
    """

    def wrap(cls):

        if kwargs.get('init', True):
            # create dataclass without init method to prevent "non-default argument follows default argument" error
            # decorated_cls = _dataclass(init=False)(cls)
            decorated_cls = resolve_abc_prop(cls)

            # fields = decorated_cls.__dataclass_fields__
            # for field in fields.values():
            #     if field._field_type in (_FIELD, _FIELD_INITVAR):
            #         if isinstance(field.default, property) and field.default.__isabstractmethod__:
            #             # Override default value of the dataclass field.
            #             # This ensures a TypeError is raised if the argument is not provided during initialzation,
            #             # rather than silently defaulting to the reference to the abstract method.
            #             field.default = _MISSING

        else:
            decorated_cls = cls

        # print(decorated_cls.__dataclass_fields__)

        # print(getattr(decorated_cls, 'val1'))

        decorated_cls = _dataclass(**kwargs)(decorated_cls)

        # if kwargs.get('slots', False):
        #     return decorated_cls

        # Create a property for each abstract property that is implemented by a 
        # dataclass field
        # return resolve_abc_prop(decorated_cls)
        return decorated_cls

    if _cls is None:
        return wrap

    return wrap(_cls)
