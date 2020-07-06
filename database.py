from pymongo import MongoClient


class DataBase:

    client = MongoClient(
        "mongodb+srv://admin-user:" +
        "awefwryheegryf434352gerw@telegram-bot-logs.spdt5.mongodb.net/test?retryWrites=true&w=majority")

    def insert_one_db(self, dictionary):
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


