from runtime.builder import ApplicationBuilder
from runtime.dependency_injection import services
from runtime.options import CommandsOptions
from runtime.middleware import CommandsMiddleware
import commands


class Startup:

    def configure_services(self):
        services.add_sessions()
        services.add_singleton(CommandsMiddleware)

    def configure(self, app_builder: ApplicationBuilder):
        app_builder.use_bot_token("1222869042:AAGqMH0Nn5mVIHnuK6c_q_pG1FlzIgBL3tk")
        app_builder.timeout = 3000
        app_builder.updates_limit = 3
        app_builder.use_commands(self.configure_commands)

    def configure_commands(self):
        options = CommandsOptions()
        options.use_commands_modules(list((commands,)))
        return options
