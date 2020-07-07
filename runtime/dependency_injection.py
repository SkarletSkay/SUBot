import uuid
import abc
import enum
import inspect
import typing


class IServiceEngine(abc.ABC):

    @abc.abstractmethod
    def get_or_create_instance(self, obj_type: typing.Type, session_id: int) -> object:
        pass


class IServiceProvider(abc.ABC):

    @abc.abstractmethod
    def get_instance(self, obj_type: typing.Type, session_id: int = None):
        pass


class LifeSpan(enum.Enum):
    SINGLETON = 1
    SCOPED = 2
    TRANSIENT = 3


class ServiceDefinition:

    def __init__(self):
        self.__source_type: type = object
        self.__implementation_type: typing.Optional[type] = object
        self.__lifespan: LifeSpan = LifeSpan.TRANSIENT
        self.__uuid = uuid.uuid4()

    @property
    def source_type(self) -> type:
        return self.__source_type

    @source_type.setter
    def source_type(self, value: type):
        self.__source_type = value

    @property
    def implementation_type(self) -> typing.Optional[type]:
        return self.__implementation_type

    @implementation_type.setter
    def implementation_type(self, value: typing.Optional[type]):
        self.__implementation_type = value

    @property
    def lifespan(self) -> LifeSpan:
        return self.__lifespan

    @lifespan.setter
    def lifespan(self, value: LifeSpan):
        self.__lifespan = value

    @property
    def uuid(self) -> uuid.UUID:
        return self.__uuid


class ServiceCollection:
    __t = typing.TypeVar("__t")

    def __init__(self):
        self.__services: typing.List[ServiceDefinition] = list()

    def add_singleton(self, obj_type: typing.Type[__t], imp_type: typing.Optional[typing.Type[__t]] = None):
        self.__add_service(obj_type, imp_type, LifeSpan.SINGLETON)

    def add_scoped(self, obj_type: typing.Type[__t], imp_type: typing.Optional[typing.Type[__t]] = None):
        self.__add_service(obj_type, imp_type, LifeSpan.SCOPED)

    def add_transient(self, obj_type: typing.Type[__t], imp_type: typing.Optional[typing.Type[__t]] = None):
        self.__add_service(obj_type, imp_type, LifeSpan.TRANSIENT)

    def __add_service(self, obj_type: typing.Type[__t], imp_type: typing.Optional[typing.Type[__t]],
                      lifespan: LifeSpan):
        if self.registered(obj_type):
            return

        service = ServiceDefinition()
        service.source_type = obj_type
        service.implementation_type = imp_type
        service.lifespan = lifespan
        self.__services.append(service)

    def remove(self, base_type: typing.Type[__t]):
        for service in self.__services:
            if service.source_type == base_type:
                self.__services.remove(service)
                break

    def registered(self, base_type: typing.Type[__t]) -> bool:
        for service in self.__services:
            if service.source_type == base_type:
                return True
        return False

    def get_service(self, base_type) -> typing.Optional[ServiceDefinition]:
        for service in self.__services:
            if service.source_type == base_type:
                return service
        return None

    @property
    def services(self) -> typing.Tuple[ServiceDefinition, ...]:
        return tuple(self.__services)

    def add_commands(self, options):
        commands_modules = options()["__modules__"]

        for module in commands_modules:
            all_classes = inspect.getmembers(module, inspect.isclass)
            for class_name, val in all_classes:
                if class_name.endswith("Commands"):
                    self.add_scoped(val)


class ServiceEngine(IServiceEngine):

    def __init__(self, services: typing.Tuple[ServiceDefinition]):
        self.__services = services
        self.__realized: typing.Dict[typing.Tuple[typing.Type, typing.Optional[int]], object] = dict()

    def get_or_create_instance(self, obj_type: typing.Type, session_id: typing.Optional[int] = None) -> object:
        return self.__get_or_create_instance(obj_type, session_id, list())

    def __get_or_create_instance(self, obj_type: typing.Type, session_id: typing.Optional[int] = None,
                                 created: typing.List[typing.Type] = None):
        definition: typing.Optional[ServiceDefinition] = None
        for service in self.__services:
            if service.implementation_type == obj_type or service.source_type == obj_type:
                definition = service
                break
        if definition is None:
            return None

        target_type: typing.Type = definition.source_type
        if definition.implementation_type is not None:
            target_type = definition.implementation_type
        if target_type in created:
            raise RuntimeError(f"Recursive injection of type {target_type} is not allowed")

        if definition.lifespan == LifeSpan.SINGLETON and (definition.uuid, 0) in self.__realized:
            return self.__realized[(target_type, 0)]

        if definition.lifespan == LifeSpan.SCOPED and (definition.uuid, session_id) in self.__realized:
            return self.__realized[(target_type, session_id)]

        created.append(target_type)
        ctor_signature = inspect.signature(target_type.__init__)
        param_dict = dict()
        for param_name, param_data in ctor_signature.parameters.items():
            if param_name == 'self' or param_data.kind == inspect.Parameter.VAR_POSITIONAL or param_data.kind == inspect.Parameter.VAR_KEYWORD:
                continue
            param_type = param_data.annotation
            param_instance = self.__get_or_create_instance(param_type, session_id, created)

            param_dict[param_name] = param_instance
        obj_instance = target_type(**param_dict)

        if definition.lifespan == LifeSpan.SCOPED:
            self.__realized[(target_type, session_id)] = obj_instance
        elif definition.lifespan == LifeSpan.SINGLETON:
            self.__realized[(target_type, 0)] = obj_instance
        return obj_instance


class ServiceProvider(IServiceProvider):

    def get_instance(self, obj_type: typing.Type, session_id: int = None) -> typing.Optional[object]:
        if self.__engine is None:
            return None
        return self.__engine.get_or_create_instance(obj_type, session_id)

    def __init__(self):
        self.__engine: typing.Optional[IServiceEngine] = None

    def populate(self, services: typing.Tuple[ServiceDefinition]):
        self.__engine = ServiceEngine(services)
