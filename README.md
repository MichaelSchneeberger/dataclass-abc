# Dataclass-ABC

**Dataclass-ABC** is a Python library that bridges the gap between abstract base classes (ABCs) and dataclasses. It allows you to define and automatically implement abstract properties in dataclasses when these properties are overridden by fields.

## Features

* **Abstract properties**: Implement abstract properties by inheritence using dataclasses.
* **Trait Behavior**: Allows to reproduce Trait-like behavior (as in Scala or Rust) using Python ABC classes.



## Installation

Install **Dataclass-ABC** using pip:

```bash
pip install dataclassabc
```


## Usage

The `dataclassabc` decorator enables the use of abstract properties within dataclasses.
It resolves abstract properties defined in an abstract base class (ABC) and enforces their implementation through fields in the derived dataclass.


### Example

Here's how you can define an abstract property in an abstract class and implement it in a dataclass:

``` python
from abc import ABC, abstractmethod
from dataclassabc import dataclassabc

# Define an abstract base class with an abstract property
class A(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

# Use the dataclassabc decorator to implement the abstract property in a dataclass
@dataclassabc(frozen=True)
class B(A):
    # Implementing the abstract property 'name'
    name: str

# Works as expected
b1 = B(name='A')

# TypeError: B.__init__() missing 1 required positional argument: 'name'
b2 = B()
```


## Define mutable variables

<!-- You can define mutable abstract properties by using the `@property` and `@name.setter` decorators in the abstract class. The following example demonstrates how to define and set a mutable property: -->
The dataclassabc library also supports defining mutable abstract properties. Use the @property decorator alongside a setter to define mutable properties in the abstract class.

``` python
from abc import ABC, abstractmethod
from dataclassabc import dataclassabc

class A(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @name.setter
    @abstractmethod
    def name(self, val: str): ...

@dataclassabc
class B(A):
    name: str
```



## Comparison with the standard `dataclass`

Here are known issues when using the standard `dataclass` decorator in combination with `abc` library:

<!-- * AttributeError: "Property object has not setter"
    ``` python
    from abc import abstractmethod
    from dataclasses import dataclass

    class A:
        @property
        @abstractmethod
        def name(self) -> str:
            ...

    @dataclass(frozen=True)
    class B(A):
        name: str

    # AttributeError: property 'name' of 'B' object has no setter
    b = B(name='A')
    ``` -->



* TypeError: "Can't instantiate abstract class" when trying to override an abstract property with a dataclass field.
    ``` python
    from abc import ABC, abstractmethod
    from dataclasses import dataclass

    class A(ABC):
        @property
        @abstractmethod
        def name(self) -> str:
            ...

    @dataclass(frozen=True)
    class B(A):
        name: str

    # TypeError: Can't instantiate abstract class B without an implementation for abstract method 'name'
    b = B(name='A')
    ```


* Unexpected Default Value `<property object at ...>` when using dataclass option `slots=True`.
    ``` python
    from abc import ABC, abstractmethod
    from dataclasses import dataclass

    class A(ABC):
        @property
        @abstractmethod
        def name(self) -> str:
            ...

    @dataclass(slots=True)
    class B(A):
        name: str

    # No exception is raised when name is not provided
    b = B()

    # The output will be <property object at ...>
    print(b.name)
    ```


* TypeError: "Non-default argument follows default argument" when using dataclass option `slots=True`.
    ``` python
    from abc import ABC, abstractmethod
    from dataclasses import dataclass

    class A(ABC):
        @property
        @abstractmethod
        def name(self) -> str:
            ...

    @dataclass(slots=True)
    class B(A):
        name: str
        age: int

    # TypeError: non-default argument 'age' follows default argument 'name'
    b = B(age=12, name='A')
    ```
