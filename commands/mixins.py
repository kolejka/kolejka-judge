from validators import UsedTimePostcondition, UsedMemoryPostcondition


class SolutionMixin:
    def __init__(self, *args, **kwargs):
        self.limits = {}
        super().__init__(*args, **kwargs)

    def postconditions(self):
        conditions = []
        if 'time' in self.limits:
            conditions.append((UsedTimePostcondition(self.limits['time']), 'TLE'))
        if 'memory' in self.limits:
            conditions.append((UsedMemoryPostcondition(self.limits['memory']), 'MEM'))
        return conditions
