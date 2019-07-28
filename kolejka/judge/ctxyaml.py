import collections
import datetime
import glob
import hashlib
import io
import os
import re
import shutil
import sys
import tempfile
import yaml

__all__ = [ 'HUMAN', 'MACHINE', 'load', 'load_all', 'dump', 'dump_all' ]

class NamespaceDict(collections.OrderedDict):

    def __getitem__(self, key):
        try:
            return super(NamespaceDict, self).__getitem__(key)
        except KeyError:
            if '_factory' in self.__dict__:
                try:
                    value = self._factory(key)
                    self[key] = value
                    return value
                except:
                    pass
            raise

    def __setitem__(self, key, value):
        if value.__class__ in [ dict, collections.OrderedDict ]:
            value = NamespaceDict(value)
        super(NamespaceDict, self).__setitem__(key, value)

    def __getattr__(self, name):
        name = name.replace('_', ' ')
        try:
            return self[name]
        except:
            raise AttributeError()

    def __setattr__(self, name, value):
        if name in self.__dict__ or name[:1] == '_':
            self.__dict__[name] = value
        else:
            name = name.replace('_', ' ')
            self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        elif name in self.__dict__:
            del self.__dict__[name]


def directory_of(file):
    name = getattr(file, 'name', None)
    return name and os.path.abspath(os.path.dirname(name))

def combine(root_dir, current_dir, path):
    if not path:
        return None
    elif os.path.isabs(path):
        drive, tail = os.path.splitdrive(path)
        path = os.path.relpath(tail, drive + os.sep)
        path = os.path.join(root_dir, path)
    else:
        path = os.path.join(current_dir, path)
    matches = glob.glob(path)
    if len(matches) == 0:
        raise Exception("file %s does not exist" % path)
    if len(matches) > 1:
        raise Exception("path %s is ambiguous" % path)
    path = matches[0]
    return path

