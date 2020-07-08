from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class CallbackKeyboard:
    @staticmethod
    def from_dict(buttons: dict, row_width: int = 1):
        """
        Create an InlineKeyboardMarkup with given buttons passed as a dict, having a maximum of row_count button per row

        :param buttons: Dictionary with keys as button texts and values os their callback data
        :param row_width: int, maximum buttons per row, defaults to 1
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
    Defined in init, static keyboards can be accessed using the class properties
    Dynamically generated (depending on parameters) keyboards are the static methods (ironically enough)
    """

    def __init__(self):
        self.__commands = CallbackKeyboard.from_dict({
            "Create a request": "/new_request"
        })
        self.__admin_commands = CallbackKeyboard.from_dict({
            "Create a request": "/new_request",
            "See requests from a specific user": "/get_user_messages",
            "See new requests": "/check_new_requests"
        })
        self.__request_categories = CallbackKeyboard.from_dict(dict(
            [(category, f"/category {category}") for category in (
                'Professors & TAs', 'DoE or Administration', 'Student Affairs', 'Events', 'Student Projects', 'Clubs',
                'Education process', 'Representatives', 'Student Union'
            )] + [("Cancel", "/cancel_request")]), 2
        )
        self.__user_request_actions = CallbackKeyboard.from_dict({
            "Show/Hide request text": "/show_request_text",
            "Refresh": "/refresh_request_status"
        })
        self.__user_request_confirmation = CallbackKeyboard.from_dict({
            "Send!": "/send_request",
            "Cancel": "/cancel_request",
            "Enable/Disable notifications": "/request_notifications"
        }, 2)
        self.__change_category = CallbackKeyboard.from_dict({"Change category": "/new_request"})
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
    def user_request_confirmation(self) -> InlineKeyboardMarkup:
        return self.__user_request_confirmation

    @property
    def change_category(self) -> InlineKeyboardMarkup:
        return self.__change_category

    @property
    def empty(self) -> InlineKeyboardMarkup:
        return self.__empty

    @staticmethod
    def continue_request_creation(category: str):
        return CallbackKeyboard.from_dict({"Continue": f"/category {category}"})

    @staticmethod
    def new_request_actions(request_id: str) -> InlineKeyboardMarkup:
        return CallbackKeyboard.from_dict(dict(
            [(action, f"/new_request_action {request_id}:{action}") for action in (
                'Take', 'Respond', 'Close',
            )] + [("Cancel", "Cancel")])
        )

    @staticmethod
    def get_user_messages_paginated(alias: str, offset: int, l_available=True, r_available=True) -> InlineKeyboardMarkup:
        arrows = []
        if l_available:
            arrows.append("<")
        if r_available:
            arrows.append(">")
        return CallbackKeyboard.from_dict(dict(
            [(action, f"/get_user_messages {alias}:{action}:{offset}") for action in arrows] + [("Cancel", "Cancel")])
        )
