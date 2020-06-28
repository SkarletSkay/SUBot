from runtime.commands import CommandsBase

admins = {"molberte", "ntdesmond", "lexa_small", "alias25664"}
messages = {"molberte": ["hello", "nehello"], "ntdesmond": ["спасибо", "зa", "открывашку"]}


class AdminCommands(CommandsBase):
    def is_admin(self) -> bool:
        if self.session.user.username in admins:
            return True
        else:
            return False

    def get_user_messages_command(self, message_text: str):
        if self.is_admin():
            if message_text == "/get_user_messages":
                self.hold_next(2)
                return self.send_message("Send the alias of user you want to get messages from", reply_markup=None)
            else:
                user_alias = self.message.text
                if user_alias in messages.keys():
                    return self.send_message("\n".join(messages[user_alias][-20:]), reply_markup=None)
                else:
                    return self.send_message("There is no history with that user", reply_markup=None)
        else:
            return self.send_message("Can not access. Not enough rights", reply_markup=None)
