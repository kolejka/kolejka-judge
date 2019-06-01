from typing import Optional, Tuple

from kolejka.judge.exceptions import PrerequisiteException


class TaskBase:
    name = None

    def execute(self, environment) -> Tuple[Optional[str], Optional[object]]:
        raise NotImplementedError

    def set_name(self, name):
        self.name = name

    def prerequisites(self):
        return []

    def verify_prerequisites(self, environment):
        for prerequisite in self.prerequisites():
            if not prerequisite(environment):
                raise PrerequisiteException("Prerequisite `{}` not satisfied for {}".format(prerequisite, self.name))
