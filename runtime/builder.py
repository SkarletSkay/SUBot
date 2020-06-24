from typing import List, Callable, Union, Tuple, Optional, overload
from telegram import Bot
from runtime.context import Context
from runtime.options import Options
from runtime.middleware import CommandsMiddleware


class ApplicationBuilder:

    def __init__(self):
        self.__bot = None
        self.__timeout = 0
        self.__updates_limit = 0
        self.__components: List[Tuple[Union[type, Callable[[Context], bool]], Optional[Options]]] = list()

    def use_bot_token(self, token: str):
        self.__bot = Bot(token)

    @property
    def timeout(self) -> int:
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout: int):
        self.__timeout = timeout

    @property
    def bot(self) -> Bot:
        return self.__bot

    @property
    def updates_limit(self) -> int:
        return self.__updates_limit

    @updates_limit.setter
    def updates_limit(self, limit: int):
        self.__updates_limit = limit

    def use_middleware(self, middleware: type, options: Optional[Options]):
        self.__components.append((middleware, options))

    def use_commands(self, options_configurator: Optional[Callable[[], Options]]):
        if options_configurator is None:
            self.__components.append((CommandsMiddleware, None))
        else:
            self.__components.append((CommandsMiddleware, options_configurator()))

    def build(self) -> List:
        return self.__components
