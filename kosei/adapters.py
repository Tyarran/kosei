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
