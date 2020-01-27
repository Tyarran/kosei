import collections
import functools
import itertools
import os

import colander
import colorama
import more_itertools
from kosei import adapters, models
from kosei import readers as readers_mod
from kosei import schemas
from tabulate import tabulate

__version__ = "0.1.0"
colorama.init()
BOLD = "\033[1m"


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

    def __init__(self, readers=None):
        self.readers = readers or []

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
            values.name: adapters.DictToDeserializeRawVarAdapter(values).to_dict()
            for data in self.data.values()
            for values in data
            if values.name in names
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
                if node.name == values["name"]
                if child.name == "value"
            )
            self._vars[values["name"]] = models.Variable(
                name=values["name"],
                value=values["value"],
                typ=typ,
                original=values["original"],
                source=values["source"],
                path=values["path"],
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
        schema = schemas.Variable(name=name)
        schema.add(
            colander.SchemaNode(
                type(), name="value", validator=validator, required=required
            )
        )
        self.schema_nodes.append(schema)

    def bind(self, data):
        readers = itertools.chain(self.readers, (readers_mod.BindedReader(data),))
        for reader in readers:
            self.data[reader] = reader() or {}

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


config = Configuration(readers=[readers_mod.dotenv_reader])

config.declare("TEST3", colander.String, validator=my_validator, required=False)
config.declare("TEST4", colander.Integer)
config.declare("TEST5", colander.String)
config.declare("TEST6", colander.Bool)

data = {
    "TEST4": "1",
    "TEST3": "My Variable",
    "TEST5": 42,
    # "TEST6": 1,
}
data.update(os.environ)
config.bind(data)


config.validate()
