from datetime import datetime
from functools import wraps

from telegram import ParseMode

from database import DataBase
from modules.keyboard import Keyboard
from runtime.commands import CommandsBase

admins = {"molberte", "ntdesmond", "lexa_small", "alias25664"}


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

    def __init__(self, keyboard: Keyboard):
        super().__init__()
        self.__keyboard = keyboard
        self.__category_prefix = "/new_request_action "

    def is_admin(self) -> bool:
        return self.session.user.username in admins

    @staticmethod
    def build_request_body(db_item):
        msg = (
            f"*Category:* {db_item.get('category')}\n"
            f"*Date:* {db_item.get('timestamp', datetime.now()).strftime('%d-%b-%Y (%H:%M)')}\n"
            f"*Closed:* `{db_item.get('closed', False)}`\n"
            f"*Taken:* `{db_item.get('taken', False)}`\n"
        )
        if db_item.get("taken"):
            msg += f"*Mentor:* @{db_item.get('mentor')}\n"
        return msg + f"*Message*:\n```\n{db_item.get('message')}\n```"

    @admin_only
    def get_user_messages_command(self, message_text: str):
        if self.callback_query is not None:
            if message_text == "Cancel":
                self.hold_next(0)  # don't hold anymore
                return self.edit_message(
                    self.callback_query.message.message_id,
                    "You cancelled user messages listing",
                    None,
                )
            elif message_text.startswith("/get_user_messages"):
                alias, action, offset = message_text[
                    len("/get_user_messages ") :
                ].split(":")
                offset = int(offset)
                if action == ">":
                    new_offset = offset + self.pagination_step
                else:
                    new_offset = offset - self.pagination_step
                messages, count = DataBase().get_requests_by_alias(
                    alias, offset=new_offset
                )
                res = (
                    "\n\n".join([self.build_request_body(msg) for msg in messages])
                    or "None"
                )
                return self.edit_message(
                    self.callback_query.message.message_id,
                    res,
                    self.__keyboard.get_user_messages_paginated(
                        alias,
                        new_offset,
                        l_available=new_offset > 0,
                        r_available=count > new_offset,
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
        else:
            if message_text == "/get_user_messages":
                self.hold_next(1)
                return self.send_message(
                    "Send the alias of user you want to get messages from",
                    reply_markup=None,
                )
            else:
                messages, count = DataBase().get_requests_by_alias(self.message.text)
                if messages:
                    res = "\n\n".join(
                        [self.build_request_body(msg) for msg in messages]
                    )
                    return self.send_message(
                        res,
                        reply_markup=self.__keyboard.get_user_messages_paginated(
                            self.message.text,
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
    def check_new_requests_command(self, message_text: str):
        res = []
        if message_text == "/check_new_requests":
            messages = DataBase().get_new_requests()
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

    def new_request_action_command(self, message_text: str):
        if message_text.startswith(self.__category_prefix):
            request_id, command = message_text[len(self.__category_prefix) :].split(":")
            user_id = self.session.user.id
            alias = self.session.user.username
            if command == "Take":
                DataBase().update_request(
                    request_id=request_id, taken=True, mentor=alias, mentor_id=user_id
                )
                return self.edit_message(
                    self.callback_query.message.message_id, "Taken", None
                )
            elif command == "Respond":
                request = DataBase().find_by_id(request_id)
                alias = request.get("alias")
                user_id = request.get("user_id")
                self.hold_next(1)
                self.session["request_user_id"] = user_id
                self.session["request_respond_id"] = request_id
                self.session[
                    "new_request_message_id"
                ] = self.callback_query.message.message_id
                return self.send_message(f"Enter text to respond to @{alias}", None)
            elif command == "Close":
                DataBase().update_request(request_id=request_id, closed=True)
                return self.edit_message(
                    self.callback_query.message.message_id, "Closed", None
                )
        elif self.holding_left == 0 and self.session["new_request_message_id"] and self.session["request_respond_id"]:
            request_id = self.session["request_respond_id"]
            user_id = self.session["request_user_id"]
            return self.compound_result(
                (
                    self.edit_message(
                        self.session["new_request_message_id"],
                        "Your response was successfully sent",
                        None,
                    ),
                    self.send_message(
                        chat_id=user_id,
                        text=f"*Your request was reviewed.*\nAnswer:\n```\n{message_text}\n```",
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
