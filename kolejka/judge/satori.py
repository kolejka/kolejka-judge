# vim:ts=4:sts=4:sw=4:expandtab


from collections import OrderedDict
import datetime
import math
import pathlib
import re
import traceback


from kolejka.judge import config
from kolejka.judge.ctxyaml import *
from kolejka.judge.parse import *
from kolejka.judge.paths import *
from kolejka.judge.result import *
from kolejka.judge.typing import *


__all__ = [ 'satori_result', ]
def __dir__():
    return __all__


def plain_result(result, prefix='/'):
    ret = dict()
    for k,v in result.items():
        if isinstance(v, dict) or isinstance(v, OrderedDict) or isinstance(v, ResultDict):
            ret.update(plain_result(v, prefix + str(k) + '/'))
        elif isinstance(v, Result):
            ret.update(plain_result(v.yaml, prefix + str(k) + '/'))
        else:
            ret[prefix + str(k)] = v
    return ret

def str_operator(v):
    if isinstance(v, pathlib.Path):
        with v.open('rb') as vf:
            content = vf.read(config.SATORI_STRING_LENGTH)
            try:
                content = str(content, 'utf8').rstrip()
                if content:
                    content += '\n'
                return content
            except UnicodeDecodeError:
                return repr(content)[2:-1][:config.SATORI_STRING_LENGTH]
    if isinstance(v, list):
        return ' '.join([e for e in [str_operator(e) for e in v] if e])[:config.SATORI_STRING_LENGTH].rstrip('\n')
    if isinstance(v, bytes):
        return str(v, 'utf8')[:config.SATORI_STRING_LENGTH]
    return str(v)[:config.SATORI_STRING_LENGTH]

def float_operator(v):
    return float(str_operator(v))

def int_operator(v):
    return int(math.floor(float_operator(v)+0.5))

def milisec_operator(v):
    s = str_operator(v)
    return int(parse_time(str_operator(v)).total_seconds() * 1000)

def path_match(pattern, path):
    rep = ''
    i=0;
    while i < len(pattern):
        if pattern[i] == '*' and i+1 < len(pattern) and pattern[i+1] == '*':
            rep += '.*'
            i += 2;
        else:
            if pattern[i] == '*':
                rep += '[^/]*'
            elif pattern[i] == '?':
                rep += '[^/]'
            else:
                rep += '['+pattern[i]+']'
            i += 1;
    #TODO: match []?
    return bool(re.fullmatch(rep, path))

def result_access(result, val):
    operator = None
    val = val.split(':')
    if len(val) > 1:
        operator = val[0]
        val = ':'.join(val[1:])
    else:
        val = val[0]
    val = val.split(',')
    vs = list()
    for k,v in result.items():
        for m in val:
            if path_match(m, k):
                vs.append(v)
    if len(vs) == 0:
        return None
    if operator == 'str':
        return str_operator(vs)
    elif operator == 'float':
        return float_operator(vs)
    elif operator == 'int':
        return int_operator(vs)
    elif operator == 'milisec':
        return milisec_operator(vs)
    if len(vs) > 1:
        raise ValueError
    vs = vs[0]
    return vs

def satori_result_path(key, res, result_dir):
    new = result_dir.resolve() / key / res.name
    new.parent.mkdir(parents=True)
    new.symlink_to(res)
    return new

def satori_result(test, result, result_dir):
    satori = ResultDict()
    satori.set_status(result.status)
    presult = plain_result(result)
    for key,val in test.get('kolejka', dict()).get('satori', dict()).get('result', dict()).items():
        res = result_access(presult, val)
        if res is not None:
            if isinstance(res, pathlib.Path):
                res = satori_result_path(key, res, result_dir / config.SATORI_RESULT)
            else:
                res = str_operator(res)
            if key == 'status':
                satori.set_status(res)
            else:
                satori.set(key, res)
    result.set('satori', satori)
