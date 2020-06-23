from runtime.context import Context, MessageContext
from telegram import Update


class CommandHandlerBase:

    def __init__(self, context: Context):
        self.holding = 0
        self.__context = context

    @property
    def context(self) -> Context:
        return self.__context

    def hold_next(self, duration: int = 1):
        self.holding = duration

    def execute_async(self) -> bool:
        return True

    def satisfy(self, update: Update) -> bool:
        return False


class HelpCommand(CommandHandlerBase):

    def satisfy(self, update: Update) -> bool:
        return update.message is not None and update.message.text in ("/help", "/start")

    def execute_async(self) -> bool:
        from modules import Help
        return Help.get_help(self)


class NewRequestCommand(CommandHandlerBase):

    def satisfy(self, update: Update) -> bool:
        return update.message is not None and update.message.text == "/new_request" or \
               update.callback_query is not None and update.callback_query.data == "/new_request"

    def execute_async(self) -> bool:
        from modules import UserRequest
        return UserRequest.new_request(self)


class MyCommand(CommandHandlerBase):

    def satisfy(self, update: Update) -> bool:
        return True

    def execute_async(self) -> bool:
        return True
