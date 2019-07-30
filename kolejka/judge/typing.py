# vim:ts=4:sts=4:sw=4:expandtab
from collections import OrderedDict
from copy import deepcopy
from typing import Any, Callable, Dict, Generator, List, Optional, Sequence, Set, Tuple, Union


from kolejka.judge import config

__all__ = [ 'AbstractCommand', 'AbstractTask', 'AbstractSystem', 'AbstractLimits', 'AbstractResult', 'AbstractPath', 'Resolvable', 'default_kwargs', 'nononedict', ]
__all__ += [ 'Any', 'Callable', 'Dict', 'Generator', 'List', 'Optional', 'Sequence', 'Set', 'Tuple', 'Union', ]
def __dir__():
    return __all__


class AbstractCommand:
    pass


class AbstractTask:
    pass


class AbstractSystem:
    pass


class AbstractLimits:
    pass


class AbstractResult:
    pass


class AbstractPath:
    pass


Resolvable = Union[str, AbstractPath, Sequence[Union[str, AbstractPath]]]


class default_kwargs:
    def __init__(self, fn):
        self.fn = fn

    def __set_name__(self, owner, name):
        cls = owner
        fn = self.fn

        def fun(self, *args, **kwargs):
            for key, val in cls.__dict__.items():
                if key.startswith('DEFAULT_'):
                    key = key[8:].lower()
                    if val is not None:
                        kwargs[key] = kwargs.get(key, val)
            return fn(self, *args, **kwargs)
        setattr(owner, name, fun)

class nononedict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def __setitem__(self, key, val):
        if val is not None:
            super().__setitem__(key, val)
