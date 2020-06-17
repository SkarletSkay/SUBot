from runtime.configuration import Configuration
from runtime.commandHandlers import CommandHandlerBase
from runtime.contextStorage import DefaultContextStorage
from runtime.context import MessageContext, CallbackContext
from threading import Thread


class Pipeline:

    def __init__(self):
        self.__configuration = None
        self.__polling_daemon = None

    def configure(self, configuration: Configuration):
        self.__configuration = configuration

    def start_polling(self):
        if self.__configuration is None:
            raise RuntimeError("Configuration should be set before starting bot")

        self.__polling_daemon = MainDaemon(self)
        self.__polling_daemon.start()
        self.__polling_daemon.join()

    def get_configuration(self) -> Configuration:
        return self.__configuration


class MainDaemon(Thread):

    def __init__(self, pipeline: Pipeline):
        super().__init__(name="MainPipelineDaemon", daemon=True)
        self.__pipeline = pipeline
        self.__contextStorage = DefaultContextStorage()

    def run(self):
        configuration = self.__pipeline.get_configuration()
        storage = self.__contextStorage
        limit = configuration.updates_limit
        timeout = configuration.timeout
        commands = configuration.get_commands()
        bot = configuration.get_bot()
        offset = 0

        while True:
            updates_list = bot.get_updates(offset, limit, timeout)
            for update in updates_list:
                for command in commands:
                    context = storage.restore_context(update.effective_user.id, update.effective_chat.id)
                    if update.message is not None and (context is None or isinstance(context, CallbackContext)):
                        if context is None:
                            context = MessageContext(bot, update.effective_user, update.effective_chat)
                        else:
                            context = MessageContext(bot, update.effective_user, update.effective_chat, context.prev_updates)
                    elif update.callback_query is not None and (context is None or isinstance(context, MessageContext)):
                        if context is None:
                            context = CallbackContext(bot, update.effective_user, update.effective_chat)
                        else:
                            context = CallbackContext(bot, update.effective_user, update.effective_chat, context.prev_updates)

                    context.add_update(update)
                    command_instance: CommandHandlerBase = command(context)
                    if configuration.is_holding(update.effective_user.id, update.effective_chat.id, command) \
                            or command_instance.satisfy(update):

                        executed = command_instance.execute_async()
                        if command_instance.holding != 0:
                            configuration.hold_for(update.effective_user.id, update.effective_chat.id,
                                                   command, command_instance.holding)

                        if executed:
                            offset = update.update_id + 1

                        storage.store_context(update.effective_user.id, update.effective_chat.id, context)
                        if configuration.is_holding(update.effective_user.id, update.effective_chat.id, command):
                            configuration.decrease_holding(update.effective_user.id, update.effective_chat.id, command)
                        break
