import typing


class BotRequest:

    def __init__(self):
        self.__command: typing.Optional[str] = None
        self.__args: typing.Optional[typing.List[str]] = None
        self.__message_id: int = 0
        self.__message_text: typing.Optional[str] = None
        self.__is_callback = False

    @property
    def is_callback(self) -> bool:
        return self.__is_callback

    @is_callback.setter
    def is_callback(self, value: bool):
        self.__is_callback = value

    @property
    def command(self) -> typing.Optional[str]:
        return self.__command

    @command.setter
    def command(self, value: typing.Optional[str]):
        self.__command = value

    @property
    def args(self) -> typing.Optional[typing.List[str]]:
        return self.__args

    @args.setter
    def args(self, value: typing.Optional[typing.List[str]]):
        self.__args = value

    @property
    def message_id(self) -> int:
        return self.__message_id

    @message_id.setter
    def message_id(self, value: int):
        self.__message_id = value

    @property
    def message_text(self) -> str:
        return self.__message_text

    @message_text.setter
    def message_text(self, value: str):
        self.__message_text = value


class BotResponse:

    def __init__(self):
        self.__actions: typing.List = list()

    def add_action(self, action):
        self.__actions.append(action)

    @property
    def actions_queue(self) -> typing.Tuple[typing.Any, ...]:
        return tuple(self.__actions)

    def pop_action_at(self, index: int):
        return self.__actions.pop(index)
