from datetime import datetime

from runtime.commands import MessageResult
from runtime.context import Context
import os


class Logger:

    def __init__(self):
        self.__base_path = "logs/"
        if not os.path.exists(self.__base_path):
            os.mkdir(self.__base_path)
        self.__logfile = open(self.__base_path + "default log.txt", 'a', encoding='utf-8')

    def info(self, message: str):
        self.__logfile.write(str(datetime.now()) + " info: " + message + "\n")

    def warn(self, message: str):
        self.__logfile.write(str(datetime.now()) + " warning: " + message + "\n")

    def debug(self, message: str):
        self.__logfile.write(str(datetime.now()) + " debug: " + message + "\n")

    def error(self, message: str):
        self.__logfile.write(str(datetime.now()) + " error: " + message + "\n")
