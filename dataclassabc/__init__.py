import sys
from dataclasses import (
    _FIELD,  # type: ignore
    _FIELD_INITVAR,  # type: ignore
    MISSING as _MISSING,
    Field as _Field,
    field as _field,
    dataclass as _dataclass,
)
import types
from typing import Generic, TypeVar, Type, Callable, get_origin

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

    for class_obj in cls.__mro__:
        for key, value in class_obj.__dict__.items():
            if isinstance(value, property):
                if not hasattr(value, "__isabstractmethod__") or not getattr(
                    value, "__isabstractmethod__"
                ):
                    non_abstract_prop[key] = value

                elif hasattr(value, "__isabstractmethod__") and getattr(
                    value, "__isabstractmethod__"
                ):
                    abstract_prop[key] = value

    def gen_get_set_properties():
        """
        For each matching dataclass field and abstract property pair, create a getter and setter method.
        """

        for class_obj in cls.__mro__:
            if "__dataclass_fields__" in class_obj.__dict__:
                for key, _ in class_obj.__dict__["__dataclass_fields__"].items():
                    if key in abstract_prop:

                        def get_func(self, key=key):
                            return getattr(self, f"__{key}")

                        def set_func(self, val, key=key):
                            return setattr(self, f"__{key}", val)

                        yield key, property(get_func, set_func)

                    elif key in non_abstract_prop:
                        raise AttributeError(
                            f'field "{key}" shadows non-abstract property "{key}", '
                            f'either turn property "{key}" to an abstract property '
                            f'or rename the field "{key}".'
                        )

    get_set_properties = dict(gen_get_set_properties())

    # filter out Generic classes
    mro_filtered = tuple(mro for mro in cls.__mro__ if mro is not Generic)

    new_cls = type(
        cls.__name__,
        mro_filtered,
        {**cls.__dict__, **get_set_properties},
    )

    return new_cls


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
    *,
    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=False,
    match_args=True,
    kw_only=False,
    slots=False,
    weakref_slot=False,
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

        def inner_dataclass(inner_cls, init):
            if sys.version_info >= (3, 11):
                return _dataclass(
                    init=init,
                    repr=repr,
                    eq=eq,
                    order=order,
                    unsafe_hash=unsafe_hash,
                    frozen=frozen,
                    match_args=match_args,
                    kw_only=kw_only,
                    slots=slots,
                    weakref_slot=weakref_slot,
                )(inner_cls)
            else:
                return _dataclass(
                    init=init,
                    repr=repr,
                    eq=eq,
                    order=order,
                    unsafe_hash=unsafe_hash,
                    frozen=frozen,
                    match_args=match_args,
                    kw_only=kw_only,
                    slots=slots,
                )(inner_cls)

        # create dataclass without init method to avoid "non-default argument 
        # follows default argument" error
        decorated_cls = inner_dataclass(cls, init=False)

        if init:
            fields = decorated_cls.__dataclass_fields__
            for field in fields.values():
                if field._field_type in (_FIELD, _FIELD_INITVAR):
                    if (
                        isinstance(field.default, property)
                        and field.default.__isabstractmethod__
                    ):
                        # override default value
                        field.default = _MISSING

            def gen_generic():
                for base in types.get_original_bases(decorated_cls):
                    if get_origin(base) is Generic:
                        yield base

            # create new class with empty dunder methods (__repr__, __setattr__, etc.)
            #   to avoid triggering dataclass's exception
            cls_no_init = types.new_class(
                cls.__name__,
                (decorated_cls,) + tuple(gen_generic()),
                {},
            )
            decorated_cls = inner_dataclass(cls_no_init, init=True)

        if slots:
            return decorated_cls

        # Create a property for each abstract property that is implemented by a 
        # dataclass field
        return resolve_abc_prop(decorated_cls)

    if _cls is None:
        return wrap

    return wrap(_cls)
