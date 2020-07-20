import inspect
import os
import typing
from datetime import datetime

import telegram

from runtime.command_model import PropertyDefinition, CommandModelDefinition
from runtime.commands import ModelCommandBase, MessageResult
from runtime.context import Context
from runtime.logging import Logger
from runtime.options import Options, CommandsOptions
from runtime.resources import IResourceProvider
from resources.designer import Resources


class Middleware:

    def __init__(self):
        self.__next: typing.Optional[typing.Callable[[Context], None]] = None

    def invoke(self, context: Context):
        self.invoke_next(context)

    def invoke_next(self, context: Context):
        if self.__next is not None:
            self.__next(context)

    def set_next(self, next_middleware_invoker: typing.Optional[typing.Callable[[Context], None]]):
        self.__next = next_middleware_invoker

    def configure(self, options: Options):
        pass


class CommandsMiddleware(Middleware):

    def __init__(self, logger: Logger):
        super().__init__()
        self.__logger = logger
        self.__commands_modules = None
        self.__suppress_command = False
        self.__error_handler = None
        self.__functions_dict: typing.Dict[str, typing.Tuple[object, str]] = dict()

    def configure(self, options: CommandsOptions):
        self.__error_handler = options["__error_handler__"]
        self.__commands_modules = options["__modules__"]

        for module in self.__commands_modules:
            all_classes = inspect.getmembers(module, inspect.isclass)
            for class_name, val in all_classes:
                if class_name.endswith("Commands"):
                    class_functions = inspect.getmembers(val, inspect.isfunction)
                    for func_name, _ in class_functions:
                        if func_name.endswith("_command"):
                            self.__functions_dict[func_name] = (module, class_name)

    def invoke(self, context: Context):

        if context.session is not None and context.session["__holding__"] is not None and context.session["__holding__"] != 0:
            context.session["__holding__"] -= 1
            command = context.session["__command__"]
            self.__logger.info("found hold command for user " + str(context.user.id) + " command: " + command)
        else:
            if context.bot_request.command is not None:
                command = context.bot_request.command[1:] + "_command"
            else:
                command = "unknown_command"

        if command not in self.__functions_dict:
            command = "unknown_command"
        if command not in self.__functions_dict:
            self.invoke_next(context)
            return

        controller = getattr(self.__functions_dict[command][0], self.__functions_dict[command][1])
        class_instance = context.services.get_instance(controller, context.user.id)
        class_instance.session = context.session
        class_instance.resources = context.resources
        class_instance.services = context.services
        class_instance.user = context.user
        class_instance.bot_request = context.bot_request
        class_instance.bot_response = context.bot_response

        command_callable = getattr(class_instance, command)
        try:
            command_result = command_callable(context.bot_request.args)
        except Exception as exception:
            self.__logger.error(str(exception) + " " + str(exception))
            if self.__error_handler is None:
                self.__logger.warn("error handler not found")
                if getattr(class_instance, "error_handler", None) is None:
                    raise exception
                self.__logger.info("using error handler for class " + str(class_instance))
                handler = getattr(class_instance, "error_handler")
                command_result = handler(exception)
            else:
                self.__logger.info("using common error handler")
                self.__error_handler(exception, context)
                return

        command_result.attach_to(context.bot_response)

        if class_instance.session is not None and class_instance.session["__redir__"] == 1:
            class_instance.session["__redir__"] = 0
        elif class_instance.session is not None and class_instance.session["__holding__"] is not None and \
                class_instance.session["__holding__"] != 0:
            self.__logger.info("redirected")
            class_instance.session["__command__"] = command

        self.invoke_next(context)


