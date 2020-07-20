from modules.commands import Handler
from runtime.builder import ApplicationBuilder
from runtime.commands import ModelCommandBase
from runtime.logging import Logger
from runtime.middleware import CommandsMiddleware, CommandsModelMiddleware, ErrorHandlerMiddleware, LoggingMiddleware
from runtime.options import CommandsOptions
import runtime.dependency_injection
import runtime.session
import modules.commands
from runtime.resources import XmlResourceParser, IResourceParser, IResourceProvider, Resources


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
        services.add_scoped(Handler)
        services.add_singleton(Logger)
        services.add_singleton(ErrorHandlerMiddleware)
        services.add_singleton(LoggingMiddleware)

    def configure(self, app_builder: ApplicationBuilder):
        app_builder.use_bot_token("1114791345:AAFY4DwdCJEfqj5uRmcchjtcqgEo93Lf77I")
        app_builder.timeout = 3000
        app_builder.updates_limit = 3
        app_builder.use_middleware(LoggingMiddleware)
        app_builder.use_middleware(CommandsModelMiddleware)
        app_builder.use_commands(self.configure_commands)

    def configure_commands(self):
        options = CommandsOptions()
        options.use_commands_modules([modules.commands])
        return options
