from runtime.commands import CommandsBase
from pymongo import MongoClient
from database import DataBase

admins = {"molberte", "ntdesmond", "lexa_small", "alias25664"}
# messages = {"molberte": ["hello", "nehello"], "ntdesmond": ["спасибо", "зa", "открывашку"]}


class AdminCommands(CommandsBase):
    def is_admin(self) -> bool:
        return self.session.user.username in admins

    def get_user_messages_command(self, message_text: str):
        if self.is_admin():
            if message_text == "/get_user_messages":
                self.hold_next(2)
                return self.send_message("Send the alias of user you want to get messages from", reply_markup=None)
            else:
                user_alias = self.message.text
                messages = DataBase().read_db()
                if user_alias in messages.keys():
                    return self.send_message("\n".join(messages[user_alias][-20:]), reply_markup=None)
                else:
                    return self.send_message("There is no history with that user", reply_markup=None)
        else:
            return self.send_message("Can not access. Not enough rights", reply_markup=None)

    def check_new_requests_command(self, message_text: str):
        if self.is_admin():
            if message_text == "/check_new_requests":
               # self.hold_next(2)

                return DataBase.get_new_requests_command()

   # def respond_command(self, id_of_request: str):
