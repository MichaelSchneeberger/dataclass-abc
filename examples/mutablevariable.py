from abc import ABC, abstractmethod

from dataclassabc import dataclassabc

class A(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @name.setter
    @abstractmethod
    def name(self, val: str):
        ...

@dataclassabc
class B(A):
    name: str

b = B(name='A')
b.name = 'B'

print(f'{b=}')