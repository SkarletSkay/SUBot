from runtime.commands import CommandsBase
from modules.keyboard import Keyboard
from modules.database import DataBase


class UserRequestCommands(CommandsBase):
    def __init__(self, keyboard: Keyboard, database: DataBase):
        super().__init__()
        self.__keyboard = keyboard
        self.__db = database
        self.__category_prefix = "/category "

    def new_request_command(self, message_text: str):
        if message_text == "/new_request":
            if self.callback_query is None:
                return self.send_message("Select a category of your request", self.__keyboard.request_categories)
            else:
                return self.edit_message(self.callback_query.message.message_id,
                                         "Select a category of your request",
                                         self.__keyboard.request_categories)

    def category_command(self, message_text: str):
        if self.callback_query is None:
            if self.session["new_request_message_id"] is not None:
                if message_text.startswith("/"):
                    # redirect to other actions
                    if not self.session["new_request_interrupted"]:
                        # interrupt: must be called only once \/
                        self.bot.edit_message_text("You have interrupted request creation.",
                                                   chat_id=self.session.user.id,
                                                   message_id=self.session["new_request_message_id"],
                                                   reply_markup=self.__keyboard.continue_request_creation(
                                                       self.session["request_category"]
                                                   ))
                        self.session["new_request_interrupted"] = True
                    return self.redirect_to_command(f"{message_text.split()[0][1:]}_command")
                else:
                    # write a request body
                    return self.redirect_to_command("confirm_request_command")
        else:
            if message_text.startswith(self.__category_prefix):
                if self.session["new_request_message_id"] is None or self.callback_query.message.message_id == self.session["new_request_message_id"]:
                    self.hold_next()  # Take the request text in the next message
                    # save the category
                    self.session["new_request_interrupted"] = False
                    return self.select_category(message_text)
                else:
                    self.hold_next()  # Take the request text in the next message
                    return self.edit_message(self.callback_query.message.message_id,
                                             "You cannot create two requests in parallel. "
                                             "Complete the one you have started to edit, "
                                             "or cancel it and create a new request.", None)
            else:
                return self.redirect_to_command(f"{message_text.split()[0][1:]}_command")
        return self.no_message()

    def select_category(self, message_text: str):
        # helper function
        category = message_text[len(self.__category_prefix):]
        self.session["request_category"] = category
        self.session["new_request_message_id"] = self.callback_query.message.message_id
        return self.edit_message(self.callback_query.message.message_id,
                                 f"Selected category: {category}\n"
                                 "Alright, now write your request, providing all the information that you consider to be useful here.",
                                 self.__keyboard.change_category)

    def confirm_request_command(self, message_text: str):
        if self.callback_query is None:
            self.session['request_text'] = message_text
            return self.compound_result((
                self.edit_message(self.session["new_request_message_id"], None, self.__keyboard.empty),
                self.send_message("Please, check the request once again and use the button below to confirm sending.\n\n"
                                  f"Category: {self.session['request_category']}\nText:\n{self.session['request_text']}\n\n"
                                  "Notifications on updates: " + ("ON" if self.session["request_notifications"] else "OFF"),
                                  self.__keyboard.user_request_confirmation)
            ))
        else:
            return self.edit_message(self.callback_query.message.message_id,
                                     "Please, check the request once again and use the button below to confirm sending.\n\n"
                                     f"Category: {self.session['request_category']}\nText:\n{self.session['request_text']}\n\n"
                                     "Notifications on updates: " + ("ON" if self.session["request_notifications"] else "OFF"),
                                     self.__keyboard.user_request_confirmation)

    def send_request_command(self, message_text: str):
        if self.callback_query is not None:
            save_success = self.__db.insert_new_request(user_id=self.session.user.id,
                                                        alias=self.session.user.username,
                                                        category=self.session["request_category"],
                                                        text=self.session["request_text"],
                                                        notify=self.session["request_notifications"] or False)
            self.session["new_request_message_id"] = None
            self.session["request_category"] = None
            self.session["request_text"] = None
            return self.compound_result((
                self.edit_message(self.callback_query.message.message_id, None, self.__keyboard.empty),
                self.send_message("We've saved your request.\nStatus: New" if save_success else "There was an error saving your request :(", None)
            ))
        else:
            return self.no_message()

    def cancel_request_command(self, message_text: str):
        if self.callback_query is None:
            return self.no_message()
        else:
            self.session["new_request_message_id"] = None
            self.session["request_category"] = None
            self.session["request_text"] = None
            return self.edit_message(self.callback_query.message.message_id,
                                     "You have cancelled the request creation.", None)

    def request_notifications_command(self, message_text: str):
        if self.callback_query is None:
            return self.no_message()
        else:
            self.session["request_notifications"] = not self.session["request_notifications"]
            return self.redirect_to_command("confirm_request_command")

    def pending_request_command(self, message_text: str):
        request: dict = self.__db.__get_requests(self.session.user.id)[0]
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
            return self.redirect_to_command(f"pending_request_command")

    def refresh_request_status_command(self, message_text: str):
        if self.callback_query is None:
            return self.no_message()
        else:
            return self.redirect_to_command("pending_request_command")
