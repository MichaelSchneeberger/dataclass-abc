import unittest
from abc import ABC, abstractmethod
from dataclasses import dataclass

from dataclass_abc import resolve_abc_prop


class TestResolveABCProp(unittest.TestCase):
    def test_frozen_dataclass(self):
        class A(ABC):
            @property
            @abstractmethod
            def val1(self) -> int:
                ...

        @resolve_abc_prop
        @dataclass(frozen=True)
        class B(A):
            val1: int

        b = B(val1=1)

        self.assertEqual(1, b.val1)

    def test_non_frozen_dataclass(self):
        class A(ABC):
            @property
            @abstractmethod
            def val1(self) -> int:
                ...

            # define setter only for type hinting
            @val1.setter
            @abstractmethod
            def val1(self, value: int):
                ...

        @resolve_abc_prop
        @dataclass
        class B(A):
            val1: int

        b = B(val1=1)

        self.assertEqual(1, b.val1)

        b.val1 = 2

        self.assertEqual(2, b.val1)

    def test_shadowing_non_abstract_property(self):
        class A:
            @property
            def val1(self) -> int:
                return 1

        with self.assertRaisesRegex(AttributeError, 'field "val1" shadows non-abstract property "val1"') as exc:
            @resolve_abc_prop
            @dataclass
            class B(A):
                val1: int

    def test_shadowing_function(self):
        class A:
            def val1(self) -> int:
                return 1

        @resolve_abc_prop
        @dataclass
        class B(A):
            val1: int

        b = B(val1=2)

        self.assertEqual(2, b.val1)
