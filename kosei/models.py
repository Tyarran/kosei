import collections

RawVar = collections.namedtuple("RawVar", ["name", "value", "source", "path"],)

Variable = collections.namedtuple(
    "Variable", ["name", "value", "original", "source", "typ", "path"]
)
