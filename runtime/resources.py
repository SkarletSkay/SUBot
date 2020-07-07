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
    def parse_strings(self, configuration: str) -> typing.List[IResourceEntry]:
        pass

    @abc.abstractmethod
    def parse_models(self, configuration: str) -> typing.List[IResourceEntry]:
        pass


class Resources(IResourceProvider):

    def __init__(self, parser: IResourceParser):
        self.__parser = parser
        self.__configuration = None
        self.__strings = None
        self.__string_arrays = None
        self.__models = None
        self.__strings_parsed = False
        self.__models_parsed = False

    @property
    def __models_resources(self) -> typing.List[IResourceEntry]:
        if not self.__models_parsed:
            self.__load_models()
        return self.__models

    @__models_resources.setter
    def __models_resources(self, value: typing.List[IResourceEntry]):
        self.__models = value
        if value is None:
            self.__models_parsed = False
        else:
            self.__models_parsed = True

    @property
    def __strings_resources(self) -> typing.List[IResourceEntry]:
        if not self.__strings_parsed or self.__strings is None:
            self.__load_strings()
        return self.__strings

    @__strings_resources.setter
    def __strings_resources(self, value: typing.List[IResourceEntry]):
        self.__strings = value
        if value is not None:
            self.__strings_parsed = True
        else:
            self.__strings_parsed = False

    @property
    def __strings_array_resources(self) -> typing.List[IResourceEntry]:
        if not self.__strings_parsed or self.__string_arrays is None:
            self.__load_strings()
        return self.__string_arrays

    @__strings_array_resources.setter
    def __strings_array_resources(self, value: typing.List[IResourceEntry]):
        self.__string_arrays = value
        if value is None:
            self.__strings_parsed = False
        else:
            self.__strings_parsed = True

    @property
    def configuration(self) -> str:
        return self.__configuration

    @configuration.setter
    def configuration(self, value: str):
        if self.__configuration == value:
            return
        self.__strings_parsed = False
        self.__models_parsed = False
        self.__configuration = value

    def get_string(self, resource_id: str) -> typing.Optional[str]:
        resource: IResourceEntry
        for resource in self.__strings_resources:
            if resource.name == resource_id:
                return resource.data

        raise RuntimeError(f"Resource with given name {resource_id} not found")

    def get_string_array(self, resource_id: str) -> typing.Optional[typing.Tuple[str]]:
        resource: IResourceEntry
        for resource in self.__strings_array_resources:
            if resource.name == resource_id:
                return resource.data

        raise RuntimeError(f"Resource with given name {resource_id} not found")

    def get_model(self, resource_id: str) -> typing.Optional[CommandModelDefinition]:
        resource: IResourceEntry
        for resource in self.__models_resources:
            if resource.name == resource_id:
                return resource.data
        raise RuntimeError(f"Resource with given name {resource_id} not found")

    def __load_strings(self):
        resources = self.__parser.parse_strings(self.__configuration)
        strings = list()
        string_arrays = list()
        for resource in resources:
            if isinstance(resource, StringResourceEntry):
                strings.append(resource)
            elif isinstance(resource, StringArrayResourceEntry):
                string_arrays.append(resource)
        self.__strings_resources = strings
        self.__strings_array_resources = string_arrays

    def __load_models(self):
        resources = self.__parser.parse_models(self.__configuration)
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

    def parse_models(self, configuration: str) -> typing.List[IResourceEntry]:

        file = self.__get_file_by_configuration('models', configuration)
        if file is None:
            file = self.__get_file_by_configuration('models')
        if file is None:
            raise FileNotFoundError("models.xml")

        file_content = file.read()
        file.close()

        models = list()
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
            models.append(resource)
        return models

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
    def __get_file_by_configuration(resource_type: str, configuration: str = "default") -> typing.Optional[typing.IO]:
        # scanning the /resources/ directory
        directory = os.scandir("resources")
        entry: os.DirEntry
        for entry in directory:
            if entry.is_file():
                file_name: str = entry.name
                # and searching the file that starts with 'type'
                if not file_name.startswith(resource_type):
                    continue

                # check the configuration. For default 'type'.xml and 'type'-en.xml are appropriate so, en is default
                if configuration == "default":
                    if file_name == resource_type + ".xml" or file_name == resource_type + "-en.xml":
                        return open("resources/" + file_name, "r", encoding='utf-8')

                # otherwise searching the file of "'type'-{conf}.xml", e.g. strings-ru.xml
                if file_name.find("-" + configuration) != -1:
                    return open("resources/" + file_name, "r", encoding='utf-8')

        return None

    def parse_strings(self, configuration: str) -> typing.List[IResourceEntry]:

        file = self.__get_file_by_configuration('strings', configuration)
        if file is None:
            file = self.__get_file_by_configuration('strings')
        if file is None:
            raise FileNotFoundError("strings.xml")

        file_content = file.read()
        file.close()

        # write the contents in dictionary { name:value }
        resources: typing.List[IResourceEntry] = list()

        xml_tree = ElementTree.fromstring(file_content)
        string_entry: Element
        for string_entry in xml_tree:
            if "name" not in string_entry.attrib:       # looking at the 'name' attribute
                raise RuntimeError("Every child in resources should have 'name' attribute")
            if string_entry.tag == "string":            # if we deal with <string ...>...</string> single string entry
                resource = StringResourceEntry()
                resource.name = string_entry.attrib["name"]
                resource.data = string_entry.text
                resources.append(resource)
            if string_entry.tag == "string-array":      # if we deal with <string-array ...>...</string-array> array entry
                resource = StringArrayResourceEntry()
                resource.name = string_entry.attrib["name"]
                array_entry: Element
                for array_entry in string_entry:
                    if array_entry.tag != "item":       # so, item should have <item>some_text</item> pattern
                        continue
                    resource.data.append(array_entry.text)
                resources.append(resource)
        return resources
