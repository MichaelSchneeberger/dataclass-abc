# Dataclass ABC

Library that lets you define abstract properties for dataclasses. 

## Installation

```pip install dataclass-abc```

## Usage

The `dataclass_abc` class decorator resolves the abstract properties 
overwritten by a field.

``` python
from abc import ABC, abstractmethod

from dataclass_abc import dataclass_abc

class A(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

@dataclass_abc(frozen=True)
class B(A):
    name: str        # overwrites the abstract property 'name' in 'A'
```

## Define mutable variables

Define a mutable variable `name` in the abstract class `A` by using the
`name.setter` decorator. 

``` python
from abc import ABC, abstractmethod

from dataclass_abc import dataclass_abc

class A(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @name.setter
    @abstractmethod
    def name(self, val: str):
        ...

    def set_name(self, val: str):
        self.name = val

@dataclass_abc
class B(A):
    name: str

b = B(name='A')
b.set_name('B')
```

## Example

The [example](https://github.com/MichaelSchneeberger/dataclass-abc/tree/master/example)
implements the code snippets taken from [RealPython](https://realpython.com/python-data-classes/)
 with abstract properties.

## Design pattern

This library suggests the following design pattern:

- **mixins** - a *mixin* is an abstract class that implements data as abstract
properties and methods based on the abstract properties.
- **classes** - an abstract class inherits from one or more mixins
(see `City` or `CapitalCity` in the example). This class is used for pattern matching,
e.g. using `isinstance` method.
- **impl** - an *implementation class* implements the abstract properties. 
(see `CityImpl` or `CapitalCityImpl` in the example). This class is decorated with
`dataclass_abc` and `resolve_abc_prop` and should always be called through an 
*initialize function*.
- **init** - an *initialize function* (or *constructor function*) initializes an 
*implementation class*.
