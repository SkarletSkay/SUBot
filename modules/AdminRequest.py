from runtime.commandHandlers import CommandHandlerBase
from runtime.context import MessageContext

messages = {"molberte": ["hello", "nehello"], "alias2": ["verni nalogi"]}
admins = {"molberte", "id2"}


def is_admin(command: CommandHandlerBase) -> bool:
    if command.context.user.username in admins:
        return True
    else:
        command.context.send_message("Can not access. You do not have enough rights.")
        return False


def get_all_messages(command: CommandHandlerBase) -> bool:
    if is_admin(command):
        if isinstance(command.context, MessageContext) and command.context.text == "/get_user_messages":
            command.hold_next(2)
            command.context.send_message("Send alias of the user you want to get message from")
            return True
        else:
            user_alias = command.context.text
            if user_alias in messages.keys():
                command.context.send_message("\n".join(messages[user_alias][-20:]))
            else:
                command.context.send_message("There is no user with the given alias")
            return True
    else:
        return True