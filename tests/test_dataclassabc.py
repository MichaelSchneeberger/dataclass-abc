import unittest
from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError

from dataclassabc import dataclassabc


class TestDataclassABC(unittest.TestCase):
    def test_frozen_dataclass(self):
        class A(ABC):
            @property
            @abstractmethod
            def val1(self) -> int: ...

        @dataclassabc(frozen=True)
        class B(A):
            val1: int

        b = B(val1=1)

        self.assertEqual(1, b.val1)
        with self.assertRaises(FrozenInstanceError):
            b.val1 = 2

    def test_non_frozen_dataclass(self):
        class A(ABC):
            @property
            @abstractmethod
            def val1(self) -> int: ...

            # define setter only for type hinting
            @val1.setter
            @abstractmethod
            def val1(self, value: int): ...

        @dataclassabc
        class B(A):
            val1: int

        b = B(val1=1)

        self.assertEqual(1, b.val1)

        b.val1 = 2

        self.assertEqual(2, b.val1)

    def test_non_default_follows_default_argument(self):
        class A(ABC):
            @property
            @abstractmethod
            def val1(self) -> int: ...

        @dataclassabc
        class B(A):
            val1: int
            val2: int

        b = B(val1=1, val2=2)

    def test_shadowing_non_abstract_property(self):
        class A:
            @property
            def val1(self) -> int:
                return 1

        with self.assertRaisesRegex(
            AttributeError, 'field "val1" shadows non-abstract property "val1"'
        ) as exc:

            @dataclassabc
            class B(A):
                val1: int

    def test_shadowing_function(self):
        class A:
            def val1(self) -> int:
                return 1

        @dataclassabc
        class B(A):
            val1: int

        b = B(val1=2)

        self.assertEqual(2, b.val1)
