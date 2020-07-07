from typing import List, Tuple

from telegram import Message, CallbackQuery, Bot, ReplyMarkup

from runtime.session import Session


class CommandResult:

    def execute(self, bot: Bot):
        pass


class CommandsBase:

    def __init__(self):
        self.__session = None
        self.__message = None
        self.__callback = None
        self.__bot = None

    @property
    def holding_left(self) -> int:
        if self.session["__holding__"] is not None:
            return self.session["__holding__"]
        return 0

    @property
    def message(self) -> Message:
        return self.__message

    @message.setter
    def message(self, value: Message):
        self.__message = value

    @property
    def callback_query(self) -> CallbackQuery:
        return self.__callback

    @callback_query.setter
    def callback_query(self, value: CallbackQuery):
        self.__callback = value

    @property
    def session(self) -> Session:
        return self.__session

    @session.setter
    def session(self, value: Session):
        self.__session = value

    @property
    def bot(self) -> Bot:
        return self.__bot

    @bot.setter
    def bot(self, value: Bot):
        self.__bot = value

    def hold_next(self, duration: int = 1):
        self.session["__holding__"] = duration

    def send_message(self, text: str, reply_markup, chat_id=None, parse_mode=None) -> CommandResult:
        if chat_id:
            return MessageResult(text, chat_id, reply_markup, parse_mode)
        return MessageResult(text, self.session.chat.id, reply_markup, parse_mode)

    def no_message(self) -> CommandResult:
        return EmptyResult()

    def redirect_to_command(self, command: str) -> CommandResult:
        self.session["__holding__"] = 1
        self.session["__command__"] = command
        return RedirectToCommandResult()

    def send_message_list(self, messages_list: List[str]):
        result = MessageListResult(self.session.chat.id, messages_list)
        return result

    def edit_message(self, message_id: int, new_text: str, new_markup: ReplyMarkup, parse_mode=None):
        result = EditMessageResult(self.session.chat.id, message_id, new_text, new_markup, parse_mode)
        return result

    def reply_to_message(self, message_id: int, text: str, reply_markup):
        result = ReplyToMessageResult(message_id, self.session.chat.id, text, reply_markup)
        return result

    def compound_result(self, results: Tuple[CommandResult, ...]):
        return CompoundResult(list(results))


class CompoundResult(CommandResult):
    def __init__(self, results: List[CommandResult]):
        self.__results = results

    def execute(self, bot: Bot):
        for result in self.__results:
            result.execute(bot)


class MessageResult(CommandResult):

    def __init__(self, message: str, chat_id: int, reply_markup, parse_mode=None):
        self.__message = message
        self.__chat_id = chat_id
        self.__markup = reply_markup
        self.__parse_mode = parse_mode

    def execute(self, bot: Bot):
        bot.send_message(self.__chat_id, self.__message, reply_markup=self.__markup, parse_mode=self.__parse_mode)


class EmptyResult(CommandResult):

    def execute(self, bot: Bot):
        pass


class RedirectToCommandResult(CommandResult):

    def execute(self, bot: Bot):
        pass


class ReplyToMessageResult(CommandResult):
    def __init__(self, message_id: int, chat_id: int, text: str, reply_markup):
        self.__message_id = message_id
        self.__chat_id = chat_id
        self.__text = text
        self.__markup = reply_markup

    def execute(self, bot: Bot):
        bot.send_message(self.__chat_id, self.__text, reply_to_message_id=self.__message_id, reply_markup=self.__markup)


class MessageListResult(CommandResult):
    def __init__(self, chat_id: int, messages: List[str]):
        self.__chat_id = chat_id
        self.__messages = messages

    def execute(self, bot: Bot):
        for message in self.__messages:
            bot.send_message(self.__chat_id, message)


class EditMessageResult(CommandResult):
    def __init__(self, chat_id: int, message_id: int, new_text: str, new_markup: ReplyMarkup, parse_mode=None):
        self.__chat_id = chat_id
        self.__message_id = message_id
        self.__new_text = new_text
        self.__new_markup = new_markup
        self.__parse_mode = parse_mode

    def execute(self, bot: Bot):
        if self.__new_text is not None:
            bot.edit_message_text(self.__new_text, chat_id=self.__chat_id, message_id=self.__message_id,
                                  parse_mode=self.__parse_mode)
        if self.__new_markup is not None:
            bot.edit_message_reply_markup(self.__chat_id, self.__message_id, reply_markup=self.__new_markup)


class EditMessageMarkupResult(CommandResult):
    def __init__(self, chat_id: int, message_id: int, new_markup):
        self.__chat_id = chat_id
        self.__new_markup = new_markup
        self.__message_id = message_id

    def execute(self, bot: Bot):
        bot.edit_message_reply_markup(chat_id=self.__chat_id, message_id=self.__message_id,
                                      reply_markup=self.__new_markup)
