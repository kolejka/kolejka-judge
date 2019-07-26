# vim:ts=4:sts=4:sw=4:expandtab
from copy import deepcopy
import sys
from typing import Any, Callable, Dict, Generator, List, Optional, Sequence, Set, Tuple, Union
assert sys.version_info >= (3, 6)


__all__ = [ 'AbstractCommand', 'AbstractTask', 'AbstractSystem', 'AbstractLimits', 'AbstractResult', 'AbstractPath', 'Resolvable', 'default_kwargs', ]
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
                    kwargs[key] = kwargs.get(key, deepcopy(val))
            return fn(self, *args, **kwargs)
        setattr(owner, name, fun)
