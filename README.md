# Dataclass ABC

Library that lets you define abstract properties for dataclasses. 

## Installation

```pip install dataclass-abc```

## Usage

The `dataclass_abc` class decorator:

* erases the default value of the fields (see comment below)
* resolves the abstract properties overwritten by a field

``` python
from abc import ABC, abstractmethod

from dataclass_abc import dataclass_abc

class A(ABC):
    @property
    @abstractmethod
    def val(self) -> str:
        ...

@dataclass_abc
class B(A):
    val: str        # overwrites the abstract property 'val' in 'A'
```

### Erase default value

`dataclass_abc` erases the default values of fields. This has the advantage that
additional fields that do not refer to an abstract property can be added
without running into the "*non-default argument follows default argument*" 
exception.

Therefore, do not define default values, work with *initialize functions* 
instead (see Design Pattern below).

``` python
from abc import ABC, abstractmethod

from dataclass_abc import dataclass_abc

class A(ABC):
    @property
    @abstractmethod
    def val1(self) -> str:
        ...

@dataclass_abc
class B(A):
    val1: str
    val2: str

# work with initialize functions when dealing with default values
def init_b(
    val1: str,
    val2: str = 'default',
):
    return B(val1=val1, val2=val2)
```

## Example

The [example](https://github.com/MichaelSchneeberger/dataclass-abc/tree/master/example)
implements the code snippets taken from [RealPython](https://realpython.com/python-data-classes/)
 with abstract properties.

## Design pattern

This library suggests the design pattern as implemented in the 
[example](https://github.com/MichaelSchneeberger/dataclass-abc/tree/master/example):

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
