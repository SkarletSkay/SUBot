from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Type


class CallbackKeyboard:
    @staticmethod
    def from_dict(buttons: dict, row_width: int = 3):
        """
        Create an InlineKeyboardMarkup with given buttons passed as a dict, having a maximum of row_count button per row

        :param buttons: Dictionary with keys as button texts and values os their callback data
        :param row_width: int, maximum buttons per row, defaults to 3
        """
        button_objects = [InlineKeyboardButton(text=key, callback_data=buttons[key]) for key in buttons]
        keyboard_rows = []
        for i in range(0, len(button_objects), row_width):
            keyboard_rows.append(button_objects[i:i+row_width])
        return InlineKeyboardMarkup(keyboard_rows)

    @staticmethod
    def from_tuple(buttons: tuple, row_width: int = 1):
        """
        Create an InlineKeyboardMarkup with given buttons passed as a tuple, having a maximum of row_count button per row

        :param buttons: Tuple with values that are used as button text and callback data
        :param row_width: int, maximum buttons per row, defaults to 1
        """
        button_objects = [InlineKeyboardButton(text=key, callback_data=key) for key in buttons]
        keyboard_rows = []
        for i in range(0, len(button_objects), row_width):
            keyboard_rows.append(button_objects[i:i+row_width])
        return InlineKeyboardMarkup(keyboard_rows)


class Keyboard:
    """
    A class with all the InlineKeyboardMarkup objects used by bot.
    Defined in init, objects can be accessed using the class properties
    """
    def __init__(self):
        self.__commands = CallbackKeyboard.from_dict({
            "Create a request": "/new_request",
            "See my request": "/pending_request"
        })
        self.__admin_commands = CallbackKeyboard.from_dict({
            "Create a request": "/new_request",
            "See user requests": "/get_user_messages"
        })
        self.__request_categories = CallbackKeyboard.from_dict(dict(
            [(category, f"/category {category}") for category in (
                'Project', 'Learning', 'Another category'
            )] + [("Cancel", "/cancel")])
        )
        self.__user_request_actions = CallbackKeyboard.from_dict({
            "Show/Hide request text": "/show_request_text",
            "Refresh": "/refresh_request_status"
        })
        self.__cancel_only = CallbackKeyboard.from_dict({"Cancel": "/cancel"})
        self.__empty = InlineKeyboardMarkup([[]])

    @property
    def commands(self) -> InlineKeyboardMarkup:
        return self.__commands

    @property
    def admin_commands(self) -> InlineKeyboardMarkup:
        return self.__admin_commands

    @property
    def request_categories(self) -> InlineKeyboardMarkup:
        return self.__request_categories

    @property
    def user_request_actions(self) -> InlineKeyboardMarkup:
        return self.__user_request_actions

    @property
    def cancel_only(self) -> InlineKeyboardMarkup:
        return self.__cancel_only

    @property
    def empty(self) -> InlineKeyboardMarkup:
        return self.__empty

    @property
    def factory(self) -> Type[CallbackKeyboard]:
        return CallbackKeyboard
