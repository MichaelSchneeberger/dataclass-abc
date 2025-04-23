from abc import ABC, abstractmethod

from dataclassabc import dataclassabc

# Define an abstract base class with an abstract property
class A[T](ABC):
    @property
    @abstractmethod
    def name(self) -> T:
        ...

# Use the dataclassabc decorator to implement the abstract property in a dataclass
@dataclassabc(frozen=True)
class B[T](A[T]):
    # Implementing the abstract property 'name'
    name: T

b = B[str](name='B')
print(b)