class CommandsModelMiddleware(Middleware):

    def __init__(self):
        super().__init__()
        entry_commands = list()
        members = vars(Resources.Models)
        name: str
        for name, value in members.items():
            if not name.startswith("__") and not callable(value):
                entry_commands.append(value)
        self.__model_names = entry_commands

    @staticmethod
    def __parse_enum(resources: IResourceProvider, input_text: str) -> typing.Tuple[str]:
        if input_text.startswith('@'):
            resource = input_text.replace("@strings/", "")
            values = resources.get_string_array(resource)
        else:
            values = input_text.split(',')
        result = list()
        for value in values:
            result.append(value.strip())
        return tuple(result)

    def invoke(self, context: Context):

        if context.session is None:
            self.invoke_next(context)
            return

        entry_commands = list()
        for model_name in self.__model_names:
            m_def = context.resources.get_model(model_name)
            entry_commands.append(m_def.entry_command)

        if "__current_command__" not in context.session.keys:
            if context.bot_request.command is None or not context.bot_request.command.startswith('/') or context.bot_request.command[1:] not in entry_commands:
                self.invoke_next(context)
                return
            else:
                for model_name in self.__model_names:
                    m_def = context.resources.get_model(model_name)
                    if m_def.entry_command == context.bot_request.command[1:]:
                        context.session["__current_command__"] = model_name
                context.session["__current_state__"] = "init"

        model_definition = context.resources.get_model(context.session["__current_command__"])
        handler: ModelCommandBase = context.services.get_instance(ModelCommandBase)
        if model_definition.handler_class is not None:
            handler = context.services.get_instance(model_definition.handler_class)

        handler.services = context.services
        handler.session = context.session
        handler.resources = context.resources
        handler.bot_request = context.bot_request
        handler.user = context.user
        handler.bot_response = context.bot_response

        model = None
        if model_definition.command_class is not None:
            model = model_definition.command_class()
            model = self.__fill_up_model(context, model)

        if context.bot_request.command is not None and context.bot_request.command.startswith('/'):
            if context.bot_request.command == "/edit":
                context.session["__current_state__"] = "edit"
                if len(context.bot_request.args) != 0:
                    prop_name = context.bot_request.message_text.replace("/edit ", "")
                    if prop_name == "__back__":
                        context.session["__stage__"] = "back"
                    else:
                        context.session["__current_state__"] = "prop_set"
                        context.session["__stage__"] = "show_hint"
                        context.session["__mode__"] = "manual"
                        for i in range(len(model_definition.required_properties)):
                            if model_definition.required_properties[i].name == prop_name:
                                context.session["__prop_index__"] = i
                        for i in range(len(model_definition.optional_options)):
                            if model_definition.optional_options[i].name == prop_name:
                                context.session["__prop_index__"] = i + len(model_definition.required_properties)

            elif context.bot_request.command == "/send":
                context.session["__current_state__"] = "send"
                if not model_definition.confirm_send:
                    context.session["__stage__"] = "yes"
                elif len(context.bot_request.args) == 0:
                    context.session["__stage__"] = "ask"
                else:
                    res = context.bot_request.args[0]
                    if res == "yes":
                        context.session["__stage__"] = "yes"
                    else:
                        context.session["__stage__"] = "no"

            elif context.bot_request.command == "/cancel":
                context.session["__current_state__"] = "cancel"
                if not model_definition.confirm_cancel:
                    context.session["__stage__"] = "yes"
                elif len(context.bot_request.args) == 0:
                    context.session["__stage__"] = "ask"
                else:
                    res = context.bot_request.args[0]
                    if res == "yes":
                        context.session["__stage__"] = "yes"
                    else:
                        context.session["__stage__"] = "no"

            elif context.session["__current_state__"] != "init":
                context.session["__current_state__"] = "cancel"
                context.session["__stage__"] = "ask"
                if not model_definition.confirm_cancel:
                    context.session["__stage__"] = "yes"
        else:
            if context.session["__current_state__"] != "prop_set" and context.session["__stage__"] != "enter_val":
                context.session["__current_state__"] = "cancel"
                context.session["__stage__"] = "ask"
                if not model_definition.confirm_cancel:
                    context.session["__stage__"] = "yes"

        if context.session["__current_state__"] == "init":
            handler.on_enter().attach_to(context.bot_response)
            context.session["__current_state__"] = "prop_set"
            context.session["__stage__"] = "show_hint"
            context.session["__mode__"] = "auto"
            context.session["__prop_index__"] = 0

        if context.session["__current_state__"] == "edit":
            if context.session["__stage__"] == "back":
                context.session["__current_state__"] = "review"
                context.session.remove("__stage__")
            else:
                review_text = handler.create_review(model)
                markup = self.__make_markup_for_edit(context, model_definition)
                handler.send_or_edit_message(message_id=context.bot_request.message_id, text=review_text, reply_markup=markup).attach_to(context.bot_response)

        if context.session["__current_state__"] == "send":
            if context.session["__stage__"] == "ask":
                markup = self.__make_send_confirm_markup(context)
                review_text = handler.create_review(model)
                confirm_text = context.resources.get_string(Resources.Strings.CONFIRM_SENDING)
                text = review_text + "\n\n" + confirm_text
                handler.send_or_edit_message(message_id=context.bot_request.message_id, text=text, reply_markup=markup).attach_to(context.bot_response)
                return
            if context.session["__stage__"] == "yes":
                complete_result = handler.on_complete(model)
                if isinstance(complete_result, str):
                    context.session["__current_state__"] = "review"
                    context.session["__add_text__"] = complete_result
                else:
                    complete_result.attach_to(handler.bot_response)
                    context.session.clear()
                    return
            if context.session["__stage__"] == "no":
                context.session["__current_state__"] = "review"

        if context.session["__current_state__"] == "cancel":
            if context.session["__stage__"] == "ask":
                markup = self.__make_cancel_confirm_markup(context)
                review_text = handler.create_review(model)
                confirm_text = context.resources.get_string(Resources.Strings.CONFIRM_CANCEL)
                text = review_text + "\n\n" + confirm_text
                handler.send_or_edit_message(message_id=context.bot_request.message_id, text=text, reply_markup=markup).attach_to(context.bot_response)
                return

            if context.session["__stage__"] == "yes":
                handler.on_cancel(model).attach_to(context.bot_response)
                context.session.clear()
                return

            if context.session["__stage__"] == "no":
                context.session["__current_state__"] = "review"

        if context.session["__current_state__"] == "prop_set":
            prop_index = context.session["__prop_index__"]
            if prop_index < len(model_definition.required_properties):
                prop_definition = model_definition.required_properties[prop_index]
            else:
                prop_definition = model_definition.optional_options[
                    prop_index - len(model_definition.required_properties)]

            if context.session["__stage__"] == "enter_val":
                if prop_definition.type == "str" or prop_definition.type == "int":
                    if prop_definition.type == "str":
                        prop_value = context.bot_request.message_text
                    else:
                        try:
                            prop_value = int(context.bot_request.message_text)
                        except ValueError:
                            handler.on_property_invalid_type(model, prop_definition.name, "int", context.bot_request.message_text).attach_to(context.bot_response)
                            return
                elif prop_definition.type == "bool":
                    prop_value = False
                    if context.bot_request.message_text == context.resources.get_string(Resources.Strings.YES):
                        prop_value = True
                    elif context.bot_request.message_text == context.resources.get_string(Resources.Strings.NO):
                        prop_value = False
                else:
                    select_list = self.__parse_enum(context.resources, prop_definition.type)
                    if context.bot_request.message_text not in select_list:
                        handler.on_property_invalid_type(model, prop_definition.name, prop_definition.type, context.bot_request.message_text).attach_to(context.bot_response)
                        return
                    prop_value = context.bot_request.message_text

                error = handler.on_property_set(model, prop_definition.name, prop_value)
                if error is not None:
                    handler.send_message(text=error).attach_to(context.bot_response)
                    return
                context.session["__property_" + prop_definition.name] = prop_value
                model = self.__fill_up_model(context, model)

                if context.session["__mode__"] == "auto" and prop_index < len(model_definition.required_properties) - 1:
                    context.session["__prop_index__"] = prop_index + 1
                    prop_definition = model_definition.required_properties[prop_index + 1]
                    context.session["__stage__"] = "show_hint"
                else:
                    context.session["__current_state__"] = "review"
                    context.session.remove("__prop_index__")
                    context.session.remove("__stage__")

            if context.session["__stage__"] == "show_hint":
                self.__prepare_for_property(prop_definition, handler)
                context.session["__stage__"] = "enter_val"
                return

        if context.session["__current_state__"] == "review":
            confirmation_text = handler.create_review(model)
            if "__add_text__" in context.session.keys:
                confirmation_text += '\n\n' + context.session["__add_text__"]
                context.session.remove("__add_text__")
            markup = self.__make_sending_markup(context, model_definition)
            handler.send_or_edit_message(message_id=context.bot_request.message_id, text=confirmation_text, reply_markup=markup).attach_to(context.bot_response)
            return

    @staticmethod
    def __make_sending_markup(context: Context,
                              model_definition: CommandModelDefinition) -> telegram.InlineKeyboardMarkup:
        buttons = []
        for p_def in model_definition.optional_options:
            b_text = p_def.name
            if p_def.text is not None:
                b_text = p_def.text
                if p_def.text.startswith('@'):
                    resource = p_def.text.replace("@strings/", "")
                    b_text = context.resources.get_string(resource)
            buttons.append([telegram.InlineKeyboardButton(text=b_text, callback_data="/edit " + p_def.name)])
        buttons.append([telegram.InlineKeyboardButton(context.resources.get_string(Resources.Strings.EDIT), callback_data="/edit")])
        buttons.append([
            telegram.InlineKeyboardButton(context.resources.get_string(Resources.Strings.CANCEL), callback_data="/cancel"),
            telegram.InlineKeyboardButton(context.resources.get_string(Resources.Strings.SEND), callback_data="/send")])
        return telegram.InlineKeyboardMarkup(buttons)

    @staticmethod
    def __make_cancel_confirm_markup(context: Context) -> telegram.InlineKeyboardMarkup:
        buttons = [[
            telegram.InlineKeyboardButton(context.resources.get_string(Resources.Strings.NO), callback_data="/cancel no"),
            telegram.InlineKeyboardButton(context.resources.get_string(Resources.Strings.YES), callback_data="/cancel yes")
        ]]
        return telegram.InlineKeyboardMarkup(buttons)

    @staticmethod
    def __make_send_confirm_markup(context: Context) -> telegram.InlineKeyboardMarkup:
        buttons = [[
            telegram.InlineKeyboardButton(context.resources.get_string(Resources.Strings.NO), callback_data="/send no"),
            telegram.InlineKeyboardButton(context.resources.get_string(Resources.Strings.YES), callback_data="/send yes")
        ]]
        return telegram.InlineKeyboardMarkup(buttons)

    @staticmethod
    def __make_markup_for_edit(context: Context,
                               model_definition: CommandModelDefinition) -> telegram.InlineKeyboardMarkup:
        buttons = []
        for p_def in model_definition.required_properties:
            b_text = p_def.name
            if p_def.text is not None:
                b_text = p_def.text
                if p_def.text.startswith('@'):
                    resource = p_def.text.replace("@strings/", "")
                    b_text = context.resources.get_string(resource)
            buttons.append([telegram.InlineKeyboardButton(text=b_text, callback_data="/edit " + p_def.name)])
        buttons.append([telegram.InlineKeyboardButton(text=context.resources.get_string(Resources.Strings.BACK), callback_data="/edit __back__")])
        return telegram.InlineKeyboardMarkup(buttons)

    @staticmethod
    def __prepare_for_property(property_definition: PropertyDefinition, handler: ModelCommandBase):

        hint = property_definition.hint
        if hint.startswith('@'):
            resource = property_definition.hint.replace("@strings/", "")
            hint = handler.resources.get_string(resource)

        if property_definition.type == "str" or property_definition.type == "int":
            handler.send_message(text=hint).attach_to(handler.bot_response)
            return

        if property_definition.type == "bool":
            buttons = [[
                telegram.InlineKeyboardButton(handler.resources.get_string(Resources.Strings.YES),
                                              callback_data=handler.resources.get_string(Resources.Strings.YES)),
                telegram.InlineKeyboardButton(handler.resources.get_string(Resources.Strings.NO),
                                              callback_data=handler.resources.get_string(Resources.Strings.NO))]]
            handler.send_or_edit_message(message_id=handler.bot_request.message_id, text=hint,
                                         reply_markup=telegram.InlineKeyboardMarkup(buttons)).attach_to(handler.bot_response)
            return

        parsed_enum = CommandsModelMiddleware.__parse_enum(handler.resources, property_definition.type)
        select_list = tuple(parsed_enum)
        buttons = list()
        for option in select_list:
            buttons.append([telegram.InlineKeyboardButton(option, callback_data=option)])
        handler.send_or_edit_message(message_id=handler.bot_request.message_id, text=hint,
                                     reply_markup=telegram.InlineKeyboardMarkup(buttons)).attach_to(handler.bot_response)

    @staticmethod
    def __fill_up_model(context: Context, model):
        for session_key in context.session.keys:
            if session_key.startswith("__property_"):
                model_prop_name = session_key.replace("__property_", "")
                model_prop_val = context.session[session_key]
                if hasattr(model, model_prop_name):
                    setattr(model, model_prop_name, model_prop_val)
        return model


class LoggingMiddleware(Middleware):

    def __init__(self):
        super().__init__()
        self.__log_path = "logs/"

    def invoke(self, context: Context):
        if not os.path.exists(self.__log_path):
            os.mkdir(self.__log_path)
        log_file = open(self.__log_path + str(context.user.id) + ".txt", "a", encoding='utf-8')
        log_file.write(str(datetime.now()) + " request: " + context.bot_request.message_text + "; command=" + str(context.bot_request.command) + " args=" + ",".join(context.bot_request.args) + "\n")
        log_file.close()
        self.invoke_next(context)


class ErrorHandlerMiddleware(Middleware):

    def __init__(self, logger: Logger):
        super().__init__()
        self.__logger = logger

    def invoke(self, context: Context):
        try:
            self.invoke_next(context)
        except Exception as exception:
            self.__logger.error(str(exception.__class__) + " " + str(exception))
            MessageResult("Oops, something went wrong. Please, contact SU head and tell your user id: " + str(context.user.id), context.user.id, None).attach_to(context.bot_response)
