# vim:ts=4:sts=4:sw=4:expandtab


import os
import pathlib
import time


__all__ = [ 'info', 'ppid', 'pids', 'ppids', 'children', 'descendants' ]
def __dir__():
    return __all__


page_size = int(os.sysconf("SC_PAGE_SIZE"))
clock_ticks = int(os.sysconf("SC_CLK_TCK"))

def info(pid):
    proc = pathlib.Path('/proc/'+str(pid))
    with pathlib.Path('/proc/uptime').open() as uptime_file:
        uptime = float(uptime_file.read().strip().split()[0])
    try:
        with ( proc / 'stat' ).open() as stat_file:
            stat = stat_file.read().strip().split()
        with ( proc / 'statm' ).open() as statm_file:
            statm = statm_file.read().strip().split()
        with ( proc / 'io' ).open() as io_file:
            io = dict( [ (k.strip().lower(), int(v.strip())) for k,v in [ l.split(':') for l in io_file.read().strip().split('\n') ] ] )

        result = dict()
        result['ppid'] = int(stat[3])
        result['cpu_user'] = int(stat[13]) / clock_ticks
        result['cpu_sys'] = int(stat[14]) / clock_ticks
        result['rss'] = int(statm[1]) * page_size
        result['threads'] = int(stat[19])
        result['read'] = io['rchar']
        result['write'] = io['wchar']
        result['real_time'] = uptime - int(stat[21]) / clock_ticks
        return result
    except:
        return None

def ppid(pid):
    proc = pathlib.Path('/proc/'+str(pid))
    try:
        with ( proc / 'stat' ).open() as stat_file:
            stat = stat_file.read().strip().split()
            return int(stat[3])
    except:
        return None

def pids():
    proc = pathlib.Path('/proc')
    return [ int(p.name) for p in proc.iterdir() if p.is_dir() and not p.is_symlink() and p.name.isdigit() ] 

def ppids():
    result = dict()
    for p in pids():
        pp = ppid(p)
        if pp is not None:
            result[p] = pp
    return result

def children(pid):
    return [ p for p in pids() if ppid(p) == pid ]

def descendants(pid):
    parents = ppids()
    children = dict([ (p,list()) for p in parents.values() ])
    for child, parent in parents.items():
        children[parent].append(child)
    new_descendants = [ pid ]
    all_descendants = []
    while new_descendants:
        active = new_descendants
        new_descendants = []
        for p in active:
            all_descendants += children.get(p,[])
            new_descendants += children.get(p,[])
    return all_descendants
