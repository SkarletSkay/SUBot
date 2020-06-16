from datetime import datetime
from runtime.context import Context
from typing import Dict, Tuple, Optional


class DefaultContextStorage:

    def __init__(self):
        self.__contextDict: Dict[Tuple[int, int], Tuple[Context, datetime]] = dict()

    def store_context(self, user_id: int, chat_id: int, context: Context):
        self.__contextDict[(user_id, chat_id)] = (context, datetime.now())

    def restore_context(self, user_id: int, chat_id: int) -> Optional[Context]:
        if (user_id, chat_id) not in self.__contextDict:
            return None
        return self.__contextDict[(user_id, chat_id)][0]
