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
            keyboard_rows.append(button_objects[i:i+row_width])
        return InlineKeyboardMarkup(keyboard_rows)

    @staticmethod
    def from_tuple(buttons: tuple, row_width: int = 1):
        """
        Create an InlineKeyboardMarkup with given buttons passed as a dict, having a maximum of row_count button per row

        :param buttons: Dictionary with keys as button texts and values os their callback data
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
            "Create a request": "/new_request"
        })
        self.__admin_commands = CallbackKeyboard.from_dict({
            "Create a request": "/new_request",
            "See user requests": "/get_user_messages"
        })
        self.__request_categories = CallbackKeyboard.from_dict(dict(
            [(category, f"/category {category}") for category in (
                'Project', 'Learning', 'Another category'
            )])
        )

    @property
    def commands(self) -> InlineKeyboardMarkup:
        return self.__commands

    @property
    def admin_commands(self) -> InlineKeyboardMarkup:
        return self.__admin_commands

    @property
    def request_categories(self) -> InlineKeyboardMarkup:
        return self.__request_categories


# properties may be used only in an instance of the class
Keyboard = Keyboard()
