from runtime.commandHandlers import CommandHandlerBase
from modules.Keyboard import Keyboard

admins = {"ntdesmond", "molberte", "id2"}


def is_admin(username: str) -> bool:
    return username in admins


def get_help(command: CommandHandlerBase) -> bool:
    if is_admin(command.context.user.username):
        markup = Keyboard.admin_commands
    else:
        markup = Keyboard.commands
    command.context.bot.send_message(chat_id=command.context.chat.id,
                                     text="Hello! This bot is designed to facilitate connection between you and the Student Union (SU). \
                                     This bot can help you to send various requests to the Student Union. It may be a new project, question, \
                                     complaint — or anything else you want to tell SU about.\n\nPlease use the buttons below for navigation.",
                                     reply_markup=markup)
    return True
