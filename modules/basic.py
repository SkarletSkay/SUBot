from resources.designer import Resources
from runtime.commands import CommandsBase
from modules.keyboard import Keyboard


class BasicCommands(CommandsBase):
    def __init__(self, keyboard: Keyboard):
        super().__init__()
        self.__keyboard = keyboard
        # TODO: integrate with database or auth system
        self.__admins = {"ntdesmond", "molberte", "id2"}

    def start_command(self):
        return self.redirect_to_command("help_command")

    def help_command(self):
        if self.user.username in self.__admins:
            markup = self.__keyboard.admin_commands
        else:
            markup = self.__keyboard.commands
        # TODO: use Resources
        return self.send_message(
            "This bot is designed to facilitate connection between you and the Student Union (SU). "
            "This bot can help you to send various requests to the Student Union. It may be a new project, question, "
            "complaint — or anything else you want to tell SU about.\n\nPlease use the buttons below for navigation.",
            reply_markup=markup)

    def unknown_command(self):
        raise Exception(self.bot_request.command)

    def error_handler(self, exception: Exception):
        return self.send_message("Unknown command. Type \"/help\" for help.", None)
