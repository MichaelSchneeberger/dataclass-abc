import sys
import typing
from dataclasses import (_FIELD, _FIELD_INITVAR, _POST_INIT_NAME, MISSING,
                         _fields_in_init_order, _init_fn, _process_class,
                         _set_new_attribute)
from typing import Any, Generator, Tuple


def resolve_abc_prop(cls):
    def gen_properties() -> Generator[Tuple[str, Any], None, None]:
        """ search abstract properties in super classes """

        for class_obj in cls.__mro__:
            for key, value in class_obj.__dict__.items():
                if isinstance(value, property):
                    yield key, value

    def gen_non_abstract_prop() -> Generator[Tuple[str, Any], None, None]:
        for key, value in gen_properties():
            if not hasattr(value, '__isabstractmethod__') \
                    or not getattr(value, '__isabstractmethod__'):
                yield key, value

    def gen_abstract_prop() -> Generator[Tuple[str, Any], None, None]:
        for key, value in gen_properties():
            if hasattr(value, '__isabstractmethod__') \
                    and getattr(value, '__isabstractmethod__'):
                yield key, value

    non_abstract_prop = dict(gen_non_abstract_prop())
    abstract_prop = dict(gen_abstract_prop())

    def gen_get_set_properties():
        """ for each matching data and abstract property pair,
            create a getter and setter method """

        for class_obj in cls.__mro__:
            if '__dataclass_fields__' in class_obj.__dict__:
                for key, _ in class_obj.__dict__['__dataclass_fields__'].items():
                    if key in abstract_prop:
                        def get_func(self, key=key):
                            return getattr(self, f'__{key}')

                        def set_func(self, val, key=key):
                            return setattr(self, f'__{key}', val)

                        yield key, property(get_func, set_func)

                    elif key in non_abstract_prop:
                        raise AttributeError(f'field "{key}" shadows non-abstract property "{key}", '
                                             f'either turn property "{key}" to an abstract property '
                                             f'or rename the field "{key}".')

    get_set_properties = dict(gen_get_set_properties())

    mro_filtered = tuple(
        mro for mro in cls.__mro__ if mro is not typing.Generic)

    new_cls = type(
        cls.__name__,
        mro_filtered,
        {**cls.__dict__, **get_set_properties},
    )

    return new_cls


def dataclassabc(_cls=None, /, *, init=True, repr=True, eq=True, order=False,
                  unsafe_hash=False, frozen=False, match_args=True,
                  kw_only=False, slots=False, weakref_slot=False):
    """
    meant to be used as a class decorator similarly to `dataclasses.dataclass`.

    ```
    class A(ABC):
        @property
        @abstractmethod
        def name(self) -> str:
            ...

    @dataclassabc(frozen=True)
    class B(A):
        name: str
    ```

    in addition to `dataclasses.dataclass` it:

    * erases the default value of the fields
    * resolves the abstract properties overwritten by a field

    """

    def wrap(cls):

        try:
            cls = _process_class(cls, init=False, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash,
                                 frozen=frozen, match_args=match_args, kw_only=kw_only, slots=slots,
                                 weakref_slot=weakref_slot)
        except TypeError:
            cls = _process_class(cls, init=False, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash,
                                 frozen=frozen, match_args=match_args, kw_only=kw_only, slots=slots)

        # delete default value of field referencing abstract properties

        fields = cls.__dict__['__dataclass_fields__']

        def gen_fields():
            for field in fields.values():
                if field._field_type in (_FIELD, _FIELD_INITVAR):

                    # delete default
                    if isinstance(field.default, property) and field.default.__isabstractmethod__:
                        field.default = MISSING

                    yield field

        all_init_fields = list(gen_fields())

        # -------------------- begin: copy code from dataclasses -----------------------

        if cls.__module__ in sys.modules:
            globals = sys.modules[cls.__module__].__dict__
        else:
            globals = {}

        (std_init_fields, kw_only_init_fields) = _fields_in_init_order(all_init_fields)

        has_post_init = hasattr(cls, _POST_INIT_NAME)

        _set_new_attribute(cls, '__init__',
                           _init_fn(all_init_fields,
                                    std_init_fields,
                                    kw_only_init_fields,
                                    frozen,
                                    has_post_init,
                                    # The name to use for the "self"
                                    # param in __init__.  Use "self"
                                    # if possible.
                                    '__dataclass_self__' if 'self' in fields
                                    else 'self',
                                    globals,
                                    slots,
                                    ))

        # -------------------- end: copy code from dataclasses -----------------------

        return resolve_abc_prop(cls)

    if _cls is None:
        return wrap

    return wrap(_cls)


