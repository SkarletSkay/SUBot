import typing

import telegram

from resources.designer import Resources
from runtime.bot import BotResponse, BotRequest
from runtime.dependency_injection import IServiceProvider
from runtime.resources import IResourceProvider
from runtime.session import ISession
from runtime.user import User


class CommandResult:

    def attach_to(self, response: BotResponse):
        pass

    def execute(self, bot: telegram.Bot):
        pass


class CommandsBase:

    def __init__(self):
        self.__session: typing.Optional[ISession] = None
        self.__bot_request: typing.Optional[BotRequest] = None
        self.__bot_response: typing.Optional[BotResponse] = None
        self.__resources: typing.Optional[IResourceProvider] = None
        self.__user: typing.Optional[User] = None
        self.__services: typing.Optional[IServiceProvider] = None

    @property
    def resources(self) -> typing.Optional[IResourceProvider]:
        return self.__resources

    @resources.setter
    def resources(self, value: typing.Optional[IResourceProvider]):
        self.__resources = value

    @property
    def services(self) -> typing.Optional[IServiceProvider]:
        return self.__services

    @services.setter
    def services(self, value: typing.Optional[IServiceProvider]):
        self.__services = value

    @property
    def bot_request(self) -> typing.Optional[BotRequest]:
        return self.__bot_request

    @bot_request.setter
    def bot_request(self, value: typing.Optional[BotRequest]):
        self.__bot_request = value

    @property
    def bot_response(self) -> typing.Optional[BotResponse]:
        return self.__bot_response

    @bot_response.setter
    def bot_response(self, value: typing.Optional[BotResponse]):
        self.__bot_response = value

    @property
    def user(self) -> typing.Optional[User]:
        return self.__user

    @user.setter
    def user(self, value: typing.Optional[User]):
        self.__user = value

    @property
    def holding_left(self) -> int:
        if self.session["__holding__"] is not None:
            return self.session["__holding__"]
        return 0

    @property
    def session(self) -> typing.Optional[ISession]:
        return self.__session

    @session.setter
    def session(self, value: typing.Optional[ISession]):
        self.__session = value

    def hold_next(self, duration: int = 1):
        self.session["__holding__"] = duration

    def send_message(self, text: typing.Optional[str] = None, resource: typing.Optional[str] = None,
                     reply_markup: typing.Optional[telegram.ReplyMarkup] = None, chat_id: typing.Optional[int] = None,
                     parse_mode: telegram.parsemode.ParseMode = None) -> CommandResult:
        if resource is not None:
            text = self.resources.get_string(resource)
        if chat_id is None:
            result = MessageResult(text, self.user.id, reply_markup, parse_mode)
        else:
            result = MessageResult(text, chat_id, reply_markup, parse_mode)
        return result

    def no_message(self) -> CommandResult:
        return EmptyResult()

    def redirect_to_command(self, command: str) -> CommandResult:
        self.session["__holding__"] = 1
        self.session["__command__"] = command
        self.session["__redir__"] = 1
        return RedirectToCommandResult()

    def send_message_list(self, messages_list: typing.Optional[typing.List[str]] = None, messages_resources: typing.Optional[typing.List[str]] = None, message_array: typing.Optional[str] = None):
        if message_array is not None:
            messages_list = self.resources.get_string_array(message_array)
        elif messages_resources is not None:
            messages_list = list()
            for res_name in messages_resources:
                messages_list.append(self.resources.get_string(res_name))

        result = MessageListResult(self.user.id, messages_list)
        return result

    def edit_message(self, message_id: int, new_text: typing.Optional[str] = None, new_text_resource: typing.Optional[str] = None,
                     new_markup: telegram.ReplyMarkup = None, parse_mode: telegram.parsemode.ParseMode = None):
        if new_text_resource is not None:
            new_text = self.resources.get_string(new_text_resource)
        result = EditMessageResult(self.user.id, message_id, new_text, new_markup, parse_mode)
        return result

    def reply_to_message(self, message_id: int, text: typing.Optional[str] = None, text_resource: typing.Optional[str] = None, reply_markup: telegram.ReplyMarkup = None):
        if text_resource is not None:
            text = self.resources.get_string(text_resource)
        result = ReplyToMessageResult(message_id, self.user.id, text, reply_markup)
        return result

    def compound_result(self, results: typing.Tuple[CommandResult, ...]):
        return CompoundResult(list(results))

    def send_or_edit_message(self, message_id: int, text: str, text_resource: str = None, reply_markup: telegram.InlineKeyboardMarkup = None):
        message_text = text
        if text_resource is not None:
            message_text = self.resources.get_string(text_resource)
        return SendOrEditMessage(self.user.id, message_id, message_text, reply_markup)


