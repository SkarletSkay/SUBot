import typing

from modules.database import DataBase
from resources.designer import Resources
from runtime.commands import ModelCommandBase, CommandResult


class UserRequest:

    def __init__(self):
        self.category = ""
        self.request_text = ""
        self.notifications = False


class Handler(ModelCommandBase):
    def __init__(self, database: DataBase):
        super().__init__()
        self.database = database

    def on_complete(self, model: UserRequest) -> typing.Union[CommandResult, str]:
        save_success = self.database.insert_new_request(user_id=self.user.id,
                                                        alias=self.user.username,
                                                        category=model.category,
                                                        text=model.request_text,
                                                        notify=model.notifications or False)
        return self.send_message(resource=Resources.Strings.REQUEST_SAVE_SUCCESS if save_success else Resources.Strings.REQUEST_SAVE_SUCCESS)

    def create_review(self, model) -> str:
        result = self.resources.get_string(Resources.Strings.REVIEW_TITLE) + "\n\n"
        for entry in self.session.keys:
            if entry.startswith("__property_"):
                prop_name = entry.replace("__property_", "")
                value = self.session[entry]
                if value is not None:
                    result += self.resources.get_string(prop_name) + ":\n"
                    if isinstance(value, bool):
                        result += self.resources.get_string(Resources.Strings.YES if value else Resources.Strings.NO) + "\n\n"
                    else:
                        result += str(value) + "\n\n"
        return result

    def on_cancel(self, model) -> CommandResult:
        return self.send_message(resource=Resources.Strings.REQUEST_CANCEL)
