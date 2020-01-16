from abc import ABC, abstractmethod


class ModuleBase(ABC):
    """Base module class. Defines interface for modules.

    Modules are instantiated by the registry, and thus will raise an error if they
    do not implement all the necessary properties/methods.

    Required properties:
    - name (str): The name of the module
    - phi_labels (list(str)): A list of the keys that are expected in the phi dict.
    - kwarg_Labels (list(str)): A list of the labels that are expected in the keyword argument dict.

    Required methods:
    - get_fn(phis, kwargs): Returns the function that is used by Signal.transform()

    Additionally, if a kw is used when registering the module, then a "parse_kw" method is required.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._spec = f'{self.__class__.__module__}.{self.__class__.__name__}'

    def __call__(self, *, phis: dict, kwargs: dict):
        # force keyword arguments
        self.check_phis_kwargs(phis=phis, kwargs=kwargs)
        return self.get_fn(phis=phis, kwargs=kwargs)

    @property
    @abstractmethod
    def name(self): ...

    @property
    @abstractmethod
    def phi_labels(self): ...

    @property
    @abstractmethod
    def kwarg_labels(self): ...

    @property
    def spec(self): return self._spec

    @abstractmethod
    def get_fn(self, *, phis: dict=None, kwargs: dict=None) : ...

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.spec

    def check_phis_kwargs(self, *, phis: dict=None, kwargs: dict=None):
        """Check that all the proper phis and kwargs are passed in"""
        if not (phis is None and self.phi_labels is None):
            if (phis is None or self.phi_labels is None) or not set(phis.keys()) == set(self.phi_labels):
                raise AttributeError(f'phis not properly specified for module "{repr(self)}".')

        if not (kwargs is None and self.kwarg_labels is None):
            if (kwargs is None or self.kwarg_labels is None) or not set(kwargs.keys()) == set(self.kwarg_labels):
                raise AttributeError(f'kwargs not properly specified for module "{repr(self)}".')