class Context(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def defaults(self, **kwargs):
        result = Context(**self.__dict__)
        for key, value in kwargs.items():
            if key not in result.__dict__:
                result.__dict__[key] = value
        return result
    def apply(self, **kwargs):
        result = Context(**self.__dict__)
        result.__dict__.update(kwargs)
        return result

class WithContext(object):
    @classmethod
    def create_class(cls, context):
        class Target(cls):
            def __init__(self, *args, **kwargs):
                self.context = context
                super(Target, self).__init__(*args, **kwargs)
        Target.__name__ = cls.__name__
        for tag, regex in getattr(context, 'resolvers', { }).items():
            Target.add_implicit_resolver(tag, regex, None)
        return Target


class Loader(yaml.SafeLoader, WithContext):
    pass

class Dumper(yaml.SafeDumper, WithContext):
    def __init__(self, *args, **kwargs):
        kwargs['allow_unicode'] = True
        kwargs['width'] = sys.maxsize
        kwargs['indent'] = self.context.indent
        kwargs['default_style'] = self.context.default_style
        kwargs['default_flow_style'] = self.context.default_flow_style
        super(Dumper, self).__init__(*args, **kwargs)

for c in "0123456789":
    Dumper.yaml_implicit_resolvers[c] = [ ( t, r ) for ( t, r ) in Dumper.yaml_implicit_resolvers[c] if t != 'tag:yaml.org,2002:timestamp' ]

HUMAN = Context(
    human=True,
    indent=2,
    default_style=None,
    default_flow_style=False,
    resolvers={ }
)

MACHINE = Context(
    human=False,
    indent=1,
    default_style='"',
    default_flow_style=True
)

def load(source, context=HUMAN, **kwargs):
    ctx = context.apply(current_dir=directory_of(source), **kwargs).defaults(root_dir=os.getcwd())
    return yaml.load(source, Loader.create_class(ctx))

def load_all(source, context=HUMAN, **kwargs):
    ctx = context.apply(current_dir=directory_of(source), **kwargs).defaults(root_dir=os.getcwd())
    return yaml.load_all(source, Loader.create_class(ctx))

def dump(value, target=None, context=HUMAN, **kwargs):
    ctx = context.apply(current_dir=directory_of(target), **kwargs).defaults(root_dir=os.getcwd())
    return yaml.dump(value, target, Dumper.create_class(ctx))

def dump_all(values, target=None, context=HUMAN, **kwargs):
    ctx = context.apply(current_dir=directory_of(target), **kwargs).defaults(root_dir=os.getcwd())
    return yaml.dump_all(values, target, Dumper.create_class(ctx))

INCLUDE_TAG = u'!include'

def construct_include(loader, node):
    value = loader.construct_scalar(node)
    path = combine(loader.context.root_dir, loader.context.current_dir, value)
    with open(path, 'r') as source:
        return load(source, loader.context)

Loader.add_constructor(INCLUDE_TAG, construct_include)


class MergeItem(object):
    def __init__(self, content):
        self.content = content

def construct_mapping(loader, node):
    result = NamespaceDict()
    for key_node, value_node in node.value:
        key = loader.construct_scalar(key_node)
        if key_node.tag == INCLUDE_TAG:
            if key:
                raise yaml.MarkedYAMLError(None, None, "non-empty include used as mapping key", key_node.start_mark)
            value = construct_include(loader, value_node)
            if isinstance(value, collections.OrderedDict):
                result.update(value)
            elif isinstance(value, list):
                result = MergeItem(value)
        else:
            value = loader.construct_object(value_node)
            result[key] = value
    return result

Loader.add_constructor(Loader.DEFAULT_MAPPING_TAG, construct_mapping)


def represent_mapping(dumper, value):
    return dumper.represent_mapping(Dumper.DEFAULT_MAPPING_TAG, value.items())

Dumper.add_representer(collections.OrderedDict, represent_mapping)
Dumper.add_representer(NamespaceDict, represent_mapping)


def construct_sequence(loader, node):
    result = [ ]
    for child_node in node.value:
        child = loader.construct_object(child_node)
        if isinstance(child, MergeItem):
            result.extend(child.content)
        else:
            result.append(child)
    return result

Loader.add_constructor(Loader.DEFAULT_SEQUENCE_TAG, construct_sequence)

def construct_any(loader, node):
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_scalar(node)

def represent_any(dumper, tag, value):
    if isinstance(value, dict) or isinstance(value, collections.OrderedDict):
        return dumper.represent_mapping(tag, value)
    if isinstance(value, list):
        return dumper.represent_sequence(tag, value)
    return dumper.represent_scalar(tag, value)

class Scalar(object):
    def __init__(self, **kwargs):
        self.type = kwargs['type']
        self.tag = kwargs['tag']
        if 'load' in kwargs:
            self.load = kwargs['load']
        if 'dump' in kwargs:
            self.dump = kwargs['dump']
        def construct(loader, node):
            return self.load(construct_any(loader, node), loader.context)
        Loader.add_constructor(self.tag, construct)
        def represent(dumper, value):
            return represent_any(dumper, self.tag, self.dump(value, dumper.context))
        Dumper.add_representer(self.type, represent)
    # override any of the following if needed
    def load(self, value, context):
        return self.type(value)
    def dump(self, value, context):
        return str(value)

class Regex(Scalar):
    def __init__(self, **kwargs):
        super(Regex, self).__init__(**kwargs)
        self.regex = re.compile('^' + kwargs['regex'] + '$')

class Implicit(Regex):
    def __init__(self, **kwargs):
        super(Implicit, self).__init__(**kwargs)
        HUMAN.resolvers[self.tag] = self.regex

class RegexLoad(Regex):
    def __init__(self, **kwargs):
        if 'load' in kwargs:
            raise Exception("Cannot manually override load() for RegexLoad scalar types")
        super(RegexLoad, self).__init__(**kwargs)
        self.regex_load = kwargs['regex_load']
    def load(self, value, context):
        return self.regex_load(**self.regex.match(value).groupdict())


def register(*classes, **kwargs):
    type('+'.join([ c.__name__ for c in classes ]), classes, { })(**kwargs)


def load_datetime(year=0, month=0, day=0, hour=0, minute=0, second=0):
    return datetime.datetime(
        year=int(year),
        month=int(month),
        day=int(day),
        hour=int(hour),
        minute=int(minute),
        second=int(second)
    )

register(
    Implicit, RegexLoad,
    type=datetime.datetime,
    tag='!datetime',
    regex='(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\s+(?P<hour>\d{1,2}):(?P<minute>\d{2}):(?P<second>\d{2})',
    regex_load=load_datetime
)


def load_timespan(days=0, hours=0, minutes=0, seconds=0.0):
    return datetime.timedelta(
        days=int(days),
        hours=int(hours),
        minutes=int(minutes),
        seconds=float(seconds)
    )

def dump_timespan(value, context):
    return re.sub(r'(\.[0-9]*[1-9])0*', r'\1', str(value))

register(
    Implicit, RegexLoad,
    type=datetime.timedelta,
    tag='!timespan',
    regex='(?:(?P<days>\d+)\s*(d|day|days))?,?\s*(?P<hours>\d+):(?P<minutes>\d{2})(?::(?P<seconds>\d{2}(?:\.\d+)?))?',
    regex_load=load_timespan,
    dump=dump_timespan
)

class BlobState(object):

    MISSING = "a nonexistent BLOB"
    WRITING = "a BLOB while it is being created"
    HASDATA = "a finished BLOB without a backing file"
    HASFILE = "a finished BLOB with a backing file"


class BlobStateException(Exception):

    pass


class Blob(object):

    def __init__(self, path=None, basename=None, content=None, digest=None):
        self.path = path
        self.basename = basename or (path and os.path.basename(path))
        if self.path:
            with io.open(self.path, 'rb') as stream:
                self.digest = hashlib.sha1(stream.read()).hexdigest()
            self.content = None
            self.state = BlobState.HASFILE
        elif content:
            self.content = content
            if isinstance(self.content, bytes):
                self.digest = hashlib.sha1(self.content).hexdigest()
            else:
                self.digest = hashlib.sha1(self.content.encode()).hexdigest()
            if digest:
                assert self.digest == digest
            self.state = BlobState.HASDATA
        else:
            self.digest = digest
            self.state = BlobState.MISSING

    def load(self):
        if (self.state == BlobState.MISSING):
            if self.digest:
                self.acquire()
            elif self.path:
                with io.open(self.path, 'rb') as stream:
                    self.digest = hashlib.sha1(stream.read()).hexdigest()
                self.content = None
                self.state = BlobState.HASFILE

    def acquire(self):
        if self.state == BlobState.MISSING:
            if not self.digest:
                raise BlobStateException("Cannot download a BLOB without a digest")
            # TODO: replace this with proper downloading of BLOBs by digest
            cachepath = os.path.join('/tmp', self.digest)
            self.path = os.path.join('/tmp', self.basename or self.digest)
            self.basename = os.path.basename(self.path)
            if self.path != cachepath:
                shutil.copy(cachepath, self.path)
            self.state = BlobState.HASFILE
        else:
            raise BlobStateException("Cannot download %s" % self.state)

    def release(self):
        self.load()
        # TODO: replace this with proper uploading of BLOBs
        cachepath = os.path.join('/tmp', self.digest)
        if self.state in [ BlobState.MISSING, BlobState.WRITING ]:
            raise BlobStateException("Cannot upload %s" % self.state)
        elif self.state == BlobState.HASDATA:
            if isinstance(self.content, bytes):
                mode = 'wb'
            else:
                mode = 'wt'
            with io.open(cachepath, mode) as stream:
                stream.write(self.content)
        elif self.state == BlobState.HASFILE:
            if cachepath != self.path:
                shutil.copy(self.path, cachepath)

    def open(self, mode='r', **kwargs):
        if self.state == BlobState.MISSING:
            if self.digest:
                self.acquire()
            elif self.path:
                if 'r' in mode and '+' not in mode:
                    with io.open(self.path, 'rb') as stream:
                        self.digest = hashlib.sha1(stream.read()).hexdigest()
                    self.state = BlobState.HASFILE
                    return io.open(self.path, mode, **kwargs)
                else:
                    stream = io.open(self.path, mode, **kwargs)
                    old_close = stream.close
                    def close():
                        old_close()
                        with io.open(self.path, 'rb') as stream:
                            self.digest = hashlib.sha1(stream.read()).hexdigest()
                        self.state = BlobState.HASFILE
                    stream.close = close
                    self.content = None
                    self.digest = None
                    self.state = BlobState.WRITING
                    return stream
            else:
                if 'r' in mode and '+' not in mode:
                    raise BlobStateException("Cannot read from %s" % self.state)
                if 'b' in mode:
                    stream = io.BytesIO()
                else:
                    stream = io.StringIO()
                old_close = stream.close
                def close():
                    self.content = stream.getvalue()
                    if 'b' in mode:
                        self.digest = hashlib.sha1(self.content).hexdigest()
                    else:
                        self.digest = hashlib.sha1(self.content.encode()).hexdigest()
                    self.state = BlobState.HASDATA
                    old_close()
                stream.close = close
                self.content = None
                self.digest = None
                self.state = BlobState.WRITING
                return stream
        if self.state == BlobState.WRITING:
            raise BlobStateException("Cannot access %s" % self.state)
        if self.state == BlobState.HASDATA:
            if 'w' in mode or '+' in mode:
                raise BlobStateException("Cannot write to %s" % self.state)
            if 'b' in mode:
                if isinstance(self.content, bytes):
                    return io.BytesIO(self.content)
                else:
                    return io.BytesIO(self.content.encode())
            else:
                if isinstance(self.content, bytes):
                    return io.StringIO(self.content.decode())
                else:
                    return io.StringIO(self.content)
        if self.state == BlobState.HASFILE:
            if 'w' in mode or '+' in mode:
                raise BlobStateException("Cannot write to %s" % self.state)
            return io.open(self.path, mode, **kwargs)

    def getvalue(self):
        self.load()
        if self.state in [ BlobState.MISSING, BlobState.WRITING ]:
            raise BlobStateException("Cannot get value of %s" % self.state)
        elif self.state == BlobState.HASDATA:
            return self.content
        elif self.state == BlobState.HASFILE:
            with io.open(self.path, 'rt') as stream:
                return stream.read()

    def getdigest(self):
        self.load()
        if self.state in [ BlobState.MISSING, BlobState.WRITING ]:
            raise BlobStateException("Cannot get digest of %s" % self.state)
        return self.digest

    def move(self, path, basename=None):
        if self.state == BlobState.WRITING:
            if self.path:
                raise BlobStateException("Cannot move %s" % self.state)
        elif self.state == BlobState.HASFILE:
            shutil.move(self.path, path)
        self.path = path
        self.basename = basename or os.path.basename(path)

    def save(self, path=None, basename=None):
        self.load()
        if path and path != self.path:
            self.move(path, basename)
        if self.state in [ BlobState.MISSING, BlobState.WRITING ]:
            if not self.digest:
                raise BlobStateException("Cannot save %s" % self.state)
            self.acquire()
        elif self.state == BlobState.HASDATA:
            if isinstance(self.content, bytes):
                mode = 'wb'
            else:
                mode = 'wt'
            if self.path:
                with io.open(self.path, mode) as stream:
                    stream.write(self.content)
            else:
                with tempfile.NamedTemporaryFile(mode, delete=False) as stream:
                    self.path = stream.name
                    self.basename = os.path.basename(self.path)
                    stream.write(self.content)
            self.content = None
            self.state = BlobState.HASFILE

def load_blob(value, context):
    if context.human:
        return Blob(path=combine(context.root_dir, context.current_dir, value))
    else:
        return Blob(digest=value['hash'], basename=value['name'])

def dump_blob(value, context):
    if context.human:
        if not value.path:
            raise Exception("Cannot choose a path for a BLOB")
        value.save()
        return os.path.relpath(value.path, os.path.dirname(context.current_dir))
    else:
        value.release()
        return dict(hash=value.digest, name=value.basename)

register(
    Scalar,
    type=Blob,
    tag='!file',
    load=load_blob,
    dump=dump_blob
)

from kolejka.judge.limits import Limits
from kolejka.judge.result import Result

register(
    Scalar,
    type=Limits,
    tag='!limits',
)

register(
    Scalar,
    type=Result,
    tag='!result',
)
