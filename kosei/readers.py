import os

from dotenv import dotenv_values, find_dotenv
from kosei import constants, models


def dotenv_reader():
    source = constants.Sources.DOTENV
    path = find_dotenv()
    if path:
        values = dotenv_values(path)
        return (
            models.RawVar(name=name, value=value, source=source, path=path)
            for name, value in values.items()
        )


class BindedReader:
    source = constants.Sources.BINDED

    def __init__(self, data):
        self.data = data

    def __call__(self):
        result = (
            models.RawVar(name=name, value=str(value), source=self.source, path=None,)
            for name, value in self.data.items()
        )
        return result


def env_reader():
    source = constants.Sources.ENVVAR

    result = (
        models.RawVar(name, value=value, source=source, path=None)
        for name, value in os.environ.items()
    )
    return result
