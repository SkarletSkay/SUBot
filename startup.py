from runtime.builder import ApplicationBuilder
from runtime.commands import ModelCommandBase
from runtime.logging import Logger
from runtime.middleware import CommandsMiddleware, CommandsModelMiddleware, ErrorHandlerMiddleware, LoggingMiddleware
from runtime.options import CommandsOptions
import runtime.dependency_injection
import runtime.session
from runtime.resources import XmlResourceParser, IResourceParser, IResourceProvider, Resources
from modules import basic, database, keyboard, user_request, admin_module


class Startup:

    def configure_services(self, services: runtime.dependency_injection.ServiceCollection):
        services.add_singleton(CommandsMiddleware)
        services.add_commands(self.configure_commands)
        services.add_singleton(runtime.session.ISession, runtime.session.Session)
        services.add_singleton(runtime.session.ISessionStorage, runtime.session.FileSessionStorage)
        services.add_singleton(IResourceParser, XmlResourceParser)
        services.add_singleton(CommandsModelMiddleware)
        services.add_singleton(IResourceProvider, Resources)
        services.add_scoped(ModelCommandBase)
        services.add_scoped(user_request.Handler)
        services.add_singleton(Logger)
        services.add_singleton(ErrorHandlerMiddleware)
        services.add_singleton(LoggingMiddleware)
        services.add_singleton(database.DataBase)
        services.add_scoped(keyboard.Keyboard)

    def configure(self, app_builder: ApplicationBuilder):
        app_builder.use_bot_token("1227930360:AAH6CPN_L5S7blA_Tt0pn6OrffKcQen51jo")
        app_builder.timeout = 3000
        app_builder.updates_limit = 3
        app_builder.use_middleware(ErrorHandlerMiddleware)
        app_builder.use_middleware(LoggingMiddleware)
        app_builder.use_middleware(CommandsModelMiddleware)
        app_builder.use_commands(self.configure_commands)

    def configure_commands(self):
        options = CommandsOptions()
        options.use_commands_modules([admin_module, basic])
        return options
