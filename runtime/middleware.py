from typing import Dict, Optional, Callable, Tuple

from runtime.options import Options
from runtime.session import SessionControl, Session
from runtime.dependency_injection import services
from runtime.commands import CommandsBase, CommandResult, RedirectToCommandResult
from runtime.context import Context
import inspect


class Middleware:

    def __init__(self):
        self.__next: Optional[Callable[[Context], None]] = None

    def configure(self, options: Options):
        pass

    def invoke(self, context: Context):
        self.invoke_next(context)

    def invoke_next(self, context: Context):
        if self.__next is not None:
            self.__next(context)

    def set_next(self, next_middleware_invoker: Optional[Callable[[Context], None]]):
        self.__next = next_middleware_invoker


class CommandsMiddleware(Middleware):

    def __init__(self, session_storage: SessionControl):
        super().__init__()
        self.__commands_modules = None
        self.__suppress_command = False
        self.__error_handler = None
        self.__session_storage = session_storage
        self.__functions_dict: Dict[str, Tuple[object, str]] = dict()

    def configure(self, options: Options):
        self.__suppress_command = options["__suppress_command_literals__"]
        self.__error_handler = options["__error_handler__"]
        self.__commands_modules = options["__modules__"]

        for module in self.__commands_modules:
            all_classes = inspect.getmembers(module, inspect.isclass)
            for class_name, val in all_classes:
                if class_name.endswith("Commands"):
                    services.add_scoped(val)
                    class_functions = inspect.getmembers(val, inspect.isfunction)
                    for func_name, _ in class_functions:
                        if func_name.endswith("_command"):
                            self.__functions_dict[func_name] = (module, class_name)

    def invoke(self, context: Context):
        should_repeat = True
        session = self.__session_storage.get_session(hash(context.update.effective_chat.id))

        while should_repeat:
            if session is None:  # or create if it does not exist
                session = Session(context.update.effective_user, context.update.effective_chat)
                session["__holding__"] = 0

            if session["__holding__"] != 0:
                session["__holding__"] -= 1
                command = session["__command__"]
            else:
                if context.update.message is not None and context.update.message.text is not None:
                    message_text = context.update.message.text
                elif context.update.callback_query is not None and context.update.callback_query.data is not None:
                    message_text: str = context.update.callback_query.data
                else:
                    break

                command = message_text.strip().split()[0]
                if command[0] == '/':
                    command = command[1:]
                command += "_command"

            if command not in self.__functions_dict:
                command = "unknown_command"
            if command not in self.__functions_dict:
                break

            controller = getattr(self.__functions_dict[command][0], self.__functions_dict[command][1])
            class_instance: CommandsBase = services.get_instance(controller, session.identifier)
            class_instance.session = session
            class_instance.bot = context.bot

            class_instance.message = context.update.message
            class_instance.callback_query = context.update.callback_query

            command_callable = getattr(class_instance, command)
            command_result: Optional[CommandResult] = None
            try:
                if context.update.message is not None:
                    command_result = command_callable(context.update.message.text)
                elif context.update.callback_query.data is not None:
                    command_result = command_callable(context.update.callback_query.data)
            except Exception as exception:
                if self.__error_handler is None:
                    if getattr(class_instance, "error_handler", None) is None:
                        raise exception
                    handler = getattr(class_instance, "error_handler")
                    error_result: CommandResult = handler(exception)
                    if isinstance(error_result, RedirectToCommandResult):
                        continue
                    error_result.execute(context.bot)
                    class_instance.session["__holding__"] = 0
                    break
                else:
                    self.__error_handler(exception, context)
                    break

            if isinstance(command_result, RedirectToCommandResult):
                continue

            command_result.execute(context.bot)
            if class_instance.session["__holding__"] != 0:
                class_instance.session["__command__"] = command
                self.__session_storage.set_session(class_instance.session.identifier, class_instance.session)

            should_repeat = False

        self.invoke_next(context)
