from typing import Dict, Optional
from telegram import User, Chat


class Session:

    def __init__(self, user: User, chat: Chat):
        self.__user = user
        self.__chat = chat
        self.__data: Dict[str, object] = dict()

    @property
    def identifier(self) -> int:
        return hash(self.__chat.id)

    def __getitem__(self, item: str):
        if item not in self.__data:
            return None
        return self.__data[item]

    def __setitem__(self, key: str, value):
        self.__data[key] = value

    @property
    def user(self) -> User:
        return self.__user

    @property
    def chat(self) -> Chat:
        return self.__chat


class SessionControl:

    def __init__(self):
        self.__context_dict: Dict[object, Session] = dict()

    def get_session(self, key) -> Optional[Session]:
        if key not in self.__context_dict:
            return None
        return self.__context_dict[key]

    def set_session(self, key, value):
        self.__context_dict[key] = value
