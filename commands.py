from runtime.commands import CommandsBase
from database import DataBase

class GreetingsCommands(CommandsBase):

    def start_command(self, command: str):
        return self.compound_result((
            self.send_message("Я", None),
            self.send_message("Пидорас", None),
        ))

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

    def list_requests_command(self, command: str):
        if command == "/list_requests":
            db = DataBase()
            print("ok")
            all_requests = db.read_db()

            pretty = 'List of all requests:\n\n'
            for i in range(len(all_requests)):
                pretty += str(all_requests[i]) + "\n\n"
            return self.send_message(pretty, None)

