import threading
import typing

import telegram

from runtime.bot import BotRequest, BotResponse
from runtime.builder import ApplicationBuilder
from runtime.commands import RedirectToCommandResult
from runtime.context import Context
from runtime.dependency_injection import ServiceCollection, ServiceProvider
from runtime.middleware import Middleware
from runtime.resources import IResourceProvider
from runtime.session import ISession
from runtime.user import User


class Pipeline:

    def __init__(self):
        self.__app_builder: typing.Optional[ApplicationBuilder] = None
        self.__polling_daemon: typing.Optional[threading.Thread] = None
        self.__services: typing.Optional[ServiceCollection] = None

    def configure(self, app_builder: ApplicationBuilder, services: ServiceCollection):
        self.__app_builder = app_builder
        self.__services = services

    def start_polling(self):
        if self.__app_builder is None:
            raise RuntimeError("Cannot start the bot")

        self.__polling_daemon = MainDaemon(self.__app_builder, self.__services)
        self.__polling_daemon.start()
        self.__polling_daemon.join()


class MainDaemon(threading.Thread):

    def __init__(self, app_builder: ApplicationBuilder, services: ServiceCollection):
        super().__init__(name="MainPipelineDaemon", daemon=True)
        self.__app_builder = app_builder
        self.__service_provider = ServiceProvider()
        self.__service_provider.populate(services.services)

    def run(self):
        service_provider = self.__service_provider
        limit = self.__app_builder.updates_limit
        timeout = self.__app_builder.timeout
        bot = self.__app_builder.bot
        offset = 0

        while True:
            # get available updates
            updates_list = bot.get_updates(offset, limit, timeout)
            current_update_index: int = 0

            while current_update_index < len(updates_list):
                update = updates_list[current_update_index]
                context = Context()
                request = BotRequest()
                if update.message is not None:
                    message: telegram.Message = update.message
                    if message.text is not None:
                        message_text: str = message.text
                        message_data = message_text.split()
                        request.message_text = message_text
                        if request.message_text.startswith('/'):
                            request.command = message_data[0]
                            if len(message_data) == 1:
                                request.args = []
                            else:
                                request.args = message_data[1:]
                        else:
                            request.command = None
                            request.args = message_data
                        request.callback_text = None
                        request.message_id = message.message_id
                        request.is_callback = False
                if update.callback_query is not None:
                    callback_query: telegram.CallbackQuery = update.callback_query
                    if callback_query.data is not None:
                        callback_text: str = callback_query.data
                        callback_data = callback_text.split()
                        request.message_text = callback_text
                        if callback_text.startswith('/'):
                            request.command = callback_data[0]
                            if len(callback_data) == 1:
                                request.args = []
                            else:
                                request.args = callback_data[1:]
                        else:
                            request.command = None
                            request.args = callback_data
                        request.callback_text = callback_text
                        callback_message: telegram.Message = callback_query.message
                        request.message_id = callback_message.message_id
                        request.is_callback = True
                session = typing.cast(ISession, self.__service_provider.get_instance(ISession))
                resources = typing.cast(IResourceProvider, self.__service_provider.get_instance(IResourceProvider))
                response = BotResponse()
                telegram_user: telegram.User = update.effective_user
                user = User()
                user.id = telegram_user.id
                user.username = telegram_user.username
                user.first_name = telegram_user.first_name
                user.last_name = telegram_user.last_name

                context.session = session
                context.services = service_provider
                context.bot_request = request
                context.bot_response = response
                context.configuration = telegram_user.language_code
                context.user = user
                context.resources = resources
                session.id = user.id
                resources.configuration = context.configuration
                session.load()

                components = self.__app_builder.build()
                pipeline: typing.List[Middleware] = list()

                for i in range(len(components) - 1, -1, -1):
                    instance: Middleware = typing.cast(Middleware, service_provider.get_instance(components[i][0], user.id))
                    pipeline.append(instance)
                    if components[i][1] is not None:
                        instance.configure(components[i][1]())

                    if i != len(components) - 1:
                        instance.set_next(pipeline[len(components) - 2 - i].invoke)

                pipeline.reverse()

                if len(pipeline) != 0:
                    pipeline[0].invoke(context)
                    session.commit()
                    redirected = False
                    while len(context.bot_response.actions_queue) > 0:
                        result = context.bot_response.pop_action_at(0)
                        if isinstance(result, RedirectToCommandResult):
                            redirected = True
                            break
                        try:
                            result.execute(bot)
                        except:
                            pass
                    if redirected:
                        continue

                offset = update.update_id + 1
                current_update_index += 1
