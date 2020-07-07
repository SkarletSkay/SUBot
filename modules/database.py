from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, List


class DataBase:
    def __init__(self):
        self.client = MongoClient(
            "mongodb+srv://admin-user:"
            "awefwryheegryf434352gerw@telegram-bot-logs.spdt5.mongodb.net/test?retryWrites=true&w=majority")

    def insert_one_request(self, **kwargs) -> Dict:
        """
        Save a request into the DB.
        :param kwargs: a dict of named params, including:
            text: str - The text of the request
            category: str - The category of the request
            notify: bool - Whether the user should be notified on updates
            taken: bool - Whether the request is taken by SU members
            user_id: int - The id of the sender
            date: datetime - Time of the request creation
        :return: InsertOneResult object
        """
        db = self.client.test
        result = db.requests.insert_one(kwargs)
        return result

    def get_requests(self, **constraints) -> List[Dict]:
        """
        Query requests from the DB according to the specified constraints
        :param constraints: a dict of named params, including:
            db_id: str - The id of the request in the DB
            category: str - The category of the request
            notify: bool - Whether the user should be notified on updates
            taken: bool - Whether the request is taken by SU members
            user_id: int - The id of the sender
            date: datetime - Time of the request creation
        :return: InsertOneResult object
        """
        db = self.client.test
        collection = db.requests
        result = []
        for page in collection.find(constraints):
            print("MongoDB record:", page)
            result.append(page)

        return result

    def set_request_taken(self, db_id: str, value: bool = True):
        db_id = ObjectId(db_id)
        db = self.client.test
        collection = db.requests

        query = {"_id": db_id}
        new_values = {"$set": {"taken": value}}
        collection.update_one(query, new_values)

        result = {}
        for page in collection.find({"_id": db_id}):
            result = page
        return result

    def set_notify(self, db_id: str, value: bool = True):
        db_id = ObjectId(db_id)
        db = self.client.test
        collection = db.requests

        query = {"_id": db_id}
        new_values = {"$set": {"notify": value}}
        collection.update_one(query, new_values)

        result = {}
        for page in collection.find({"_id": db_id}):
            result = page
        return result
