from runtime.configuration import Configuration
from runtime.commandHandlers import StartCommand, MyCommand


class Startup:

    def configure(self, configuration: Configuration):
        configuration.use_bot_token("1114791345:AAFY4DwdCJEfqj5uRmcchjtcqgEo93Lf77I")
        configuration.timeout = 3
        configuration.updates_limit = 3
        configuration.use_command(StartCommand)
        configuration.use_command(MyCommand)
