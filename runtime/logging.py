from runtime.context import Context
from runtime.middleware import Middleware


class ConsoleLogger(Middleware):

    def __init__(self):
        super().__init__()
        self.num = 0

    def invoke(self, context: Context):
        print(str(self.num) + " " + context.update.message.text)
        self.num += 1

        self.invoke_next(context)
