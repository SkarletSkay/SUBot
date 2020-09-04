from typing import Dict, Callable, List
from runtime.context import Context


class Options:

    def __init__(self):
        self.__opt_dict: Dict[str, object] = dict()

    def __setitem__(self, key: str, value: object):
        self.__opt_dict[key] = value

    def __getitem__(self, item: str):
        if item not in self.__opt_dict:
            return None
        return self.__opt_dict[item]


class CommandsOptions(Options):

    @property
    def suppress_command_literal(self):
        if self["__suppress_command_literals__"] is None:
            return False
        return self["__suppress_command_literals__"]

    @suppress_command_literal.setter
    def suppress_command_literal(self, value: bool):
        self["__suppress_command_literals__"] = value

    def use_error_handler(self, error_handler: Callable[[Exception, Context], None]):
        self["__error_handler__"] = error_handler

    def use_commands_modules(self, modules: List):
        self["__modules__"] = modules
