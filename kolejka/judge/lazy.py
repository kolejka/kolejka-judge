# vim:ts=4:sts=4:sw=4:expandtab
import sys
assert sys.version_info >= (3, 6)


class DependentExpr:
    def __init__(self, *args, func=None):
        if len(args) > 1 and func is None:
            raise ValueError('Multiple arguments, but no evaluation function given')
        self.names = args
        self.func = func or self.__default_func

    @staticmethod
    def __default_func(x):
        return x

    def evaluate(self, *args):
        return self.func(*args)
