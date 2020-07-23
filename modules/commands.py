import typing
import telegram

from resources.designer import Resources
from runtime.commands import ModelCommandBase, CommandResult, CommandsBase
from runtime.resources import IResourceProvider


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


class MyCommands(CommandsBase):

    def __init__(self, res: IResourceProvider):
        super().__init__()
        self.res = res

    def start_command(self, args):
        string = self.res.get_string(Resources.Strings.CONFIRM_SENDING)
        return self.send_message(text="<i>Говно</i>", parse_mode=telegram.ParseMode.HTML)
