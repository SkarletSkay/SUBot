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
    @property
    def commands(self) -> InlineKeyboardMarkup:
        return CallbackKeyboard.from_dict({
            "Create a request": "/new_request"
        })

    @property
    def admin_commands(self) -> InlineKeyboardMarkup:
        return CallbackKeyboard.from_dict({
            "Create a request": "/new_request",
            "See user requests": "/get_user_messages"
        })

    @property
    def request_categories(self) -> InlineKeyboardMarkup:
        return CallbackKeyboard.from_dict(dict(
            [(category, f"/category {category}") for category in (
                'Project', 'Learning', 'Another category'
            )])
        )


keyboard = Keyboard()
print(keyboard.admin_commands.to_json(), keyboard.admin_commands.to_json(), keyboard.request_categories.to_json())