class CompoundResult(CommandResult):
    def __init__(self, results: typing.List[CommandResult]):
        self.__results = results

    def attach_to(self, response: BotResponse):
        for result in self.__results:
            response.add_action(result)


class MessageResult(CommandResult):

    def __init__(self, message: str, chat_id: int, reply_markup: telegram.ReplyMarkup, parse_mode: telegram.ParseMode = None):
        self.__message = message
        self.__chat_id = chat_id
        self.__markup = reply_markup
        self.__parse_mode = parse_mode

    def execute(self, bot: telegram.Bot):
        bot.send_message(self.__chat_id, self.__message, reply_markup=self.__markup, parse_mode=self.__parse_mode)

    def attach_to(self, response: BotResponse):
        response.add_action(self)


class EmptyResult(CommandResult):

    def execute(self, bot: telegram.Bot):
        pass


class RedirectToCommandResult(CommandResult):

    def attach_to(self, response: BotResponse):
        response.add_action(self)


class ReplyToMessageResult(CommandResult):
    def __init__(self, message_id: int, chat_id: int, text: str, reply_markup):
        self.__message_id = message_id
        self.__chat_id = chat_id
        self.__text = text
        self.__markup = reply_markup

    def execute(self, bot: telegram.Bot):
        bot.send_message(self.__chat_id, self.__text, reply_to_message_id=self.__message_id, reply_markup=self.__markup)

    def attach_to(self, response: BotResponse):
        response.add_action(self)


class MessageListResult(CommandResult):
    def __init__(self, chat_id: int, messages: typing.List[str]):
        self.__chat_id = chat_id
        self.__messages = messages

    def execute(self, bot: telegram.Bot):
        for message in self.__messages:
            bot.send_message(self.__chat_id, message)

    def attach_to(self, response: BotResponse):
        response.add_action(self)


class EditMessageResult(CommandResult):
    def __init__(self, chat_id: int, message_id: int, new_text: str, new_markup: telegram.ReplyMarkup, parse_mode: telegram.ParseMode = None):
        self.__chat_id = chat_id
        self.__message_id = message_id
        self.__new_text = new_text
        self.__new_markup = new_markup
        self.__parse_mode = parse_mode

    def execute(self, bot: telegram.Bot):
        if self.__new_text is not None:
            bot.edit_message_text(self.__new_text, chat_id=self.__chat_id, message_id=self.__message_id, parse_mode=self.__parse_mode)
        if self.__new_markup is not None:
            bot.edit_message_reply_markup(self.__chat_id, self.__message_id, reply_markup=self.__new_markup)

    def attach_to(self, response: BotResponse):
        response.add_action(self)


class EditMessageMarkupResult(CommandResult):
    def __init__(self, chat_id: int, message_id: int, new_markup):
        self.__chat_id = chat_id
        self.__new_markup = new_markup
        self.__message_id = message_id

    def execute(self, bot: telegram.Bot):
        bot.edit_message_reply_markup(chat_id=self.__chat_id, message_id=self.__message_id, reply_markup=self.__new_markup)

    def attach_to(self, response: BotResponse):
        response.add_action(self)


class ModelCommandBase(CommandsBase):

    def on_enter(self) -> CommandResult:
        return self.no_message()

    def create_review(self, model) -> str:
        result = "Request:\n\n"
        for entry in self.session.keys:
            if entry.startswith("__property_"):
                prop_name = entry.replace("__property_", "")
                value = self.session[entry]
                if value is not None:
                    result += prop_name + ":\n"
                    result += str(value) + "\n\n"
        return result

    def on_property_set(self, model, property_name: str, value) -> typing.Optional[str]:
        return None

    def on_property_invalid_type(self, model, property_name: str, expected_type: str, value) -> CommandResult:
        return self.send_message(resource=Resources.Strings.INVALID_PROPERTY)

    def on_complete(self, model) -> typing.Union[CommandResult, str]:
        return self.send_message("You successfully sent")

    def on_cancel(self, model) -> CommandResult:
        return self.send_message("You canceled")


class SendOrEditMessage(CommandResult):

    def __init__(self, chat_id: int, message_id: int, text: str, reply_markup: telegram.InlineKeyboardMarkup):
        self.__text = text
        self.__markup = reply_markup
        self.__message_id = message_id
        self.__chat = chat_id

    def execute(self, bot: telegram.Bot):
        try:
            EditMessageResult(self.__chat, self.__message_id, self.__text, self.__markup).execute(bot)
        except telegram.error.BadRequest:
            MessageResult(self.__text, self.__chat, self.__markup).execute(bot)

    def attach_to(self, response: BotResponse):
        response.add_action(self)
