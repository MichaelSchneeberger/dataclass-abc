import unittest
from abc import ABC
from dataclasses import dataclass, is_dataclass, fields, Field, _DataclassParams
from typing import Protocol, overload

from dataclassabc import dataclassabc


class _ObjWithSlots(Protocol):
    __slots__: tuple[str, ...]

def object_as_tuple(obj_with_slots: _ObjWithSlots) -> tuple:
    return tuple(getattr(obj_with_slots, name) for name in type(obj_with_slots).__slots__)


class TestNotLosingAttributes(unittest.TestCase):
    def test_not_losing_docstring(self):
        @dataclassabc
        class A:
            """ This is A's docstring """
            value: int

        self.assertEqual(A.__doc__.strip(), "This is A's docstring", "A's docstring is not correct")

    def test_not_losing_module(self):
        @dataclassabc
        class Parent(ABC): ...
        @dataclassabc
        class A(Parent): ...
        @dataclass
        class B(Parent): ...

        self.assertEqual(A.__module__, B.__module__, "A's `__module__` attribute has wrong value.")

    # def test_not_losing_annotation(self):
    #     @dataclassabc
    #     class A(ABC):
    #         x: int
    #         y: int
    #         name: str
    #     @dataclass
    #     class B(ABC):
    #         x: int
    #         y: int
    #         name: str
    #
    #     self.assertDictEqual(A.__annotations__, B.__annotations__, "A's annotations data was lost.")

    @overload
    def assertObjectWithSlotsEqual(self, a: Field, b: Field, msg=None):
        ...
    @overload
    def assertObjectWithSlotsEqual(self, a: _DataclassParams, b: _DataclassParams, msg=None):
        ...
    @overload
    def assertObjectWithSlotsEqual(self, a: _ObjWithSlots, b: _ObjWithSlots, msg=None):
        ...
    def assertObjectWithSlotsEqual(self, a: _ObjWithSlots, b: _ObjWithSlots, msg=None):
        self.assertTupleEqual(object_as_tuple(a), object_as_tuple(b), msg)

    def test_not_losing_dataclass_attributes(self):
        @dataclassabc(frozen=True, slots=True, order=True)
        class A(ABC):
            x: int
            y: int
            name: str
        @dataclass(frozen=True, slots=True, order=True)
        class B(ABC):
            x: int
            y: int
            name: str

        a_fields = fields(A)
        b_fields = fields(B)

        self.assertEqual(len(a_fields), len(b_fields), "Fields list length diverge.")
        for fa, fb in zip(a_fields, b_fields):
            self.assertObjectWithSlotsEqual(fa, fb, f"Field {fb.name} data is incorrect.")
        self.assertObjectWithSlotsEqual(A.__dataclass_params__, B.__dataclass_params__, "A's dataclass parameters data is incorrect.")

    def test_is_dataclass(self):
        @dataclassabc
        class A: ...
        @dataclass
        class B: ...

        self.assertTrue(is_dataclass(A), "A did not pass the dataclas check.")
        self.assertTrue(is_dataclass(B), "B SOMEHOW did not pass the dataclas check.")
