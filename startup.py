from runtime.builder import ApplicationBuilder
from runtime.context import Context
from runtime.dependency_injection import services
from runtime.options import CommandsOptions
from runtime.middleware import CommandsMiddleware
from modules import basic, user_request, keyboard, admin_module


class Startup:

    def configure_services(self):
        services.add_sessions()
        services.add_singleton(CommandsMiddleware)
        services.add_singleton(keyboard.Keyboard)
        pass

    def configure(self, app_builder: ApplicationBuilder):
        app_builder.use_bot_token("1227930360:AAH6CPN_L5S7blA_Tt0pn6OrffKcQen51jo")
        app_builder.timeout = 3000
        app_builder.updates_limit = 3
        app_builder.use_commands(self.configure_commands)

    def configure_commands(self):
        options = CommandsOptions()
        options.use_commands_modules([basic, user_request, admin_module])
        return options
