from runtime.commands import CommandsBase, CommandResult
from modules.keyboard import Keyboard


class Help:
    def __init__(self, keyboard: Keyboard):
        self.__keyboard = keyboard
        # TODO: integrate with database
        self.__admins = {"ntdesmond", "molberte", "id2"}

    def is_admin(self, username: str) -> bool:
        return username in self.__admins

    def get_help(self, command: CommandsBase) -> CommandResult:
        if self.is_admin(command.session.user.username):
            markup = self.__keyboard.admin_commands
        else:
            markup = self.__keyboard.commands
        return command.send_message("Hello! This bot is designed to facilitate connection between you and the Student Union (SU). "
                                    "This bot can help you to send various requests to the Student Union. It may be a new project, question, "
                                    "complaint — or anything else you want to tell SU about.\n\nPlease use the buttons below for navigation.",
                                    reply_markup=markup)
