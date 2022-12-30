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


def dataclass_abc(_cls=None, /, *, init=True, repr=True, eq=True, order=False,
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

    @dataclass_abc(frozen=True)
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


# def create_class(
#     name: str,
#     mixins: tuple[str],
#     path: str,
#     overwrite: bool = None,
# ):
#     """

#     """

#     impl_class_name = f'{name}Impl'
#     init_func_name = 'init_' + '_'.join(re.findall('[A-Z][^A-Z]*', name)).lower()
#     init_file_name = init_func_name.replace('_', '')

#     main_rel_import = f'{name.lower()}'
#     impl_rel_import = ('impl', f'{impl_class_name.lower()}')
#     init_rel_import = ('init', f'{init_file_name}')

#     mixins_import = f'{path}.mixins'
#     main_import = f'{path}.{name.lower()}'
#     impl_import = '.'.join((path,) + impl_rel_import)

#     folder_path = os.path.dirname(importlib.import_module(path).__file__)

#     main_file_path = os.path.join(folder_path, f'{main_rel_import}.py')
#     impl_folder_path = os.path.join(folder_path, impl_rel_import[0])
#     impl_file_path = os.path.join(impl_folder_path, f'{impl_rel_import[1]}.py')
#     init_folder_path = os.path.join(folder_path, init_rel_import[0])
#     init_file_path = os.path.join(init_folder_path, f'{init_rel_import[1]}.py')

#     if not overwrite:
#         for folder_path in (main_file_path, impl_file_path, init_file_path):
#             assert not os.path.exists(folder_path), f'"{folder_path}" already exists'

#     # make sure the mixins exists
#     def gen_mixin_imports():
#         for mixin_name in mixins:

#             mixin_import_path = f'{mixins_import}.{mixin_name.lower()}'

#             mod = importlib.import_module(mixin_import_path)
#             assert hasattr(mod, mixin_name), f'Mixin "{mixin_name}" does not exist'

#             yield mixin_name, mixin_import_path

#     mixins_info = tuple(gen_mixin_imports())

#     # main class
#     # ----------

#     with open(main_file_path, 'w') as f:

#         for mixin_name, mixin_import_path in mixins_info:
#             f.write(f'from {mixin_import_path} import {mixin_name} \n')

#         f.write('\n')

#         extends_from_mixins = ', '.join(mixins)
#         f.write(f'class {name}({extends_from_mixins}):\n\tpass\n')

#     # dataclass implementation
#     # ------------------------

#     if not os.path.exists(impl_folder_path):
#         os.makedirs(impl_folder_path)
#         open(f'{impl_folder_path}/__init__.py', 'a').close()

#     def gen_fields():
#         mod = importlib.import_module(main_import)
#         for class_obj in getattr(mod, name).__mro__:
#             for key, value in class_obj.__dict__.items():
#                 if hasattr(value, '__isabstractmethod__') and getattr(value, '__isabstractmethod__') and isinstance(value, property):
#                     type_hint = typing.get_type_hints(value.fget)['return']
#                     yield key, type_hint.__module__, type_hint.__qualname__

#     fields = tuple(gen_fields())
#     import_type_hints = set((module, cls_name) for _, module, cls_name in fields)

#     with open(impl_file_path, 'w') as f:

#         f.write(f'import dataclass_abc\n')
#         f.write(f'from {main_import} import {name} \n')

#         f.write('\n')

#         for module, cls_name in import_type_hints:
#             if module != 'builtins':
#                 f.write(f'from {module} import {cls_name} \n')

#         f.write('\n')

#         f.write(f'@dataclass_abc.dataclass_abc(frozen=True)\n')
#         f.write(f'class {impl_class_name}({name}):\n')

#         for field_name, module, cls_name in fields:
#             f.write(f'\t{field_name}: {cls_name}\n')

#     # init_function
#     # -------------

#     if not os.path.exists(init_folder_path):
#         os.makedirs(init_folder_path)
#         open(f'{init_folder_path}/__init__.py', 'a').close()

#     with open(init_file_path, 'w') as f:

#         init_func_name = '_'.join(re.findall('[A-Z][^A-Z]*', name)).lower()

#         for module, cls_name in import_type_hints:
#             if module != 'builtins':
#                 f.write(f'from {module} import {cls_name}\n')

#         f.write(f'from {impl_import} import {impl_class_name}\n')

#         f.write('\n')
#         f.write('\n')

#         f.write(f'def init_{init_func_name}(\n')

#         for field_name, module, cls_name in fields:
#             f.write(f'\t\t{field_name}: {cls_name},\n')

#         f.write(f'):\n')

#         f.write(f'\treturn {impl_class_name}(\n')

#         for field_name, module, cls_name in fields:
#             f.write(f'\t\t{field_name}={field_name},\n')

#         f.write(f')\n')
