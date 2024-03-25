from dataclasses import Field, field
from typing import Type, TypeVar, Callable, dataclass_transform, overload

__all__ = ['dataclassabc']

_T = TypeVar("_T")

@overload
@dataclass_transform(field_specifiers=(Field, field))
def dataclassabc(
    _cls: None = None, /, *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    match_args: bool = True,
    kw_only: bool = False,
    slots: bool = False,
    weakref_slot: bool = False
) -> Callable[[Type[_T]], Type[_T]]:
    ...

@overload
@dataclass_transform(field_specifiers=(Field, field))
def dataclassabc(
    _cls: Type[_T], /, *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    match_args: bool = True,
    kw_only: bool = False,
    slots: bool = False,
    weakref_slot: bool = False
) -> Type[_T]:
    ...
