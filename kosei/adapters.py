import collections

import colorama
import more_itertools
from tabulate import tabulate

colorama.init()
BOLD = "\033[1m"


class DictToDeserializeRawVarAdapter:
    def __init__(self, rawvar):
        self.rawvar = rawvar

    def to_dict(self):
        return {
            "name": self.rawvar.name,
            "value": self.rawvar.value,
            "original": self.rawvar.value,
            "source": self.rawvar.source,
            "path": self.rawvar.path,
        }


class ConsoleOutputConfigurationAdapter:
    def __init__(self, configuration):
        self.configuration = configuration

    def get_output(self):
        data = collections.OrderedDict(
            sorted(self.configuration._vars.items(), key=lambda item: item[0])
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
