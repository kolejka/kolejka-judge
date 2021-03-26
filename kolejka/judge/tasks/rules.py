# vim:ts=4:sts=4:sw=4:expandtab

import re

from kolejka.judge import config
from kolejka.judge.parse import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.tasks.base import *
from kolejka.judge.systems.base import *


__all__ = [ 'RulesTask', 'SolutionSourceRulesTask', 'SolutionBuildRulesTask' ]
def __dir__():
    return __all__

def regex_count(description, text, flags):
    m = re.fullmatch(r'(.*?)(<|<=|=|>=|>)\s*([0-9]+)\s*', description)
    if m:
        r = m[1].strip()
        e = m[2]
        c = int(m[3])
        rc = len(re.findall(r, text, flags))
        if ( e == '<' and rc >= c) or ( e == '<=' and rc > c) or ( e == '=' and rc != c) or ( e == '>=' and rc < c) or ( e == '>' and rc <= c):
            return False
    return True

class RulesTask(TaskBase):
    DEFAULT_RESULT_ON_ERROR='RUL'
    @default_kwargs
    def __init__(self, target, max_size=None, regex_count=None, regex_count_flags=re.IGNORECASE|re.MULTILINE|re.DOTALL, **kwargs):
        super().__init__(**kwargs)
        self.target = get_output_path(target)
        self.max_size = parse_memory(max_size)
        if not regex_count:
            self.regex_count = []
        else:
            if isinstance(regex_count, str):
                regex_count = regex_count.split(',')
            self.regex_count = regex_count
        self.regex_count_flags = regex_count_flags
    
    def execute(self):
        if self.max_size:
            used_size = sum(
                    [ self.resolve_path(f).stat().st_size for f in self.find_files(self.target) ]
                    )
            if used_size > self.max_size:
                self.set_result(self.result_on_error)
        if self.regex_count:
            text = '\n'.join(
                    [ self.resolve_path(f).open().read() for f in self.find_files(self.target) ]
                    )
            for rc in self.regex_count:
                if not regex_count(rc, text, self.regex_count_flags):
                    self.set_result(self.result_on_error)
        return self.result


class SolutionSourceRulesTask(RulesTask):
    DEFAULT_TARGET=config.SOLUTION_SOURCE
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SolutionBuildRulesTask(RulesTask):
    DEFAULT_TARGET=config.SOLUTION_BUILD
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
