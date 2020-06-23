from runtime.commands import CommandsBase


class GreetingsCommands(CommandsBase):

    def start_command(self, command: str):
        return self.send_message_list(list(("Я", "Пидорас")))

    def hello_command(self, command: str):
        if command == "/hello":
            self.hold_next(3)
            return self.send_message(str(self.holding_left), None)
        else:
            return self.send_message("Greetings " + str(self.session.user.username) + " " + str(self.holding_left), None)

    def unknown_command(self, command: str):
        raise Exception(command)

    def error_handler(self, exception: Exception):
        return self.redirect_to_command("start_command")
