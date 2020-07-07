import typing


class User:

    def __init__(self):
        self.__username: str = ""
        self.__first_name: str = ""
        self.__last_name: str = ""
        self.__user_id: int = 0
        self.__roles: typing.List[str] = list()

    @property
    def username(self) -> str:
        return self.__username

    @username.setter
    def username(self, value: str):
        self.__username = value

    @property
    def first_name(self) -> str:
        return self.__first_name

    @first_name.setter
    def first_name(self, value: str):
        self.__first_name = value

    @property
    def last_name(self) -> str:
        return self.__last_name

    @last_name.setter
    def last_name(self, value: str):
        self.__last_name = value

    @property
    def id(self) -> int:
        return self.__user_id

    @id.setter
    def id(self, value: int):
        self.__user_id = value



    def add_role(self, role: str):
        self.__roles.append(role)

    def in_role(self, role: str) -> bool:
        return role in self.__roles
