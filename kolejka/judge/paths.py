# vim:ts=4:sts=4:sw=4:expandtab
import pathlib
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.typing import *
from kolejka.judge.ctxyaml import Blob

__all__ = [ 'PathBase', 'InputPath', 'OutputPath', 'RelativePath', 'get_input_path', 'get_output_path', 'get_relative_path' ]
def __dir__():
    return __all__


_inner_path = None
_inner_relative = None
_inner_input = None
_inner_output = None
def _path(obj):
    return _inner_path(obj)
def _relative(obj):
    return _inner_relative(obj)
def _input(obj):
    return _inner_input(obj)
def _output(obj):
    return _inner_output(obj)

class PathBase(AbstractPath):
    @property
    def path(self):
        return _path(self._path)
    @property
    def parts(self):
        return self._path.parts
    @property
    def name(self):
        return self._path.name
    @property
    def suffix(self):
        return self._path.suffix
    @property
    def suffixes(self):
        return self._path.suffixes
    @property
    def stem(self):
        return self._path.stem
    def match(self, pattern):
        return self._path.match(pattern)


class RelativePath(PathBase):
    def __init__(self, *args):
        self._path = pathlib.PurePath(*[ _path(arg) for arg in args ])
        if self._path.is_absolute():
            raise ValueError(repr(args)+" is not a relative path")

    def __str__(self):
        return str(_path(self))
    def __bytes__(self):
        return bytes(_path(self))
    def __repr__(self):
        return 'RELATIVE:'+str(_path(self))
    def __hash__(self):
        return hash(_path(self))

    def __truediv__(self, key):
        return _relative( _path(self) / _path(_relative(key)) )
    @property
    def parent(self):
        return _relative( _path(self).parent )


class InputPath(PathBase):
    def __init__(self, *args):
        self._path = pathlib.PurePath(*[ _path(arg) for arg in args ])
        if not self._path.is_absolute():
            raise ValueError(repr(args)+" is not an input path")

    def __str__(self):
        return str(_path(self))
    def __bytes__(self):
        return bytes(_path(self))
    def __repr__(self):
        return 'INPUT:'+str(_path(self))
    def __hash__(self):
        return hash(_path(self))

    def __truediv__(self, key):
        return _input( _path(self) / _path(_relative(key)) )
    @property
    def parent(self):
        return _input( _path(self).parent )


class OutputPath(PathBase):
    def __init__(self, *args):
        self._path = pathlib.PurePath(*[ _path(arg) for arg in args ])
        if self._path.is_absolute():
            raise ValueError(repr(args)+" is not an output path")

    def __str__(self):
        return str(_path(self))
    def __bytes__(self):
        return bytes(_path(self))
    def __repr__(self):
        return 'OUTPUT:'+str(_path(self))
    def __hash__(self):
        return hash(_path(self))

    def __truediv__(self, key):
        return _output( _path(self) / _path(_relative(key)) )
    @property
    def parent(self):
        return _output( _path(self).parent )


class _InnerPath:
    def __call__(self, obj):
        for cls in [ RelativePath, InputPath, OutputPath, ]:
            if isinstance(obj, cls):
                return pathlib.PurePath(obj._path)
        for cls in [ Blob, ]:
            if isinstance(obj, cls):
                return pathlib.PurePath(obj.path)
        for cls in [ str, bytes, pathlib.PurePath,]:
            if isinstance(obj, cls):
                return pathlib.PurePath(obj)
        raise ValueError(repr(obj)+" is not a path")
_inner_path = _InnerPath()
class _RelativePath:
    def __call__(self, obj):
        for cls in [ RelativePath, ]:
            if isinstance(obj, cls):
                return RelativePath(obj._path)
        for cls in [ str, bytes, pathlib.PurePath,]:
            if isinstance(obj, cls):
                return RelativePath(obj)
        raise ValueError(repr(obj)+" is not a relative path")
_inner_relative = _RelativePath()
class _InputPath:
    def __call__(self, obj):
        for cls in [ InputPath, ]:
            if isinstance(obj, cls):
                return InputPath(obj._path)
        for cls in [ Blob, ]:
            if isinstance(obj, cls):
                return InputPath(obj.path)
        for cls in [ str, bytes, pathlib.PurePath,]:
            if isinstance(obj, cls):
                return InputPath(obj)
        raise ValueError(repr(obj)+" is not an input path")
_inner_input = _InputPath()
class _OutputPath:
    def __call__(self, obj):
        for cls in [ OutputPath, ]:
            if isinstance(obj, cls):
                return OutputPath(obj._path)
        for cls in [ str, bytes, pathlib.PurePath,]:
            if isinstance(obj, cls):
                return OutputPath(obj)
        raise ValueError(repr(obj)+" is not an output path")
_inner_output = _OutputPath()


def get_input_path(path):
    if path is None:
        return InputPath('/dev/null')
    if isinstance(path, InputPath):
        return path
    if isinstance(path, OutputPath):
        return path
    if isinstance(path, RelativePath):
        return path
    return InputPath(path)

def get_output_path(path):
    if path is None:
        return path
    if isinstance(path, InputPath):
        return path
    if isinstance(path, OutputPath):
        return path
    if isinstance(path, RelativePath):
        return path
    return OutputPath(path)

def get_relative_path(path):
    if path is None:
        return path
    if isinstance(path, InputPath):
        return path
    if isinstance(path, OutputPath):
        return path
    if isinstance(path, RelativePath):
        return path
    return RelativePath(path)
