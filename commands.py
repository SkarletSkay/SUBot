from runtime.commands import CommandsBase
from runtime.dependency_injection import services
from modules.user_request import UserRequest
from modules.help import Help


class GreetingsCommands(CommandsBase):

    def start_command(self, command: str):
        module: Help = services.get_instance(Help, self.session.identifier)
        return module.get_help(self)

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


class UserCommands(CommandsBase):
    def new_request_command(self, command: str):
        module: UserRequest = services.get_instance(UserRequest, self.session.identifier)
        return module.new_request(self, command)
