from datetime import datetime
from functools import wraps

from telegram import ParseMode

from modules.database import DataBase
from modules.keyboard import Keyboard
from runtime.commands import CommandsBase

admins = {"molberte", "ntdesmond", "lexa_small", "alias25664", "EgorBak"}


def admin_only(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_admin():
            return self.send_message(
                "Can not access. Not enough rights", reply_markup=None
            )
        return func(self, *args, **kwargs)

    return wrapper


class AdminCommands(CommandsBase):
    pagination_step = 3

    def __init__(self, keyboard: Keyboard, database: DataBase):
        super().__init__()
        self.__keyboard = keyboard
        self.__database = database
        self.__category_prefix = "/new_request_action "

    def is_admin(self) -> bool:
        return self.user.username in admins

    @staticmethod
    def build_request_body(db_item):
        msg = (
            f"*Category:* {db_item.get('category')}\n"
            f"*Date:* {db_item.get('timestamp', datetime.now()).strftime('%d-%b-%Y (%H:%M)')}\n"
            f"*Closed:* `{db_item.get('closed', False)}`\n"
            f"*Taken:* `{db_item.get('taken', False)}`\n"
        )
        if db_item.get("taken"):
            msg += f"*Mentor:* [mentor](tg://user?id={db_item.get('mentor_id')})\n"
        return msg + f"*Message*:\n```\n{db_item.get('text')}\n```"

    @admin_only
    def get_user_messages_command(self, *args):
        if self.bot_request.is_callback:
            if self.bot_request.message_text == "/get_user_messages cancel":
                self.hold_next(0)  # don't hold anymore
                return self.edit_message(
                    self.bot_request.message_id,
                    "You cancelled user messages listing",
                    None,
                )
            # quick fix so that keyboard doesn't crash
            elif self.bot_request.message_text == "/get_user_messages":
                self.hold_next(1)
                return self.send_message(
                    "Send the alias of user you want to get messages from",
                    reply_markup=None,
                )
            elif self.bot_request.message_text.startswith("/get_user_messages"):
                alias, action, offset = self.bot_request.message_text[
                    len("/get_user_messages "):
                ].split(":")
                offset = int(offset)
                if action == ">":
                    new_offset = offset + self.pagination_step
                else:
                    new_offset = offset - self.pagination_step
                messages, count = self.__database.get_requests_by_alias(
                    alias, offset=new_offset
                )
                res = (
                    "\n\n".join([self.build_request_body(msg) for msg in messages])
                    or "None"
                )
                return self.edit_message(
                    self.bot_request.message_id,
                    res,
                    new_markup=self.__keyboard.get_user_messages_paginated(
                        alias,
                        new_offset,
                        l_available=new_offset > 0,
                        r_available=count > new_offset,
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
        else:
            if self.bot_request.message_text == "/get_user_messages":
                self.hold_next(1)
                return self.send_message(
                    "Send the alias of user you want to get messages from",
                    reply_markup=None,
                )
            else:
                messages, count = self.__database.get_requests_by_alias(self.bot_request.message_text)
                if messages:
                    res = "\n\n".join(
                        [self.build_request_body(msg) for msg in messages]
                    )
                    return self.send_message(
                        res,
                        reply_markup=self.__keyboard.get_user_messages_paginated(
                            self.bot_request.message_text,
                            0,
                            l_available=False,
                            r_available=count > self.pagination_step,
                        ),
                        parse_mode=ParseMode.MARKDOWN,
                    )
                else:
                    return self.send_message(
                        "There is no history with that user", reply_markup=None
                    )

    @admin_only
    def check_new_requests_command(self):
        res = []
        if self.bot_request.message_text == "/check_new_requests":
            messages = self.__database.get_new_requests()
            if messages:
                for msg in messages:
                    res.append(
                        self.send_message(
                            self.build_request_body(msg),
                            reply_markup=self.__keyboard.new_request_actions(
                                msg["_id"]
                            ),
                            parse_mode=ParseMode.MARKDOWN,
                        )
                    )
            else:
                return self.send_message(
                    "No new requests found. Either you did a great job and answered all requests or students don't use this piece of shit",
                    reply_markup=None,
                )
        return self.compound_result(tuple(res))

    def new_request_action_command(self, *args):
        if self.bot_request.message_text.startswith(self.__category_prefix):
            request_id, command = self.bot_request.message_text[len(self.__category_prefix):].split(":")
            user_id = self.user.id
            alias = self.user.username
            if command == "Take":
                self.__database.take_request(
                    request_id=request_id, mentor_id=user_id
                )
                return self.edit_message(
                    self.bot_request.message_id, "Taken", None
                )
            elif command == "Respond":
                request = self.__database.get_request_by_id(request_id)
                user_id = request.get("user_id")
                self.hold_next(1)
                self.session["request_user_id"] = user_id
                self.session["request_respond_id"] = request_id
                self.session[
                    "new_request_message_id"
                ] = self.bot_request.message_id
                return self.send_message(f"Enter text to respond to [the user](tg://user?id={user_id})", None,
                                         parse_mode=ParseMode.MARKDOWN)
            elif command == "Close":
                self.__database.close_request(request_id=request_id)
                return self.edit_message(
                    self.bot_request.message_id, "Closed", None
                )
        elif self.holding_left == 0 and self.session["new_request_message_id"] and self.session["request_respond_id"]:
            request_id = self.session["request_respond_id"]
            user_id = self.session["request_user_id"]
            return self.compound_result(
                (
                    self.edit_message(
                        message_id=self.session["new_request_message_id"],
                        new_text="Your response was successfully sent"
                    ),
                    self.send_message(
                        chat_id=user_id,
                        text=f"*Your request was reviewed.*\nAnswer:\n```\n{self.bot_request.message_text}\n```",
                        reply_markup=None,
                        parse_mode=ParseMode.MARKDOWN,
                    ),
                )
            )
        else:
            return self.send_message(
                "No new requests found. Either you did a great job and answered all requests or students don't use this piece of shit",
                reply_markup=None,
            )
