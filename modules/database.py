import datetime


class Database:
    def get_request(self, user_id: int) -> dict:
        return {
            "user_id": 829109329,
            "category": "category",
            "date": 3872098498,  # unix-time?
            "status": "status",  # or another data type to switch between values (taken, waits for reply, e.g.)
            "text": "text"
        }

    def save_new_request(self, user_id: int, date: datetime, category: str, text: str) -> bool:
        return True
