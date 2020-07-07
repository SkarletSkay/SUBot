import typing

from runtime.context import Context


class Options:

    def __init__(self):
        self.__opt_dict: typing.Dict[str, object] = dict()

    def __setitem__(self, key: str, value: object):
        self.__opt_dict[key] = value

    def __getitem__(self, item: str):
        if item not in self.__opt_dict:
            return None
        return self.__opt_dict[item]


class CommandsOptions(Options):

    def use_error_handler(self, error_handler: typing.Callable[[Exception, Context], None]):
        self["__error_handler__"] = error_handler

    def use_commands_modules(self, modules: typing.List):
        self["__modules__"] = modules
