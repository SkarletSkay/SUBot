from typing import Dict, Tuple, Any, List
from runtime.session import SessionControl
import inspect


class ServiceStorage:

    def __init__(self):
        self.__singleton_storage: Dict[type, object] = dict()
        self.__scoped_storage: Dict[Tuple[int, type], object] = dict()
        self.__transient_storage: Dict[type, object] = dict()
        self.__singleton_list: List[type] = list()
        self.__scoped_list: List[type] = list()
        self.__transient_list: List[type] = list()

    def add_sessions(self):
        self.add_singleton(SessionControl)

    def add_transient(self, obj: type):
        if obj not in self.__scoped_list and obj not in self.__singleton_list and obj not in self.__transient_list:
            self.__transient_list.append(obj)

    def add_scoped(self, obj: type):
        if obj not in self.__scoped_list and obj not in self.__singleton_list and obj not in self.__transient_list:
            self.__scoped_list.append(obj)

    def add_singleton(self, obj: type):
        if obj not in self.__scoped_list and obj not in self.__singleton_list and obj not in self.__transient_list:
            self.__singleton_list.append(obj)

    def __get_singleton(self, key: type):
        if key not in self.__singleton_storage:
            return None
        return self.__singleton_storage[key]

    def __set_singleton(self, key: type, value: Any):
        self.__singleton_storage[key] = value

    def __get_scoped(self, key: type, session_id: int):
        if (session_id, key) not in self.__scoped_storage:
            return None
        return self.__scoped_storage[(session_id, key)]

    def __set_scoped(self, key: type, session_id: int, value: Any):
        self.__scoped_storage[(session_id, key)] = value

    def get_instance(self, obj_type: type, session_id: int):
        return self.__get_instance(obj_type, session_id, list())

    def __get_instance(self, obj_type: type, session_id: int, created_instances: List[type]):

        if obj_type not in self.__transient_list and obj_type not in self.__scoped_list and obj_type not in self.__singleton_list:
            raise RuntimeError("Cannot find dependency object {0}. You might want to register the object in configure_services method".format(obj_type))

        if obj_type in created_instances:
            raise RuntimeError("Recursive injection of object {0} is not allowed".format(obj_type))

        created_instances.append(obj_type)
        init_signature = inspect.signature(obj_type.__init__)
        param_dict = dict()
        for param_name, param_data in init_signature.parameters.items():
            param_type = param_data.annotation
            if param_type not in self.__singleton_list and param_type not in self.__transient_list and param_type not in self.__scoped_list:
                continue

            param_dict[param_name] = self.__get_instance(param_type, session_id, created_instances)

        if obj_type in self.__transient_list:
            return obj_type(**param_dict)

        if obj_type in self.__singleton_list:
            found_singleton = self.__get_singleton(obj_type)
            if found_singleton is None:
                object_inst = obj_type(**param_dict)
                self.__set_singleton(obj_type, object_inst)
                return object_inst
            return found_singleton

        found_scoped = self.__get_scoped(obj_type, session_id)
        if found_scoped is None:
            object_inst = obj_type(**param_dict)
            self.__set_scoped(obj_type, session_id, object_inst)
            return object_inst
        return found_scoped


services: ServiceStorage = ServiceStorage()
