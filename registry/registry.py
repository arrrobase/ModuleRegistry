from pathlib import Path
import importlib.util

from tabulate import tabulate

from modulebase import ModuleBase


class RegistryError(Exception):
    """Base exception for registry errors."""
    pass


class KeywordMissingError(RegistryError):
    """Raised when a keyword lookup fails."""
    def __init__(self, value):
        default_message = f'"{value}" could not be found in the keyword registry.'
        super().__init__(default_message)


class ModuleMissingError(RegistryError):
    """Raised when a module lookup fails."""
    def __init__(self, value):
        default_message = f'"{value}" could not be found in the module registry.'
        super().__init__(default_message)


class ModuleRegistry:
    """Registry of modules.

    Malformed modules will raise an error at instantiation in `activate()`.
    """
    subclasses = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path_dict = {}
        self.kw_registry = KeywordRegistry()

    def __getitem__(self, item):
        if item not in self:
            raise ModuleMissingError(item)

        return self.path_dict[item]

    def __contains__(self, item):
        return item in self.path_dict

    def __str__(self):
        """Print a pretty table instead of a dict"""
        modules = self.path_dict.values()
        pathspec = self.path_dict.keys()

        return tabulate({'Module Name': modules,
                         'Pathspec': pathspec},
                        headers='keys')

    @classmethod
    def register(cls, module_class, kw=None):
        """Registers a class with the registry.

        :param module_class:
        :param kw: Optional kw to add to the keyword registry
        """
        if not issubclass(module_class, ModuleBase):
            raise TypeError(f'Modules must inherit from "ModuleBase".')

        cls.subclasses.append((module_class, kw))

    @classmethod
    def load_directory(cls, directory):
        """Recursively imports .py files in a directory, in order for modules to be registered.

        Decorators are only called at import time, so if a class is never imported, the module
        will not get registered. Prior to activating the registry, call this method on the
        directories containing the modules.
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError('The directory could not be found.')

        for module in directory.glob('**/*.py'):
            if module.name not in ['__init__.py']:
                spec_root = str(module.relative_to(directory.parent).with_suffix('')).replace('/', '.')
                spec = importlib.util.spec_from_file_location(spec_root, module)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

    def activate(self):
        """Instantiates and adds subclasses to registries.

        Populates two dictionaries where the values are module subclasses. In `kw_registry`, the
        keys are the optionally specified keywords. In `path_dict`, the keys are the spec strings.
        """
        for cls, kw in ModuleRegistry.subclasses:
            module_instance = cls()
            self.path_dict[module_instance.spec] = module_instance

            if kw is not None:
                # add keyword to instance
                module_instance.kw = kw

                if kw in self.kw_registry:
                    print(f'WARN: overriding keyword "{kw}". '
                          f'Replacing "{self.kw_registry[kw].spec}" with "{module_instance.spec}".')
                self.kw_registry[kw] = module_instance

        return self

    def get_by_path(self, key, default=None):
        """Get item from `path_dict`. If default is specified, uses `dict.get`.

        :param str key: Pathspec string.
        :param default: Default return if not found.
        :return: Module instance handle.
        """
        if default is not None:
            return self.path_dict.get(key, default)

        return self[key]

    def get_by_kw(self, key, default=None):
        """Get item from `kw_dict`. If default is specified, uses `dict.get`.

        :param str key: Keyword string.
        :param default: Default return if not found.
        :return: Module instance handle.
        """
        if default is not None:
            return self.path_dict.get(key, default)

        return self.kw_registry[key]


class KeywordRegistry(dict):
    """Registry of keywords"""
    def __getitem__(self, item):
        if item not in self:
            raise KeywordMissingError(item)

        return super().__getitem__(item)

    def __str__(self):
        """Print a pretty table instead of a dict"""
        modules = self.values()
        keywords = self.keys()

        return tabulate({'Module Name': modules,
                         'Keyword': keywords},
                        headers='keys')


def register_module(kw=None):
    """Decorator function to register modules with the registry"""
    def inner(cls):
        ModuleRegistry.register(cls, kw=kw)
        return cls
    return inner
