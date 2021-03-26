# vim:ts=4:sts=4:sw=4:expandtab


from collections import OrderedDict
import datetime
import pathlib
import yaml


from kolejka.judge import config
from kolejka.judge.parse import *
from kolejka.judge.typing import *


__all__ = [ 'ctxyaml_load', 'ctxyaml_dump', ]
def __dir__():
    return __all__


class Loader(yaml.SafeLoader):
    pass


class Dumper(yaml.SafeDumper):
    pass


def _ordered_dict_dump(dumper, val):
    return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, val.items())
Dumper.add_representer(OrderedDict, _ordered_dict_dump)


class _Include:
    def __init__(self, include):
        self.include = include
def _include_load(loader, node):
    return _Include(loader.construct_scalar(node))
Loader.add_constructor('!include', _include_load)


class _File:
    def __init__(self, file):
        self.file = file
def _file_load(loader, node):
    return _File(loader.construct_scalar(node))
def _file_dump(dumper, val):
    return dumper.represent_scalar('!file', str(val.file))
Loader.add_constructor('!file', _file_load)
Dumper.add_representer(_File, _file_dump)


def _load(value, root):
    if value is None:
        return value
    if isinstance(value, (str, bytes, int, float, bool, complex, datetime.datetime,)):
        return value
    if isinstance(value, (dict, OrderedDict,)):
        result = dict()
        for k,v in value.items():
            if isinstance(k, _Include):
                included = ctxyaml_load(root / v) #TODO: k.include
                if isinstance(included, (dict, OrderedDict,)):
                    for kk,vv in included.items():
                        result[kk] = vv
            else:
                result[_load(k, root)] = _load(v, root)
        return result
    if isinstance(value, (list, tuple,)):
        return [ _load(e, root) for e in value ]
    if isinstance(value, _File):
        return (root / value.file).resolve()
    if isinstance(value, _Include):
        return ctxyaml_load(root / value.include)
    raise ValueError('Type {} is not supported by ctxyaml.'.format(type(value)))

def ctxyaml_load(path, root=None):
    path = pathlib.Path(path)
    if root is None:
        root = path.resolve().parent
    else:
        root - pathlib.Path(root)
    value = None
    with path.open() as ctxyaml_file:
        value = yaml.load(ctxyaml_file, Loader=Loader)
    return _load(value, root)


def _dump(value, work_dir, root):
    if value is None:
        return value
    if isinstance(value, (str, bytes, int, float, bool, complex, datetime.datetime,)):
        return value
    if isinstance(value, (dict, OrderedDict,)):
        result = OrderedDict()
        for k,v in value.items():
            result[_dump(k, work_dir, root)] = _dump(v, work_dir, root)
        return result
    if isinstance(value, (list, tuple)):
        return [ _dump(e, work_dir, root) for e in value ]
    if isinstance(value, pathlib.Path):
        return _File((work_dir / value).relative_to(root))
    raise ValueError('Type {} is not supported by ctxyaml.'.format(type(value)))


def ctxyaml_dump(value, path, work_dir=None, root=None, **kwargs):
    path = pathlib.Path(path)
    if root is None:
        root = path.resolve().parent
    else:
        root - pathlib.Path(root)
    if work_dir is None:
        work_dir = path.resolve().parent
    else:
        work_dir = pathlib.Path(work_dir).resolve()
    value = _dump(value, work_dir, root)
    with path.open('w') as ctxyaml_file:
        yaml.dump(value, ctxyaml_file, Dumper=Dumper)
