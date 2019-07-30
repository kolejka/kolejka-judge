# vim:ts=4:sts=4:sw=4:expandtab
from collections import OrderedDict
import datetime
import pathlib
import yaml

from kolejka.judge import config
from kolejka.judge.parse import *
from kolejka.judge.typing import *

class Loader(yaml.SafeLoader):
    pass
class Dumper(yaml.SafeDumper):
    pass

__all__ = [ 'ctxyaml_load', 'ctxyaml_dump', ]
def __dir__():
    return __all__


def _ordered_dict_dump(dumper, val):
    return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, val.items())
Dumper.add_representer(OrderedDict, _ordered_dict_dump)

class _Include:
    def __init__(self, include):
        self.include = include
def _include_dump(dumper, val):
    return dumper.represent_scalar('!include')
def _include_load(loader, node):
    return _Include(loader.construct_scalar(node))
Dumper.add_representer(_Include, _include_dump)
Loader.add_constructor('!include', _include_load)

class _File:
    def __init__(self, file):
        self.file = file
def _file_dump(dumper, val):
    return dumper.represent_scalar('!file', '%s'%(val.file))
def _file_load(loader, node):
    return _File(loader.construct_scalar(node))
Dumper.add_representer(_File, _file_dump)
Loader.add_constructor('!file', _file_load)


def _load(value, root):
    if value is None:
        return value
    for t in [ str, bytes, int, float, bool, complex, ]:
        if isinstance(value, t):
            return value
    for t in [ OrderedDict, dict ]:
        if isinstance(value, t):
            c = t()
            for k,v in value.items():
                if isinstance(k, _Include):
                    d = ctxyaml_load(root/v)
                    if isinstance(d, dict) or isinstance(d, OrderedDict):
                        for kk,vv in d.items():
                            c[kk] = vv
                else:
                    c[_load(k, root)] = _load(v, root)
            return c
    for t in [ list, tuple, ]:
        if isinstance(value, t):
            return t([_load(e, root) for e in value])
    if isinstance(value, _File):
        return (root / value.file).resolve()
    if isinstance(value, _Include):
        return ctxyaml_load(root / value.include)
    raise ValueError('Type {} is not supported by ctxyaml.'.format(type(value)))

def ctxyaml_load(path, root=None):
    path = pathlib.Path(path).resolve()
    if root is None:
        root = path.parent
    value = None
    with path.open() as ctxyaml_file:
        value = yaml.load(ctxyaml_file, Loader=Loader)
    return _load(value, root)

def _dump(value, output_dir, root):
    if value is None:
        return value
    for t in [ str, bytes, int, float, bool, complex, ]:
        if isinstance(value, t):
            return value
    for t in [ OrderedDict, dict ]:
        if isinstance(value, t):
            c = t()
            for k,v in value.items():
                c[_dump(k, output_dir, root)] = _dump(v, output_dir, root)
            return c
    for t in [ list, tuple, ]:
        if isinstance(value, t):
            return t([_dump(e, output_dir, root) for e in value])
    if isinstance(value, pathlib.Path):
        try:
            return _File((output_dir / value).resolve().relative_to(root))
        except:
            return None
    raise ValueError('Type {} is not supported by ctxyaml.'.format(type(value)))


def ctxyaml_dump(value, output_dir, path, root=None, **kwargs):
    output_dir = pathlib.Path(output_dir).resolve()
    path = pathlib.Path(path).resolve()
    if root is None:
        root = path.parent
    value = _dump(value, output_dir, root)
    with path.open('w') as ctxyaml_file:
        yaml.dump(value, ctxyaml_file, Dumper=Dumper)
