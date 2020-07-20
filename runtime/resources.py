import abc
import importlib
import inspect
import os
import typing
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from runtime.command_model import CommandModelDefinition, PropertyDefinition


class IResourceProvider(abc.ABC):

    @abc.abstractmethod
    def get_string(self, resource_id: str) -> typing.Optional[str]:
        pass

    @abc.abstractmethod
    def get_string_array(self, resource_id: str) -> typing.Optional[typing.Tuple[str]]:
        pass

    @abc.abstractmethod
    def get_model(self, resource_id: str) -> typing.Optional[CommandModelDefinition]:
        pass

    @property
    @abc.abstractmethod
    def configuration(self) -> str:
        pass

    @configuration.setter
    @abc.abstractmethod
    def configuration(self, value: str):
        pass


class IResourceEntry(abc.ABC):

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def data(self):
        pass


class IResourceParser(abc.ABC):

    @abc.abstractmethod
    def parse_strings(self) -> typing.Dict[str, typing.List[IResourceEntry]]:
        pass

    @abc.abstractmethod
    def parse_models(self) -> typing.Dict[str, typing.List[IResourceEntry]]:
        pass


class Resources(IResourceProvider):

    def __init__(self, parser: IResourceParser):
        self.__parser = parser
        self.__configuration = None
        self.__strings = None
        self.__models = None

    @property
    def __models_resources(self) -> typing.Dict[str, typing.List[IResourceEntry]]:
        if self.__models is None:
            self.__load_models()
        return self.__models

    @__models_resources.setter
    def __models_resources(self, value: typing.Dict[str, typing.List[IResourceEntry]]):
        self.__models = value

    @property
    def __strings_resources(self) -> typing.Dict[str, typing.List[IResourceEntry]]:
        if self.__strings is None:
            self.__load_strings()
        return self.__strings

    @__strings_resources.setter
    def __strings_resources(self, value: typing.Dict[str, typing.List[IResourceEntry]]):
        self.__strings = value

    @property
    def configuration(self) -> str:
        return self.__configuration

    @configuration.setter
    def configuration(self, value: str):
        if self.__configuration == value:
            return
        self.__configuration = value

    def get_string(self, resource_id: str) -> typing.Optional[str]:
        resource: IResourceEntry
        for conf, resources in self.__strings_resources.items():
            if '-' + self.configuration in conf:
                for res in resources:
                    if res.name == resource_id and isinstance(res, StringResourceEntry):
                        return res.data
        if "" in self.__strings_resources:
            for res in self.__strings_resources[""]:
                if res.name == resource_id and isinstance(res, StringResourceEntry):
                    return res.data

        raise RuntimeError(f"String array with given name {resource_id} not found")

    def get_string_array(self, resource_id: str) -> typing.Optional[typing.Tuple[str]]:
        resource: IResourceEntry
        for conf, resources in self.__strings_resources.items():
            if '-' + self.configuration in conf:
                for res in resources:
                    if res.name == resource_id and isinstance(res, StringArrayResourceEntry):
                        return tuple(res.data)
        if "" in self.__strings_resources:
            for res in self.__strings_resources[""]:
                if res.name == resource_id and isinstance(res, StringArrayResourceEntry):
                    return tuple(res.data)

        raise RuntimeError(f"String array with given name {resource_id} not found")

    def get_model(self, resource_id: str) -> typing.Optional[CommandModelDefinition]:
        resource: IResourceEntry
        for conf, resources in self.__models_resources.items():
            if '-' + self.configuration in conf:
                for res in resources:
                    if res.name == resource_id:
                        return res.data

        if "" in self.__models_resources:
            for res in self.__models_resources[""]:
                if res.name == resource_id:
                    return res.data

        raise RuntimeError(f"Model with given name {resource_id} not found")

    def __load_strings(self):
        resources = self.__parser.parse_strings()
        self.__strings_resources = resources

    def __load_models(self):
        resources = self.__parser.parse_models()
        self.__models_resources = resources


class StringResourceEntry(IResourceEntry):

    def __init__(self):
        self.__name = None
        self.__text = None

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def data(self) -> str:
        return self.__text

    @data.setter
    def data(self, value: str):
        self.__text = value


class StringArrayResourceEntry(IResourceEntry):

    def __init__(self):
        self.__name = None
        self.__array = list()

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def data(self) -> typing.List[str]:
        return self.__array

    @data.setter
    def data(self, value: typing.List[str]):
        self.__array = value


class ModelResourceEntry(IResourceEntry):

    def __init__(self):
        self.__name = None
        self.__model = None

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def data(self) -> CommandModelDefinition:
        return self.__model

    @data.setter
    def data(self, value: CommandModelDefinition):
        self.__model = value


