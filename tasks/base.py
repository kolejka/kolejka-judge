from typing import Optional, Tuple

from exceptions import PrerequisiteException


class Task:
    def execute(self, name, environment) -> Tuple[Optional[str], Optional[object]]:
        raise NotImplementedError

    def prerequisites(self):
        return []

    def verify_prerequisites(self, environment):
        for prerequisite in self.prerequisites():
            if not prerequisite(environment):
                raise PrerequisiteException("Prerequisite `{}` not satisfied".format(prerequisite))
