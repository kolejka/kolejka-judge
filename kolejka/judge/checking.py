# coding=utf-8
from typing import Dict

from kolejka.judge.environments import ExecutionEnvironment
from kolejka.judge.commands.base import CommandBase
from kolejka.judge.tasks.java import Task


class Checking:
    def __init__(self, environment: ExecutionEnvironment):
        self.steps: Dict[str, CommandBase or Task] = {}
        self.environment = environment

    # requires python3.6 for kwargs order preservation
    def add_steps(self, *args, **kwargs):
        if len(args) > 0 and len(kwargs) > 0:
            raise TypeError("It is impossible to detect the order of the steps when using both args and kwargs.")

        steps = {}
        if len(args) > 0:
            for i, arg in enumerate(args):
                steps[str(i)] = arg
        else:
            steps = kwargs

        for name, func in steps.items():
            if name in self.steps:
                raise TypeError("Step {} has already been added".format(name))

        for name, func in steps.items():
            self.steps[name] = func

    def run(self):
        return self.environment.run_steps(self.steps)

    def format_result(self, result):
        formatted_result = {}
        for key, value in result.items():
            formatted_result[key] = self.environment.format_execution_status(value)

        return formatted_result
