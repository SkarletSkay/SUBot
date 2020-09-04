from pymongo import MongoClient
from bson import ObjectId
import datetime
from typing import Dict, List


class DataBase:

    client = MongoClient(
        "mongodb+srv://admin-user:" +
        "awefwryheegryf434352gerw@telegram-bot-logs.spdt5.mongodb.net/test?retryWrites=true&w=majority")

    def insert_one_request(self, **kwargs) -> Dict:
        insert_data = {}
        for key, value in kwargs.items():
            insert_data[f"{key}"] = value
        db = self.client.test
        db.requests.insert_one(insert_data)
        return insert_data

    def get_requests(self, user_id: int = None, category: str = None, taken: bool = None, notify: bool = None, db_id: str = None, date: datetime = None) -> List[Dict]:
        # list should be filtered according to parameters, e.g
        # get_requests(category="Some category", status="taken")

        db = self.client.test
        collection = db.requests
        result = []
        for page in collection.find():
            print(page)
            if not (user_id is None) and page["user_id"] != user_id:
                continue
            elif not (category is None) and page["category"] != category:
                continue
            elif not (taken is None) and page["taken"] != taken:
                continue
            elif not (notify is None) and page["notify"] != notify:
                continue
            elif not (db_id is None) and page["_id"] != db_id:
                continue
            else:
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
