from threading import Thread
from typing import List

from runtime.builder import ApplicationBuilder
from runtime.context import Context
from runtime.dependency_injection import services

from runtime.middleware import Middleware


class Pipeline:

    def __init__(self):
        self.__app_builder = None
        self.__polling_daemon = None
        self.__services = None

    def configure(self, app_builder: ApplicationBuilder):
        self.__app_builder = app_builder

    def start_polling(self):
        if self.__app_builder is None:
            raise RuntimeError("Cannot start the bot")

        self.__polling_daemon = MainDaemon(self.__app_builder)
        self.__polling_daemon.start()
        self.__polling_daemon.join()


class MainDaemon(Thread):

    def __init__(self, app_builder: ApplicationBuilder):
        super().__init__(name="MainPipelineDaemon", daemon=True)
        self.__app_builder = app_builder

    def run(self):
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
                context = Context(update, bot)
                components = self.__app_builder.build()
                pipeline: List[Middleware] = list()

                for i in range(len(components) - 1, -1, -1):
                    instance: Middleware = services.get_instance(components[i][0], hash(update.effective_chat.id))
                    pipeline.append(instance)
                    if components[i][1] is not None:
                        instance.configure(components[i][1])

                    if i != len(components) - 1:
                        instance.set_next(pipeline[len(components) - 2 - i].invoke)

                pipeline.reverse()

                if len(pipeline) != 0:
                    pipeline[0].invoke(context)

                offset = update.update_id + 1
                current_update_index += 1
