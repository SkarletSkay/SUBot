from runtime.commandHandlers import CommandHandlerBase
from runtime.context import CallbackContext, MessageContext
from modules.Keyboard import Keyboard

category_prefix = "/category "


def save_request(user: str, category: str, text: str) -> bool:
    # TODO: use db instead of saving to file
    with open("requests.txt", "a") as file:
        file.write(f"{user}\t{category}\t{text}\n")
    return True


def new_request(command: CommandHandlerBase) -> bool:
    # Kludge on a kludge covered with some more kludges... Hope it will be better soon.
    if isinstance(command.context, MessageContext) and command.context.text == "/new_request" or \
       isinstance(command.context, CallbackContext) and command.context.prev_updates[-1].callback_query.data == "/new_request":
        if isinstance(command.context, CallbackContext):
            command.context.bot.answer_callback_query(command.context.callback_id)
        command.hold_next(2)
        command.context.bot.send_message(chat_id=command.context.chat.id,
                                         text="Select a category of your request",
                                         reply_markup=Keyboard.request_categories)
    elif isinstance(command.context, CallbackContext):
        if command.context.data.startswith(category_prefix):
            command.hold_next(2)
            old_message = command.context.message.message_id
            # Hack: using prev_updates to get the callback_query
            category = command.context.prev_updates[-1].callback_query.data[len(category_prefix):]
            command.context.bot.edit_message_text(chat_id=command.context.chat.id,
                                                  message_id=old_message,
                                                  text=f"Selected category: {category}")
            command.context.bot.send_message(chat_id=command.context.chat.id,
                                             text="Alright, now write your request, providing all the information that you consider to be useful here.",
                                             reply_markup=Keyboard.cancel_only)
        else:
            # Cancel button handling
            old_message = command.context.message.message_id
            command.context.bot.edit_message_text(chat_id=command.context.chat.id,
                                                  message_id=old_message,
                                                  text="You cancelled the creation of the new request.")
    else:
        callback_text = ""
        if len(command.context.prev_updates) >= 2 and command.context.prev_updates[-2].callback_query is not None:
            callback_text = command.context.prev_updates[-2].callback_query.data
        if callback_text == "" or not callback_text.startswith(category_prefix):
            command.hold_next(2)
            command.context.send_message("Please, use the buttons above to select a category.")
            return True
        # remove the "/category " prefix
        category = callback_text[len(category_prefix):]
        text = command.context.text
        user = command.context.user.username or f"id{command.context.user.id}"
        if save_request(user, category, text):
            command.context.send_message(f"We've saved your request.\nCategory: {category}\nStatus: New")
        else:
            command.context.send_message(f"There was an error saving your request :(")
    return True
