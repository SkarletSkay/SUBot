import typing


class PropertyDefinition:

    def __init__(self):
        self.__name = ""
        self.__optional = False
        self.__hint = ""
        self.__type = "str"
        self.__text = None

    @property
    def type(self) -> str:
        return self.__type

    @type.setter
    def type(self, value: str):
        self.__type = value

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def optional(self) -> bool:
        return self.__optional

    @optional.setter
    def optional(self, value: bool):
        self.__optional = value

    @property
    def hint(self) -> str:
        return self.__hint

    @hint.setter
    def hint(self, value: str):
        self.__hint = value

    @property
    def text(self) -> str:
        return self.__text

    @text.setter
    def text(self, value: str):
        self.__text = value


class CommandModelDefinition:

    def __init__(self):
        self.__command_class = None
        self.__handler_class = None
        self.__req_properties = list()
        self.__optional_properties = list()
        self.__entry_command = None
        self.__confirm_cancel = True
        self.__confirm_send = True
        self.__fill_mode = "auto"

    @property
    def fill_mode(self) -> str:
        return self.__fill_mode

    @fill_mode.setter
    def fill_mode(self, value: str):
        self.__fill_mode = value

    @property
    def confirm_send(self) -> bool:
        return self.__confirm_send

    @confirm_send.setter
    def confirm_send(self, value: bool):
        self.__confirm_send = value

    @property
    def command_class(self) -> typing.Type:
        return self.__command_class

    @command_class.setter
    def command_class(self, value: typing.Type):
        self.__command_class = value

    @property
    def handler_class(self) -> typing.Type:
        return self.__handler_class

    @handler_class.setter
    def handler_class(self, value: typing.Type):
        self.__handler_class = value

    @property
    def required_properties(self) -> typing.List[PropertyDefinition]:
        return self.__req_properties

    @required_properties.setter
    def required_properties(self, value: typing.List[PropertyDefinition]):
        self.__req_properties = value

    @property
    def optional_options(self) -> typing.List[PropertyDefinition]:
        return self.__optional_properties

    @optional_options.setter
    def optional_options(self, value: typing.List[PropertyDefinition]):
        self.__optional_properties = value

    @property
    def entry_command(self) -> str:
        return self.__entry_command

    @entry_command.setter
    def entry_command(self, value: str):
        self.__entry_command = value

    @property
    def confirm_cancel(self) -> bool:
        return self.__confirm_cancel

    @confirm_cancel.setter
    def confirm_cancel(self, value: bool):
        self.__confirm_cancel = value
