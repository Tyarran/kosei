import collections
import enum
import functools
import itertools
import os

import colander
import colorama
import more_itertools
from dotenv import dotenv_values, find_dotenv
from tabulate import tabulate

__version__ = "0.1.0"


colorama.init()

BOLD = "\033[1m"


class Sources(enum.Enum):
    OVERRIDED = {"color": colorama.Fore.RED}
    ENVVAR = {"color": colorama.Fore.BLUE}
    FILE = {"color": colorama.Fore.WHITE}
    DOTENV = {"color": colorama.Fore.GREEN}


class Source(colander.SchemaType):

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        if appstruct.name not in list(Sources.__members__):
            raise colander.Invalid(node, f'{appstruct.name} is not in Sources enum')
        return appstruct.name

    def deserialize(self, node, cstruct):
        if isinstance(cstruct, Sources):
            return cstruct
        if not isinstance(cstruct, str):
            raise colander.Invalid(node, f'{cstruct} is not a str')
        try:
            result = Sources[cstruct]
        except KeyError:
            raise colander.Invalid(node, f'{cstruct} is not a valid enum value')
        return result


class ConfigVarSchema(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(), required=True)
    original = colander.SchemaNode(colander.String(), required=True)
    source = colander.SchemaNode(Source(), required=True)
    path = colander.SchemaNode(colander.String(), required=True, missing=None)


def dotenv_reader():
    source = Sources.DOTENV
    path = find_dotenv()
    if path:
        values = dotenv_values(path)
        return [
            {
                "name": name,
                "value": value,
                "original": str(value),
                "source": source,
                "path": path,
            }
            for name, value in values.items()
        ]


class BindedReader:
    source = Sources.OVERRIDED

    def __init__(self, data):
        self.data = data

    def __call__(self):
        return [
            {
                "name": name,
                "value": str(value),
                "original": str(value),
                "source": self.source,
            }
            for name, value in self.data.items()
        ]


class ConfigVar:
    name = None
    value = None
    original = None
    source = None
    typ = None
    path = None

    def __init__(self, name, value, typ, original, source, path):
        self.name = name
        self.value = value
        self.original = original
        self.source = source
        self.typ = typ
        self.path = path


def only_if_validated(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        if not self.validated:
            raise PermissionError("Settings are not validated")
        return func(self, *args, **kwargs)

    return wrapped


def only_if_binded(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        if not self.binded:
            raise PermissionError("No data binded")
        return func(self, *args, **kwargs)

    return wrapped


class Configuration:
    schema_nodes = []
    __validated = False
    data = {}
    _vars = {}
    _dotenv_data = {}
    _readers = None

    def __init__(self, readers=None):
        self._readers = readers or []

    @property
    def validated(self):
        return self.__validated

    @property
    def binded(self):
        return bool(self.data is not None)

    @only_if_validated
    def dict(self):
        return {var.name: var.value for var in self._vars.values()}


    @only_if_binded
    def validate(self):
        names = [node.name for node in self.schema_nodes]
        data = {
            values["name"]: values
            for data in self.data.values()
            for values in data
            if values["name"] in names
        }


        schema = colander.MappingSchema()
        for node in self.schema_nodes:
            schema.add(node)

        deserialized = (values for name, values in schema.deserialize(data).items())
        for values in deserialized:
            typ = next(
                child.typ
                for node in self.schema_nodes
                for child in node.children
                if node.name == values['name']
                if child.name == 'value'
            )
            self._vars[values['name']] = ConfigVar(
                name=values['name'],
                value=values['value'],
                typ=typ,
                original=values['original'],
                source=values['source'],
                path=values['path'],
            )
            self.__validated = True
        return True

    @only_if_validated
    def __getattr__(self, item):
        try:
            return self._vars[item]
        except KeyError as exc:
            raise AttributeError(
                f"type object '{self.__class__.__name__}' has no attribute '{item}'"
            ) from exc

    def declare(self, name, type, source=None, validator=None, required=None):
        schema = ConfigVarSchema(name=name)
        schema.add(colander.SchemaNode(type(), name='value', validator=validator, required=required))
        self.schema_nodes.append(schema)

    def bind(self, data):
        readers = itertools.chain(
            self._readers,
            (BindedReader(data), )
        )
        for reader in readers:
            self.data[reader] = reader()

        self.__validated = False

    def __str__(self):
        data = collections.OrderedDict(
            sorted(self._vars.items(), key=lambda item: item[0])
        )

        def format_text(text, color=colorama.Fore.RESET, max=50):
            chunks = more_itertools.chunked(text, max)
            lines = (color + ("".join(line)) + colorama.Fore.RESET for line in chunks)
            return "\n".join(lines)

        def colorize(source):
            return f"{source.value['color']}{source.name}{colorama.Fore.RESET}"

        def colorize_name(name):
            return f"{BOLD}{colorama.Fore.BLUE}{name}{colorama.Fore.RESET}"

        def value(value):
            return format_text(str(value), colorama.Fore.YELLOW)

        def typ(typ):
            return f"{colorama.Fore.CYAN}{typ.__class__.__name__}{colorama.Fore.RESET}"

        data = (
            (
                colorize_name(d.name),
                value(str(d.value)),
                typ(d.typ),
                format_text(f'"{str(d.original)}"'),
                colorize(d.source),
                d.path,
            )
            for d in data.values()
        )
        return tabulate(
            data, headers=("Name", "Value", "Type", "Original", "Source", "Path")
        )


def my_validator(node, value):
    if not isinstance(value, str) or not value.startswith("My"):
        raise colander.Invalid(node, f"'{value}' not starts with 'My'", value)


config = Configuration(readers=[dotenv_reader])

# config.declare("TEST", colander.String)
# config.declare("TEST2", colander.String)
config.declare("TEST3", colander.String, validator=my_validator, required=False)
config.declare("TEST4", colander.Integer)
config.declare("TEST5", colander.String)
config.declare("TEST6", colander.Bool)

# config.bind({"TEST": "Variable", "TEST2": "Variable", "TEST3": "Variable"})

data = {
    "TEST4": "1",
    "TEST3": "My VariableMy VariableMy VariableMy VariableMy VariableMy VariableMy VariableMy VariableMy VariableMy VariableMy VariableMy Variable",
    "TEST5": 42,
    # "TEST6": 1,
}
data.update(os.environ)
# config._read_env()
config.bind(data)


config.validate()
# config.TEST

# print(config._vars)
