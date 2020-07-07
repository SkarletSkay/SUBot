from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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
            keyboard_rows.append(button_objects[i:i + row_width])
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
            keyboard_rows.append(button_objects[i:i + row_width])
        return InlineKeyboardMarkup(keyboard_rows)


class Keyboard:
    """
    A class with all the InlineKeyboardMarkup objects used by bot.
    Defined in init, objects can be accessed using the class properties
    """

    def __init__(self):
        self.__commands = CallbackKeyboard.from_dict({
            "Create a request": "/new_request"
        })
        self.__admin_commands = CallbackKeyboard.from_dict({
            "Create a request": "/new_request",
            "See user requests": "/get_user_messages"
        })
        self.__request_categories = CallbackKeyboard.from_dict(dict(
            [(category, f"/category {category}") for category in (
                'Project', 'Learning', 'Another category'
            )] + [("Cancel", "Cancel")])
        )
        self.__cancel_only = CallbackKeyboard.from_tuple(("Cancel",))
        self.__empty = InlineKeyboardMarkup([[]])
        self.__new_request_actions = self.new_request_actions(1)

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
    def cancel_only(self) -> InlineKeyboardMarkup:
        return self.__cancel_only

    @property
    def empty(self) -> InlineKeyboardMarkup:
        return self.__empty

    @staticmethod
    def new_request_actions(request_id) -> InlineKeyboardMarkup:
        return CallbackKeyboard.from_dict(dict(
            [(action, f"/new_request_action {request_id}:{action}") for action in (
                'Take', 'Respond', 'Close',
            )] + [("Cancel", "Cancel")])
        )

    @staticmethod
    def get_user_messages_paginated(alias, offset, l_available=True, r_available=True) -> InlineKeyboardMarkup:
        arrows = []
        arrows.append("<") if l_available else None
        arrows.append(">") if r_available else None
        return CallbackKeyboard.from_dict(dict(
            [(action, f"/get_user_messages {alias}:{action}:{offset}") for action in arrows] + [("Cancel", "Cancel")])
        )
