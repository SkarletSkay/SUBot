from runtime.builder import ApplicationBuilder
from runtime.context import Context
from runtime.dependency_injection import services
from runtime.options import CommandsOptions
from runtime.middleware import CommandsMiddleware
import commands


class Startup:

    def configure_services(self):
        services.add_sessions()
        services.add_singleton(CommandsMiddleware)
        pass

    def configure(self, app_builder: ApplicationBuilder):
        app_builder.use_bot_token("1114791345:AAFY4DwdCJEfqj5uRmcchjtcqgEo93Lf77I")
        app_builder.timeout = 3000
        app_builder.updates_limit = 3
        app_builder.use_commands(self.configure_commands)

    def configure_commands(self):
        options = CommandsOptions()
        options.use_commands_module(commands)
        return options
