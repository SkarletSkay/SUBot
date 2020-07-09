from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.cursor import Cursor
from pymongo.operations import UpdateOne
from telegram import Bot

from pymongo.results import InsertOneResult, UpdateResult, BulkWriteResult

from typing import List, Dict, Union, Tuple



class DataBase:
    def __init__(self):
        self.client = MongoClient(
            "mongodb+srv://admin-user:"
            "awefwryheegryf434352gerw@telegram-bot-logs.spdt5.mongodb.net/test?retryWrites=true&w=majority")
        self.db = self.client.test

        self.request_structure = {
            "text": str,                 # The text of the request
            "category": str,             # The category of the request
            "notify": bool,              # Whether the user should be notified on updates
            "taken": bool,               # Whether the request is taken by SU members
            "mentor_id": int,            # The ID of the mentor for this request
            "closed": bool,              # Whether the request is already closed
            "user_id": int,              # The ID of the sender
            "timestamp": datetime,       # Time of the request creation
            "taken_timestamp": datetime  # Time the request is taken at (mentor is assigned)
        }
        self.default_sorting = [("timestamp", ASCENDING)]

    def __check_types(self, request: dict) -> bool:
        """
        Check if given fields are filled with correct values.
        Request structure is described in the constructor.
        """
        for key, value in request.items():
            if value is not None and not isinstance(value, self.request_structure.get(key)):
                return False
        return True

    def __check_request(self, request: dict) -> bool:
        """
        Check if ALL the fields are filled with correct values.
        Request structure is described in the constructor.
        """
        keys_match = sorted(request.keys()) == sorted(self.request_structure.keys())
        return keys_match and self.__check_types(request)

    def insert_new_request(self, alias: str, **request_fields) -> Union[InsertOneResult, bool]:
        """
        Save a request into the DB.
        :param alias: user alias to save in case it is unknown yet
        :param request_fields: a dict of named params, including:
            text: str - The text of the request
            category: str - The category of the request
            notify: bool - Whether the user should be notified on updates
            user_id: int - The ID of the sender
        :return: InsertOneResult object or False
        """
        request_fields.update({
            "timestamp": datetime.now(),
            "taken": False,
            "closed": False,
            "mentor_id": None,
            "taken_timestamp": None
        })
        if self.__check_request(request_fields):
            if not self.known_user_id(request_fields["user_id"]):
                self.add_user_alias(request_fields["user_id"], alias)
            return self.db.requests.insert_one(request_fields)

        return False

    def _get_requests(self, sorting: List[Tuple[str, int]] = None, get_total_count: bool = False,
                      offset: int = 0, limit: int = 0, **constraints) -> Union[Tuple[List[Dict], int], List[Dict], bool]:
        """
        Query requests from the DB according to the specified constraints.
        Returns a tuple with total request count if limit is specified.
        :param sorting: list of tuples (sorting rules): (field_name: str, ASCENDING or DESCENDING)
        :param offset: amount of requests to skip
        :param limit: max amount of requests to be returned
        :param constraints: a dict of named request fields, may also include:
            _id: str or ObjectId - The id of the request in the DB
        :return: list of requests or False
        """
        req_id = constraints.pop("_id") if "_id" in constraints else None
        if self.__check_types(constraints) and (req_id is None or isinstance(req_id, (ObjectId, str))):
            if req_id is not None:
                constraints["_id"] = ObjectId(req_id)
            if sorting is None:
                sorting = self.default_sorting
            result: Cursor = self.db.requests.find(constraints, skip=offset, limit=limit, sort=sorting)
            if get_total_count:
                return list(result), self.db.requests.count_documents(constraints)
            return list(result)

        return False

    def _update_request(self, request_id: Union[str, ObjectId], **updates) -> UpdateResult:
        """
        Update the request in the DB
        :param request_id: request ID (str or ObjectId)
        :param updates: a dict of named params, may include:
            taken: bool - Whether the request is taken by SU members
            closed: bool - Whether the request is already closed
            mentor_id: int - The ID of the mentor for this request
            category: str - The category of the request
            taken_timestamp: datetime - Time the request is taken at (mentor is assigned)
        :return: UpdateResult object
        """
        allowed_updates = {"taken", "closed", "mentor_id", "category", "taken_timestamp"}

        # filter out only allowed updates (see above)
        update_body = {"$set": {key: updates[key] for key in allowed_updates if key in updates.keys()}}
        return self.db.requests.update_one({"_id": ObjectId(request_id)}, update_body, upsert=True)

    def get_request_by_id(self, request_id: str):
        result = self._get_requests(_id=request_id)
        if result is False:
            return False

        return result[0]

    def get_requests_by_user_id(self, user_id: int, limit: int = 10, offset: int = 0, get_total_count: bool = False):
        return self._get_requests(user_id=user_id, limit=limit, offset=offset, get_total_count=get_total_count)

    def take_request(self, request_id: str, mentor_id: int):
        return self._update_request(ObjectId(request_id), taken=True, taken_timestamp=datetime.now(), mentor_id=mentor_id)

    def close_request(self, request_id: str):
        return self._update_request(ObjectId(request_id), closed=True)

    def get_new_requests(self):
        return self._get_requests(taken=False, closed=False)

    def get_taken_requests(self):
        return self._get_requests(taken=True, closed=False)

    def get_closed_requests(self):
        return self._get_requests(closed=True)

    def get_requests_by_alias(self, alias: str, limit: int = 10, offset: int = 0):
        resolved_id = self.alias_to_user_id(alias)
        if resolved_id is False:
            return list(), 0
        return self.get_requests_by_user_id(resolved_id, limit, offset, get_total_count=True)

    def known_user_id(self, user_id: int) -> bool:
        users_found = self.db.users.count_documents({"id": user_id})
        return users_found > 0

    def add_user_alias(self, user_id: int, alias: str) -> Union[UpdateResult, InsertOneResult]:
        modification: InsertOneResult = self.db.users.insert_one({"id": user_id, "alias": alias})
        return modification

    def update_user_aliases(self, bot: Bot) -> BulkWriteResult:
        updates = []
        users: Cursor = self.db.users.find()
        for user in users:
            current_alias = bot.get_chat(user["id"]).username
            if user["alias"] != current_alias:
                updates.append(UpdateOne({"id": user["id"]}, {"$set": {"alias": current_alias}}))
        return self.db.users.bulk_write(updates)

    def alias_to_user_id(self, alias: str) -> int:
        # return the first match or False
        for user_record in self.db.users.find({"alias": alias}):
            return user_record["id"]
        return False

