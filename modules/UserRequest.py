from runtime.commandHandlers import CommandHandlerBase
from runtime.context import CallbackContext, MessageContext
from CallbackKeyboard import CallbackKeyboard

categories = (
    'Project', 'Learning', 'Another category'
)


def save_request(user: str, category: str, text: str) -> bool:
    # TODO: use db instead of saving to file
    with open("requests.txt", "w") as file:
        file.write(f"{user}\t{category}\t{text}")
    return True


def new_request(command: CommandHandlerBase) -> bool:
    if isinstance(command.context, MessageContext) and command.context.text == "/new_request":
        command.hold_next(3)
        command.context.bot.send_message(chat_id=command.context.chat.id,
                                         text="Select a category of your request",
                                         reply_markup=CallbackKeyboard.from_dict(dict([(category, f"/category {category}") for category in categories])))
        return True
    elif isinstance(command.context, CallbackContext) and command.context.data.split()[0] == "/category":
        old_message = command.context.message.message_id
        command.context.bot.edit_message_text(chat_id=command.context.chat.id,
                                              message_id=old_message,
                                              text="Alright, now write your request, providing all the information that you consider to be useful here.")
        return True
    else:
        # FIXME: will break if there is less than 2 updates
        callback_category = command.context.prev_updates[-2].callback_query.data
        # remove the "/category " prefix
        category = callback_category[callback_category.index(" ") + 1:]
        text = command.context.text
        user = command.context.user.username or f"id{command.context.user.id}"
        if save_request(user, category, text):
            command.context.send_message(f"We've saved your request.\nCategory: {category}\nStatus: New")
            return True
        else:
            command.context.send_message(f"There was an error saving your request :(")
            return False
