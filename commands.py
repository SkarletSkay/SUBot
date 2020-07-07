from runtime.commands import CommandsBase


class GreetingsCommands(CommandsBase):

    def start_command(self, *args):
        return self.compound_result((
            self.send_message("Я", None),
            self.send_message("Пидорас", None),
        ))

    def hello_command(self, *args):
        if len(args) > 0:
            return self.send_message_list(list(args))

        if self.bot_request.message_text == "/hello":
            self.hold_next(3)
            return self.send_message(str(self.holding_left), None)
        else:
            return self.send_message("Greetings " + str(self.user.username) + " " + str(self.holding_left), None)

    def unknown_command(self, *args):
        raise Exception("Жопа")

    def error_handler(self, exception: Exception):
        return self.redirect_to_command("start_command")
