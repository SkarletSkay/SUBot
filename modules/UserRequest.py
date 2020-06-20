from runtime.commandHandlers import CommandHandlerBase
from runtime.context import CallbackContext, MessageContext
from modules.CallbackKeyboard import CallbackKeyboard

categories = (
    'Project', 'Learning', 'Another category'
)
callback_prefix = "/category "


def save_request(user: str, category: str, text: str) -> bool:
    # TODO: use db instead of saving to file
    with open("requests.txt", "a") as file:
        file.write(f"{user}\t{category}\t{text}\n")
    return True


def new_request(command: CommandHandlerBase) -> bool:
    if isinstance(command.context, MessageContext) and command.context.text == "/new_request":
        command.hold_next(3)
        command.context.bot.send_message(chat_id=command.context.chat.id,
                                         text="Select a category of your request",
                                         reply_markup=CallbackKeyboard.from_dict(dict([(category, f"{callback_prefix}{category}") for category in categories])))
        return True
    elif isinstance(command.context, CallbackContext) and command.context.data.startswith(callback_prefix):
        old_message = command.context.message.message_id
        # Hack: using prev_updates to get the callback_query
        category = command.context.prev_updates[-1].callback_query.data[len(callback_prefix):]
        command.context.bot.edit_message_text(chat_id=command.context.chat.id,
                                              message_id=old_message,
                                              text=f"Selected category: {category}")
        command.context.bot.send_message(chat_id=command.context.chat.id,
                                         text="Alright, now write your request, providing all the information that you consider to be useful here.")
        return True
    else:
        callback_text = ""
        if len(command.context.prev_updates) >= 2 and command.context.prev_updates[-2].callback_query is not None:
            callback_text = command.context.prev_updates[-2].callback_query.data
        if callback_text == "" or not callback_text.startswith(callback_prefix):
            # FIXME: need to hold one more update here. Can not do so with the current pipeline. Busy waiting.
            command.context.send_message("Please, use the buttons above to select a category.")
            return True
        # remove the "/category " prefix
        category = callback_text[len(callback_prefix):]
        text = command.context.text
        user = command.context.user.username or f"id{command.context.user.id}"
        if save_request(user, category, text):
            command.context.send_message(f"We've saved your request.\nCategory: {category}\nStatus: New")
        else:
            command.context.send_message(f"There was an error saving your request :(")
        return True
