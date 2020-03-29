import sys
from dataclasses import dataclass as parent_dataclass, MISSING, _POST_INIT_NAME, _FIELD, _FIELD_INITVAR, \
    _set_new_attribute, _init_fn


def resolve_abc_prop(cls):
    def gen_properties():
        """ search abstract properties in super classes """

        for class_obj in cls.__mro__:
            for key, value in class_obj.__dict__.items():
                if isinstance(value, property):
                    yield key, value

    non_abstract_prop = dict((key, value) for key, value in gen_properties() if not value.__isabstractmethod__)
    abstract_prop = dict((key, value) for key, value in gen_properties() if value.__isabstractmethod__)

    def gen_get_set_properties():
        """ for each matching data and abstract property pair,
            create a getter and setter method """

        for class_obj in cls.__mro__:
            if '__dataclass_fields__' in class_obj.__dict__:
                for key, value in class_obj.__dict__['__dataclass_fields__'].items():
                    if key in abstract_prop:
                        def get_func(self, key=key):
                            return getattr(self, f'__{key}')

                        def set_func(self, val, key=key):
                            return setattr(self, f'__{key}', val)

                        yield key, property(get_func, set_func)

                    else:
                        if key in non_abstract_prop:
                            raise AttributeError(f'field "{key}" shadows non-abstract property "{key}", '
                                                 f'either turn property "{key}" to an abstract property '
                                                 f'or rename the field "{key}".')

    get_set_properties = dict(gen_get_set_properties())

    new_cls = type(
        cls.__name__,
        cls.__mro__,
        {**cls.__dict__, **get_set_properties},
    )

    return new_cls


def dataclass_abc(_cls=None, *, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False):
    """
    meant to be used as a class decorator similarly to `dataclasses.dataclass_abc`.

    in addition to `dataclasses.dataclass_abc` it:

    * erases the default value of the fields
    * resolves the abstract properties overwritten by a field

    """

    def wrap(cls):
        if cls.__module__ in sys.modules:
            globals = sys.modules[cls.__module__].__dict__
        else:
            # Theoretically this can happen if someone writes
            # a custom string to cls.__module__.  In which case
            # such dataclass_abc won't be fully introspectable
            # (w.r.t. typing.get_type_hints) but will still function
            # correctly.
            globals = {}

        cls = parent_dataclass(cls, init=False, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash, frozen=frozen)

        fields = cls.__dict__['__dataclass_fields__']

        def gen_fields():
            for field in fields.values():
                # Include InitVars and regular fields (so, not ClassVars).
                if field._field_type in (_FIELD, _FIELD_INITVAR):
                    field.default = MISSING
                    field.default_factory = MISSING
                    yield field

        flds = list(gen_fields())

        # Does this class have a post-init function?
        has_post_init = hasattr(cls, _POST_INIT_NAME)

        _set_new_attribute(cls, '__init__',
                           _init_fn(flds,
                                    frozen,
                                    has_post_init,
                                    # The name to use for the "self"
                                    # param in __init__.  Use "self"
                                    # if possible.
                                    '__dataclass_self__' if 'self' in fields
                                            else 'self',
                                    globals,
                          ))

        return resolve_abc_prop(cls)

    # See if we're being called as @dataclass or @dataclass().
    if _cls is None:
        # We're called with parens.
        return wrap

    # We're called as @dataclass without parens.
    return wrap(_cls)
