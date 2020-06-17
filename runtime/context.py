from telegram import Update, User, Chat, Bot, Message
from datetime import datetime


class Context:

    def __init__(self, bot: Bot, user: User, chat: Chat, updates=None):
        self.__bot = bot
        self.__prev_updates = [] if updates is None else list(updates)
        self.__user = user
        self.__chat = chat

    @property
    def prev_updates(self) -> tuple:
        return tuple(self.__prev_updates)

    @property
    def bot(self) -> Bot:
        return self.__bot

    @property
    def user(self) -> User:
        return self.__user

    @property
    def chat(self) -> Chat:
        return self.__chat

    def add_update(self, update: Update):
        if update.effective_user != self.__user or update.effective_chat != self.__chat:
            return

        self.__prev_updates.append(update)

    def import_updates(self, updates: tuple):
        self.__prev_updates = list(updates)


class MessageContext(Context):

    def __init__(self, bot: Bot, user: User, chat: Chat, updates=None):
        super().__init__(bot, user, chat, updates)
        self.__message_id = 0
        self.__message_text = ""
        self.__date = datetime.min

    def add_update(self, update: Update):
        super().add_update(update)
        # Callbacks appear as MessageContext since they are restored
        # :see: pipeline.py, line 50 - fixed that
        # :see: method __init__ of Context
        self.__message_id = update.message.message_id
        self.__date = update.message.date
        self.__message_text = update.message.text

    @property
    def message_id(self) -> int:
        return self.__message_id

    def send_message(self, text: str):
        self.bot.send_message(self.chat.id, text)

    @property
    def text(self) -> str:
        return self.__message_text

    @property
    def date(self) -> datetime:
        return self.__date


class CallbackContext(Context):

    def __init__(self, bot: Bot, user: User, chat: Chat, updates=None):
        super().__init__(bot, user, chat, updates)
        self.__callback_id = 0
        self.__message = Message(0, 0, datetime.min, chat)
        self.__data = ""

    def add_update(self, update: Update):
        super().add_update(update)
        self.__callback_id = update.callback_query.id
        self.__message = update.callback_query.message
        self.__data = update.callback_query.data

    @property
    def callback_id(self) -> int:
        return self.__callback_id

    @property
    def message(self) -> Message:
        return self.__message

    @property
    def data(self) -> str:
        return self.__data
