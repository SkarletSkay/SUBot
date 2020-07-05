import datetime
from typing import Dict, List


class Database:
    def get_requests(self, user_id: int = None, category: str = None, status: str = None) -> List[Dict]:
        # list should be filtered according to parameters, e.g
        # get_requests(category="Some category", status="taken")
        return [{
            "user_id": 829109329,
            "category": "category",
            "date": 3872098498,  # unix-time?
            "status": "status",  # or another data type to switch between values (taken, waits for reply, e.g.)
            "text": "text"
        }]

    def save_new_request(self, user_id: int, date: datetime, category: str, text: str, notifications: bool) -> bool:
        success = True
        return success
