from telegram import User, Chat, Bot
from typing import List, Tuple, Dict


class Configuration:

    def __init__(self):
        self.__commands: List[type] = []
        self.__holding_log: Dict[Tuple[int, int, type], int] = {}
        self.__bot = None
        self.__timeout = 0
        self.__updates_limit = 0

    def get_bot(self) -> Bot:
        return self.__bot

    def use_bot_token(self, token: str):
        self.__bot = Bot(token)

    def get_commands(self) -> Tuple[type]:
        return tuple(self.__commands)

    def get_holding_log(self) -> dict:
        return self.__holding_log

    @property
    def timeout(self) -> int:
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout: int):
        self.__timeout = timeout

    @property
    def updates_limit(self) -> int:
        return self.__updates_limit

    @updates_limit.setter
    def updates_limit(self, limit: int):
        self.__updates_limit = limit

    def use_command(self, command_type: type):
        self.__commands.append(command_type)

    def hold_for(self, user_id: int, chat_id: int, command: type, duration: int):
        self.__holding_log[(user_id, chat_id, command)] = duration

    def hold_forever(self, user_id: int, chat_id: int, command: type):
        self.__holding_log[(user_id, chat_id, command)] = -1

    def is_holding(self, user_id: int, chat_id: int, command: type) -> bool:
        if (user_id, chat_id, command) not in self.__holding_log:
            return False
        return self.__holding_log[(user_id, chat_id, command)] != 0

    def decrease_holding(self, user_id: int, chat_id: int, command: type):
        if (user_id, chat_id, command) in self.__holding_log:
            self.__holding_log[(user_id, chat_id, command)] -= 1

    def unhold(self, user_id: int, chat_id: int, command: type):
        self.__holding_log[(user_id, chat_id, command)] = 0
