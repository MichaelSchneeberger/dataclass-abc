# Dataclass ABC

Library that lets you define abstract properties in dataclasses. 

## Installation

```pip install dataclass-abc```

## Usage

``` python
from abc import ABC, abstractmethod
from dataclasses import dataclass

from dataclass_abc import resolve_abc_prop

class A(ABC):
    @property
    @abstractmethod
    def val(self) -> str:
        ...

@resolve_abc_prop
@dataclass
class B(A):
    val: str
```

## Example

The [example](https://github.com/MichaelSchneeberger/dataclass-abc/tree/master/example)
takes some code snippets from https://realpython.com/python-data-classes/ and
implements them with abstract properties.

## Design pattern

This library suggests the design pattern as implemented in the 
[example](https://github.com/MichaelSchneeberger/dataclass-abc/tree/master/example):

- **mixins** - a mixin is an abstract class that implements data as abstract
properties and methods based on the abstract properties.
- **classes** - an abstract class inherits from one or more mixins
(see `City` or `CapitalCity` in the example). This class is used for pattern matching,
e.g. using `isinstance` method.
- **impl** - an implementation class implements the abstract properties. 
(see `CityImpl` or `CapitalCityImpl` in the example). This class is decorated with
`dataclass` and `resolve_abc_prop` and should always be called through an 
initialize function.
- **init** - initialize functions (or constructor functions) initialize an 
implementation class.
