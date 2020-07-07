import typing

from runtime.commands import ModelCommandBase, CommandResult


class Request:

    def __init__(self):
        self.title = ""
        self.description = ""
        self.category = ""
        self.notify = ""


class Handler(ModelCommandBase):

    def on_complete(self, model: Request) -> typing.Union[CommandResult, str]:
        return self.no_message()

    def on_property_set(self, model: Request, property_name: str, value) -> typing.Optional[str]:
        return None

    def on_enter(self) -> CommandResult:
        return self.send_message(text="YOU STARTED NEW REQUEST")
