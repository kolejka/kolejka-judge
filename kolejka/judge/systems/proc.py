# vim:ts=4:sts=4:sw=4:expandtab


import os
import pathlib
import time


__all__ = [ 'proc_info', ]
def __dir__():
    return __all__


page_size = int(os.sysconf("SC_PAGE_SIZE"))
clock_ticks = int(os.sysconf("SC_CLK_TCK"))

def proc_info(pid):
    proc = pathlib.Path('/proc/'+str(pid))
    if not proc.is_dir():
        return None
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
