import abc
import typing

from runtime.bot import BotRequest, BotResponse
from runtime.dependency_injection import IServiceProvider
from runtime.resources import IResourceProvider
from runtime.session import ISession
from runtime.user import User


class IContextProvider(abc.ABC):

    @property
    @abc.abstractmethod
    def configuration(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def session(self) -> ISession:
        pass

    @property
    @abc.abstractmethod
    def bot_request(self) -> BotRequest:
        pass

    @property
    @abc.abstractmethod
    def bot_response(self) -> BotResponse:
        pass

    @property
    @abc.abstractmethod
    def services(self) -> IServiceProvider:
        pass

    @property
    @abc.abstractmethod
    def user(self) -> User:
        pass


class Context(IContextProvider):

    @property
    def user(self) -> User:
        return self.__user

    @user.setter
    def user(self, value: User):
        self.__user = value

    @property
    def session(self) -> ISession:
        return self.__session

    @session.setter
    def session(self, value: ISession):
        self.__session = value

    @property
    def bot_request(self) -> BotRequest:
        return self.__bot_request

    @bot_request.setter
    def bot_request(self, value: BotRequest):
        self.__bot_request = value

    @property
    def bot_response(self) -> BotResponse:
        return self.__bot_response

    @bot_response.setter
    def bot_response(self, value: BotResponse):
        self.__bot_response = value

    @property
    def services(self) -> IServiceProvider:
        return self.__services

    @services.setter
    def services(self, value: IServiceProvider):
        self.__services = value

    @property
    def configuration(self) -> str:
        return self.__configuration

    @configuration.setter
    def configuration(self, value: str):
        self.__configuration = value

    @property
    def resources(self) -> typing.Optional[IResourceProvider]:
        return self.__resources

    @resources.setter
    def resources(self, value: typing.Optional[IResourceProvider]):
        self.__resources = value

    def __init__(self):
        self.__configuration: typing.Optional[str] = None
        self.__services: typing.Optional[IServiceProvider] = None
        self.__bot_request: typing.Optional[BotRequest] = None
        self.__bot_response: typing.Optional[BotResponse] = None
        self.__session: typing.Optional[ISession] = None
        self.__user: typing.Optional[User] = None
        self.__resources: typing.Optional[IResourceProvider] = None
