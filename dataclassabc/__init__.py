import sys
from dataclasses import (
    _FIELD,  # type: ignore
    _FIELD_INITVAR,  # type: ignore
    _POST_INIT_NAME,  # type: ignore
    MISSING as _MISSING,
    _fields_in_init_order,  # type: ignore
    _init_fn,  # type: ignore
    _process_class,  # type: ignore
    _set_new_attribute,  # type: ignore
    Field as _Field,
    field as _field,
)
from typing import Generic, TypeVar, Type, Callable

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
        try:
            cls = _process_class(
                cls,
                init=False,
                repr=repr,
                eq=eq,
                order=order,
                unsafe_hash=unsafe_hash,
                frozen=frozen,
                match_args=match_args,
                kw_only=kw_only,
                slots=slots,
                weakref_slot=weakref_slot,
            )
        except TypeError:  # Python 3.10
            cls = _process_class(
                cls,
                init=False,
                repr=repr,
                eq=eq,
                order=order,
                unsafe_hash=unsafe_hash,
                frozen=frozen,
                match_args=match_args,
                kw_only=kw_only,
                slots=slots,
            )

        fields = cls.__dict__["__dataclass_fields__"]

        def gen_fields():
            """
            Generates dataclass fields with _MISSING default value when shadowing abstract properties.

            Abstract properties that shadow dataclass fields are added as default values to those fields. If this default
            value (a property object) is not removed, the dataclass will incorrectly assign the property object as the
            field's value when an argument is not provided during initialization.

            Example:

            ```python
            from abc import ABC, abstractmethod
            from dataclassabc import dataclassabc

            class A(ABC):
                @property
                @abstractmethod
                def name(self) -> str: ...

            @dataclassabc(frozen=True)
            class B(A):
                name: str

            # Attempting to create an instance without providing a value for 'name'
            b = B()
            print(b)   # Output: B(name=<property object at ...>)
            ```

            Once the field's default value is remove, initializing the dataclass `B` without providing a value for the `name` argument
            will result in an error.

            ``` python
            # TypeError: B.__init__() missing 1 required positional argument: 'name'
            b = B()
            ```
            """

            for field in fields.values():
                if field._field_type in (_FIELD, _FIELD_INITVAR):
                    if (
                        isinstance(field.default, property)
                        and field.default.__isabstractmethod__
                    ):
                        field.default = _MISSING

                    yield field

        all_init_fields = list(gen_fields())

        if cls.__module__ in sys.modules:
            globals = sys.modules[cls.__module__].__dict__
        else:
            globals = {}

        (std_init_fields, kw_only_init_fields) = _fields_in_init_order(all_init_fields)

        has_post_init = hasattr(cls, _POST_INIT_NAME)

        # Recreate the __init__ method after removing default values from the fields
        _set_new_attribute(
            cls,
            "__init__",
            _init_fn(
                all_init_fields,
                std_init_fields,
                kw_only_init_fields,
                frozen,
                has_post_init,
                # The name to use for the "self"
                # param in __init__.  Use "self"
                # if possible.
                "__dataclass_self__" if "self" in fields else "self",
                globals,
                slots,
            ),
        )

        # Create a property for each abstract property that is overridden by a corresponding dataclass field
        return resolve_abc_prop(cls)

    if _cls is None:
        return wrap

    return wrap(_cls)
