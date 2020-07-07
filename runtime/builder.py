import typing

import telegram

from runtime.middleware import Middleware, CommandsMiddleware
from runtime.options import Options


class ApplicationBuilder:

    def __init__(self):
        self.__bot = None
        self.__timeout = 0
        self.__updates_limit = 0
        self.__components: typing.List[typing.Tuple[typing.Type[Middleware], typing.Callable[[], Options]]] = list()

    def use_bot_token(self, token: str):
        self.__bot = telegram.Bot(token)

    @property
    def timeout(self) -> int:
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout: int):
        self.__timeout = timeout

    @property
    def bot(self) -> telegram.Bot:
        return self.__bot

    @property
    def updates_limit(self) -> int:
        return self.__updates_limit

    @updates_limit.setter
    def updates_limit(self, limit: int):
        self.__updates_limit = limit

    def use_middleware(self, middleware: typing.Type[Middleware], configurator: typing.Callable[[], Options] = None):
        self.__components.append((middleware, configurator))

    def use_commands(self, configurator: typing.Callable[[], Options]):
        self.__components.append((CommandsMiddleware, configurator))

    def build(self) -> typing.Tuple[typing.Tuple[typing.Type[Middleware], typing.Callable[[], Options]], ...]:
        return tuple(self.__components)
