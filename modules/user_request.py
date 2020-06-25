from runtime.commands import CommandsBase
from modules.keyboard import Keyboard


class UserRequestCommands(CommandsBase):
    def __init__(self, keyboard: Keyboard):
        super().__init__()
        self.__keyboard = keyboard
        self.__category_prefix = "/category "

    def save_request(self, user: str, category: str, text: str) -> bool:
        # TODO: use db instead of saving to file
        with open("requests.txt", "a") as file:
            file.write(f"{user}\t{category}\t{text}\n")
        return True

    def new_request_command(self, message_text: str):
        if message_text == "/new_request":
            self.hold_next(2)
            if self.callback_query is None:
                return self.send_message("Select a category of your request", self.__keyboard.request_categories)
            else:
                return self.edit_message(self.callback_query.message.message_id,
                                         "Select a category of your request",
                                         self.__keyboard.request_categories)
        elif self.callback_query is not None and message_text == "Cancel":
            self.hold_next(0)  # don't hold anymore
            return self.edit_message(self.callback_query.message.message_id,
                                     "You cancelled the creation of the new request.", None)
        elif self.holding_left == 1:
            if self.callback_query is None:
                self.hold_next(2)
                return self.send_message("Please, use the buttons above to select a category.", None)
            elif message_text.startswith(self.__category_prefix):
                category = message_text[len(self.__category_prefix):]
                self.session["new_request_category"] = category
                self.session["new_request_message_id"] = self.callback_query.message.message_id
                return self.edit_message(self.callback_query.message.message_id,
                                         f"Selected category: {category}\n"
                                         "Alright, now write your request, providing all the information that you consider to be useful here.",
                                         self.__keyboard.cancel_only)
        else:
            category = self.session["new_request_category"]
            user = self.session.user.username or f"id{self.session.user.id}"
            if self.save_request(user, category, message_text):
                return self.compound_result((
                    self.edit_message(self.session["new_request_message_id"], None, self.__keyboard.empty),
                    self.send_message(f"We've saved your request.\nCategory: {category}\nStatus: New", None)
                ))
            else:
                return self.send_message(f"There was an error saving your request :(", None)
