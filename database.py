from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING


class DataBase:
    client = MongoClient(host=["localhost:27017"])

    def insert_new_request(self, user_id, alias, message, category):
        db = self.client.test
        db.chats.insert_one(
            {
                "user_id": user_id,
                "alias": alias,
                "message": message,
                "category": category,
                "timestamp": datetime.now(),
                "taken": False,
                "closed": False,
                "mentor": None,
                "mentor_id": None,
                "taken_timestamp": None,
            }
        )

    def update_request(self, request_id, taken=None, closed=None, mentor=None, mentor_id=None):
        update_body = {"$set": {}}
        if taken:
            update_body["$set"]["taken"] = bool(taken)
        if closed:
            update_body["$set"]["closed"] = bool(closed)
        if mentor:
            update_body["$set"]["mentor"] = str(mentor)
        if mentor_id:
            update_body["$set"]["mentor_id"] = mentor_id
        db = self.client.test
        db.chats.update_one({"_id": ObjectId(request_id)}, update_body, upsert=True)

    def get_requests_by_alias(self, alias, limit=10, offset=0):
        db = self.client.test
        user_msgs = db.chats.find({"alias": alias}).sort([("timestamp", DESCENDING)])
        return list(user_msgs.skip(offset).limit(limit)), user_msgs.count()

    def insert_one_db(self, dictionary):
        dictionary["notify"] = False
        dictionary["taken"] = False
        db = self.client.test
        db.chats.insert_one(dictionary)

    def read_db(self, amount=10):
        db = self.client.test
        collection = db.chats
        result = []
        for page in collection.find():
            result.append(page)

        if len(result) <= amount:
            return result
        else:
            return result[-amount:]

    def find_by_id(self, _id):
        db = self.client.test
        return list(db.chats.find({"_id": ObjectId(_id)}))[0]

    def get_new_requests(self):
        db = self.client.test
        return list(db.chats.find({"taken": False, "closed": False}).sort([("timestamp", ASCENDING)]))

    def get_taken_requests(self):
        db = self.client.test
        return list(db.chats.find({"taken": True, "closed": False}).sort([("timestamp", ASCENDING)]))

    def get_closed_requests(self):
        db = self.client.test
        return list(db.chats.find({"closed": True}).sort([("timestamp", ASCENDING)]))
