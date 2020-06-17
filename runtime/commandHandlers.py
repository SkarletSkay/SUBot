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


class StartCommand(CommandHandlerBase):

    def satisfy(self, update: Update) -> bool:
        if update.message is not None and update.message.text == "/start":
            return True
        else:
            return False

    def execute_async(self) -> bool:
        self.context.send_message("hello")
        self.hold_next(4)

        return True


class NewRequestCommand(CommandHandlerBase):

    def satisfy(self, update: Update) -> bool:
        return update.message is not None and update.message.text == "/new_request"

    def execute_async(self) -> bool:
        from modules import UserRequest
        return UserRequest.new_request(self)


class MyCommand(CommandHandlerBase):

    def satisfy(self, update: Update) -> bool:
        return True

    def execute_async(self) -> bool:
        return True
