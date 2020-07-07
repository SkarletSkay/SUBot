import typing
import pickle
import os
import abc


class ISessionStorage(abc.ABC):

    @abc.abstractmethod
    def commit(self, identifier: int, object_inst):
        pass

    @abc.abstractmethod
    def load(self, identifier: int):
        pass


class ISession(abc.ABC):

    @property
    @abc.abstractmethod
    def id(self):
        pass

    @id.setter
    @abc.abstractmethod
    def id(self, value: int):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def __getitem__(self, item: str):
        pass

    @abc.abstractmethod
    def __setitem__(self, key: str, value: typing.Union[str, int, bool]):
        pass

    @property
    @abc.abstractmethod
    def keys(self) -> typing.Tuple[str, ...]:
        pass

    @abc.abstractmethod
    def load(self):
        pass

    @abc.abstractmethod
    def commit(self):
        pass

    @abc.abstractmethod
    def remove(self, key: str):
        pass


class Session(ISession):

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, value: int):
        self.__id = value

    def clear(self):
        self.__data.clear()

    @property
    def keys(self) -> typing.Tuple[str, ...]:
        return tuple(self.__data.keys())

    def load(self):
        data = self.__storage.load(self.id)
        if data is not None:
            self.__data = data

    def commit(self):
        self.__storage.commit(self.id, self.__data)

    def remove(self, key: str):
        if key in self.__data:
            self.__data.pop(key)

    def __init__(self, storage: ISessionStorage):
        self.__id = 0
        self.__data: typing.Dict[str, typing.Union[str, int]] = dict()
        self.__storage: ISessionStorage = storage

    def __getitem__(self, item: str):
        if item not in self.__data:
            return None
        return self.__data[item]

    def __setitem__(self, key: str, value: typing.Union[str, int]):
        self.__data[key] = value


class FileSessionStorage(ISessionStorage):

    def __init__(self):
        self.__base_path = "sessions/"

    def commit(self, identifier: int, object_inst):
        path = self.__base_path + str(identifier) + ".session"
        if not os.path.exists(self.__base_path):
            os.mkdir(self.__base_path)

        object_bytes = pickle.dumps(object_inst)

        out_stream = open(path, "wb")
        out_stream.write(object_bytes)
        out_stream.flush()
        out_stream.close()

    def load(self, identifier: int):
        path = self.__base_path + str(identifier) + ".session"
        if not os.path.exists(path):
            return None

        in_stream = open(path, "rb")
        content = in_stream.read()
        in_stream.close()
        object_inst = pickle.loads(content)
        return object_inst
