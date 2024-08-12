# Dataclassabc

A Python library that allows you to define abstract properties for dataclasses, bridging the gap between abstract base classes (ABCs) and dataclasses.

## Installation

Install the library using pip:

```bash
pip install dataclassabc
```

## Usage

The `dataclassabc` decorator enables the use of abstract properties within dataclasses.
It resolves abstract properties defined in an abstract base class (ABC) and enforces their implementation through fields in the derived dataclass.

### Example

Here's how you can define an abstract property in a base class and implement it in a derived dataclass:

``` python
from abc import ABC, abstractmethod

from dataclassabc import dataclassabc

# Define an abstract base class with an abstract property
class A(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

# Use the dataclassabc decorator to implement the abstract property in a dataclass
@dataclassabc(frozen=True)
class B(A):
    # Implementing the abstract property 'name'
    name: str
```

Using the standard `dataclass` decorator from the `dataclasses` module to implement abstract properties will result in a TypeError, as shown below:

``` python
from abc import ABC, abstractmethod

from dataclasses import dataclass

@dataclass(frozen=True)
class B(A):
    name: str

# TypeError: Can't instantiate abstract class B without an implementation for abstract method 'name'
b = B(name='A')
```


## Define mutable variables

You can define mutable abstract properties by using the `@property` and `@name.setter` decorators in the abstract class. The following example demonstrates how to define and set a mutable property:

### Example

``` python
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
# modify the mutable variable
b.name = 'B'

# Output will be b=B(name='B')
print(f'{b=}')
```

<!-- ## Design pattern

The `dataclassabc` library encourages a structured approach to designing dataclasses with abstract properties, following a specific design pattern:

- **Mixins**: Abstract classes that define data through abstract properties and implement methods based on these properties.
- **Abstract Classes** -  Inherit from one or more mixins and may define additional abstract methods or properties. These classes are typically used for type checking (e.g., with isinstance).
- **Implementation Classes** - Concrete classes that implement the abstract properties. These classes are decorated with `dataclassabc`. They should be instantiated through an initializer function.
- **initializer Functions** - Functions responsible for initializing and returning instances of implementation classes, encapsulating the creation logic.

## Conclusion

The `dataclassabc` library facilitates the integration of abstract base classes with Python's dataclasses, promoting a clean and data focused design pattern in your projects. By following the recommended design pattern, you can maintain a clear separation of concerns between abstract definitions and their concrete implementations. -->
