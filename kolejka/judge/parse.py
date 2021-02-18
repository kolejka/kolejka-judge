# vim:ts=4:sts=4:sw=4:expandtab


import datetime


from kolejka.judge import config


__all__ = [ 'parse_time', 'unparse_time', 'parse_memory', 'unparse_memory', 'parse_bool', 'unparse_bool' ]
def __dir__():
    return __all__


def parse_float_with_modifiers(x, modifiers):
    if isinstance(x, float):
        return x
    if isinstance(x, int):
        return float(x)
    modifier = 1
    x = str(x).strip()
    while len(x) > 0 and x[-1] in modifiers :
        modifier *= modifiers[x[-1]]
        x = x[:-1]
    return float(x) * modifier


def parse_time(x) :
    if x is not None:
        if isinstance(x, datetime.timedelta):
            return x
        return datetime.timedelta(seconds=parse_float_with_modifiers(x, {
            'W' : 60*60*24*7,
            'D' : 60*60*24,
            'H' : 60*60,
            'M' : 60,
            's' : 1,
            'm' : 10**-3,
            'µ' : 10**-6,
            'n' : 10**-9,
        }))

def unparse_time(x) :
    if x is not None:
        assert isinstance(x, datetime.timedelta)
        return str(x.total_seconds())+'s'


def parse_memory(x):
    if x is not None:
        return int(round(parse_float_with_modifiers(x, {
            'b' : 1,
            'B' : 1,
            'k' : 1024,
            'K' : 1024,
            'm' : 1024**2,
            'M' : 1024**2,
            'g' : 1024**3,
            'G' : 1024**3,
            't' : 1024**4,
            'T' : 1024**4,
            'p' : 1024**5,
            'P' : 1024**5,
        })))

def unparse_memory(x):
    if x is not None:
        assert isinstance(x, int)
        return str(x)+'b'

def parse_bool(x):
    if x is not None:
        if isinstance(x, bool):
            return x
        return str(x).lower().strip() not in [ 'false', 'no', '0' ]

def unparse_bool(x):
    if x is not None:
        assert isinstance(x, bool)
        return ('true' if x else 'false')
