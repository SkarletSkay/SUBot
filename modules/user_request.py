from runtime.commands import CommandsBase, CommandResult
from modules.keyboard import Keyboard


class UserRequest:
    def __init__(self, keyboard: Keyboard):
        self.__keyboard = keyboard
        self.__category_prefix = "/category "

    def save_request(self, user: str, category: str, text: str) -> bool:
        # TODO: use db instead of saving to file
        with open("requests.txt", "a") as file:
            file.write(f"{user}\t{category}\t{text}\n")
        return True

    def new_request(self, command: CommandsBase, message_text: str) -> CommandResult:
        if message_text == "/new_request":
            if command.callback_query is not None:
                # TODO: add answer_callback_query or edit markup to None to fix the hanging "clock" on buttons
                pass
            command.hold_next(2)
            return command.send_message("Select a category of your request", self.__keyboard.request_categories)
        elif command.callback_query is not None and message_text == "Cancel":
            return command.edit_message_text(command.callback_query.message.message_id, "You cancelled the creation of the new request.")
        elif command.holding_left == 1:
            if command.callback_query is None:
                command.hold_next(2)
                return command.send_message("Please, use the buttons above to select a category.", None)
            elif message_text.startswith(self.__category_prefix):
                category = message_text[len(self.__category_prefix):]
                command.session["new_request_category"] = category
                # FIXME: line below doesn't work, find an alternative
                command.edit_message_text(command.callback_query.message.message_id, f"Selected category: {category}\n")
                return command.send_message("Alright, now write your request, providing all the information that you consider to be useful here.", self.__keyboard.cancel_only)
        else:
            category = command.session["new_request_category"]
            user = command.session.user.username or f"id{command.session.user.id}"
            if self.save_request(user, category, message_text):
                return command.send_message(f"We've saved your request.\nCategory: {category}\nStatus: New", None)
            else:
                return command.send_message(f"There was an error saving your request :(", None)
