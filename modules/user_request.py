from runtime.commands import CommandsBase
from modules.keyboard import Keyboard
from modules.database import Database


class UserRequestCommands(CommandsBase):
    def __init__(self, keyboard: Keyboard, database: Database):
        super().__init__()
        self.__keyboard = keyboard
        self.__db = database
        self.__category_prefix = "/category "

    def category_command(self, message_text: str):
        if self.session["request_category"] is None:
            if self.callback_query is None:
                return self.no_message()
            else:
                # save the category
                category = message_text[len(self.__category_prefix):]
                self.session["request_category"] = category
                self.session["new_request_message_id"] = self.callback_query.message.message_id
                self.hold_next()  # Take the request text in the next message
                return self.edit_message(self.callback_query.message.message_id,
                                         f"Selected category: {category}\n"
                                         "Alright, now write your request, providing all the information that you consider to be useful here.",
                                         self.__keyboard.cancel_only)
        else:
            # write a request body
            if self.callback_query is None and not message_text.startswith("/"):
                category: str = self.session["request_category"]
                self.session["request_category"] = None
                if self.__db.save_new_request(self.session.user.id, self.message.date, category, message_text):
                    return self.compound_result((
                        self.edit_message(self.session["new_request_message_id"], None, self.__keyboard.empty),
                        self.send_message(f"We've saved your request.\nCategory: {category}\nStatus: New", None)
                    ))
                else:
                    return self.compound_result((
                        self.edit_message(self.session["new_request_message_id"], None, self.__keyboard.empty),
                        self.send_message(f"There was an error saving your request :(", None)
                    ))
            else:
                # redirect if user used another button
                # TODO: confirmation before sending
                if message_text.startswith(self.__category_prefix):
                    self.hold_next()
                    return self.edit_message(self.callback_query.message.message_id,
                                             "You cannot create two requests in parallel. "
                                             "Write the request body for the one awaiting your response, "
                                             "or hit Cancel and create a new request.", None)
                else:
                    self.bot.edit_message_text("You have interrupted request creation.",
                                               chat_id=self.session.chat.id,
                                               message_id=self.session["new_request_message_id"],
                                               reply_markup=self.__keyboard.factory.from_dict(
                                                   {"Continue": f"/category {self.session['request_category']}"}
                                               ))
                    self.session["request_category"] = None
                    return self.redirect_to_command(f"{message_text.split()[0][1:]}_command")

    def new_request_command(self, message_text: str):
        if message_text == "/new_request":
            if self.callback_query is None:
                return self.send_message("Select a category of your request", self.__keyboard.request_categories)
            else:
                return self.edit_message(self.callback_query.message.message_id,
                                         "Select a category of your request",
                                         self.__keyboard.request_categories)

    def pending_request_command(self, message_text: str):
        request: dict = self.__db.get_request(self.session.user.id)
        if request is None:
            response_text: str = "You have no request being reviewed by Student Union."
        else:
            response_text: str = f"Here is your request:\nCategory: {request['category']}\nStatus: {request['status']}"
            if self.session["show_request_text"]:
                response_text += f"\n\nText:\n{request['text']}"
        if self.callback_query is None:
            return self.send_message(response_text, self.__keyboard.user_request_actions)
        else:
            return self.edit_message(self.callback_query.message.message_id, response_text, self.__keyboard.user_request_actions)

    def show_request_text_command(self, message_text: str):
        if self.callback_query is None:
            return self.no_message()
        else:
            self.session["show_request_text"] = not self.session["show_request_text"]
            return self.redirect_to_command("pending_request_command")

    def refresh_request_status_command(self, message_text: str):
        if self.callback_query is None:
            return self.no_message()
        else:
            return self.redirect_to_command("pending_request_command")