class XmlResourceParser(IResourceParser):

    def __parse_model_property(self, entry: Element) -> PropertyDefinition:
        property_definition = PropertyDefinition()
        if 'name' not in entry.attrib:
            raise RuntimeError("Property entry should contain 'name' attribute")
        property_definition.name = entry.attrib['name']
        property_definition.type = 'str'
        if 'type' in entry.attrib:
            property_definition.type = entry.attrib['type']
        if 'hint' in entry.attrib:
            property_definition.hint = entry.attrib['hint']
        if 'optional' in entry.attrib:
            property_definition.optional = self.__parse_bool(entry.attrib['optional'])
        if 'text' in entry.attrib:
            property_definition.text = entry.attrib['text']
        return property_definition

    def parse_models(self) -> typing.Dict[str, typing.List[IResourceEntry]]:

        files = self.__get_files_by_type('models')
        if len(files) == 0:
            raise FileNotFoundError("models.xml")

        resources = dict()

        for file_name in files:
            file = open(file_name, "r", encoding="utf-8")
            file_content = file.read()
            file.close()
            configuration = file_name.replace("resources/models", "").replace(".xml", "")

            if configuration not in resources:
                resources[configuration] = list()

            xml_tree = ElementTree.fromstring(file_content)
            model_entry: Element
            for model_entry in xml_tree:
                if "name" not in model_entry.attrib:
                    raise RuntimeError("Every child in resources should have 'name' attribute")
                resource = ModelResourceEntry()
                resource.name = model_entry.attrib["name"]
                if "entry_command" not in model_entry.attrib:
                    raise RuntimeError("Entry command should be specified for every command model")
                model_definition = CommandModelDefinition()
                model_definition.entry_command = model_entry.attrib["entry_command"]
                if "confirm_cancel" in model_entry.attrib:
                    model_definition.confirm_cancel = self.__parse_bool(model_entry.attrib["confirm_cancel"])
                if "class" in model_entry.attrib:
                    model_definition.command_class = self.__parse_class(model_entry.attrib["class"])
                if "handler" in model_entry.attrib:
                    model_definition.handler_class = self.__parse_class(model_entry.attrib["handler"])
                if "confirm_send" in model_entry.attrib:
                    model_definition.confirm_send = self.__parse_bool(model_entry.attrib["confirm_send"])
                model_definition.fill_mode = "auto"
                if "fill_mode" in model_entry.attrib:
                    mode = model_entry.attrib["fill_mode"].lower()
                    if mode == "manual":
                        model_definition.fill_mode = "manual"
                    elif mode == "auto":
                        model_definition.fill_mode = "auto"
                    else:
                        raise RuntimeError(f"Invalid value for 'fill_mode' attribute. Expected auto/manual, got {mode.lower()}")
                property_entry: Element
                for property_entry in model_entry:
                    property_definition = self.__parse_model_property(property_entry)
                    if property_definition.optional:
                        model_definition.optional_options.append(property_definition)
                    else:
                        model_definition.required_properties.append(property_definition)

                resource.data = model_definition
                resources[configuration].append(resource)
        return resources

    @staticmethod
    def __parse_class(value: str) -> typing.Type:
        last_dot = value.rfind('.')
        if last_dot == -1:
            raise RuntimeError(f"Cannot find class {value}")

        module_name = value[0:last_dot]
        class_name = value[last_dot + 1:]
        module = importlib.import_module(module_name)
        target_type = getattr(module, class_name)
        if inspect.isclass(target_type):
            return target_type
        else:
            raise RuntimeError(f"Cannot find class {value}")

    @staticmethod
    def __parse_bool(value: str) -> bool:
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        raise RuntimeError(f"Invalid value for 'optional' attribute. Expected true/false, got {value.lower()}")

    @staticmethod
    def __get_files_by_type(resource_type: str) -> typing.List[str]:
        # scanning the /resources/ directory
        directory = os.scandir("resources")
        files = list()
        entry: os.DirEntry
        for entry in directory:
            if entry.is_file():
                file_name: str = entry.name
                # and searching the file that starts with 'type'
                if not file_name.startswith(resource_type) or not file_name.endswith(".xml"):
                    continue
                files.append("resources/" + file_name)
        return files

    def parse_strings(self) -> typing.Dict[str, typing.List[IResourceEntry]]:

        files = self.__get_files_by_type('strings')
        if len(files) == 0:
            raise FileNotFoundError("strings.xml")

        resources = dict()

        for file_name in files:
            file = open(file_name, "r", encoding="utf-8")
            file_content = file.read()
            file.close()
            configuration = file_name.replace("resources/strings", "").replace(".xml", "")

            if configuration not in resources:
                resources[configuration] = list()

            # write the contents in dictionary { name:value }
            xml_tree = ElementTree.fromstring(file_content)
            string_entry: Element
            for string_entry in xml_tree:
                if "name" not in string_entry.attrib:       # looking at the 'name' attribute
                    raise RuntimeError("Every child in resources should have 'name' attribute")
                if string_entry.tag == "string":            # if we deal with <string ...>...</string> single string entry
                    resource = StringResourceEntry()
                    resource.name = string_entry.attrib["name"]
                    resource.data = string_entry.text
                    resources[configuration].append(resource)
                if string_entry.tag == "string-array":      # if we deal with <string-array ...>...</string-array> array entry
                    resource = StringArrayResourceEntry()
                    resource.name = string_entry.attrib["name"]
                    array_entry: Element
                    for array_entry in string_entry:
                        if array_entry.tag != "item":       # so, item should have <item>some_text</item> pattern
                            continue
                        resource.data.append(array_entry.text)
                    resources[configuration].append(resource)
        return resources
