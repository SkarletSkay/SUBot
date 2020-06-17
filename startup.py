from runtime.configuration import Configuration
from runtime.commandHandlers import StartCommand, NewRequestCommand, MyCommand


class Startup:

    def configure(self, configuration: Configuration):
        configuration.use_bot_token("1227930360:AAH6CPN_L5S7blA_Tt0pn6OrffKcQen51jo")
        configuration.timeout = 3
        configuration.updates_limit = 3
        configuration.use_command(StartCommand)
        configuration.use_command(NewRequestCommand)
        configuration.use_command(MyCommand)
