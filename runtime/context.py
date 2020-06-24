from telegram import Update, Bot


class Context:
    def __init__(self, update: Update, bot: Bot):
        self.__bot = bot
        self.__update = update

    @property
    def bot(self) -> Bot:
        return self.__bot

    @property
    def update(self) -> Update:
        return self.__update
