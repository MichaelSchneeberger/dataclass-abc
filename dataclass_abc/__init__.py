def resolve_abc_prop(cls):
    def gen_abstract_properties():
        """ search for abstract properties in super classes """

        for class_obj in cls.__mro__:
            for key, value in class_obj.__dict__.items():
                if isinstance(value, property) and value.__isabstractmethod__:
                    yield key, value

    abstract_prop = dict(gen_abstract_properties())

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

    get_set_properties = dict(gen_get_set_properties())

    new_cls = type(
        cls.__name__,
        cls.__mro__,
        {**cls.__dict__, **get_set_properties},
    )

    return new_cls