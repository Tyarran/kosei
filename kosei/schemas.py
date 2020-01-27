import colander
from kosei import constants


class Source(colander.SchemaType):
    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        if appstruct.name not in list(constants.Sources.__members__):
            raise colander.Invalid(node, f"{appstruct.name} is not in Sources enum")
        return appstruct.name

    def deserialize(self, node, cstruct):
        if isinstance(cstruct, constants.Sources):
            return cstruct
        if not isinstance(cstruct, str):
            raise colander.Invalid(node, f"{cstruct} is not a str")
        try:
            result = constants.Sources[cstruct]
        except KeyError:
            raise colander.Invalid(node, f"{cstruct} is not a valid enum value")
        return result


class Variable(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(), required=True)
    original = colander.SchemaNode(colander.String(), required=True)
    source = colander.SchemaNode(Source(), required=True)
    path = colander.SchemaNode(colander.String(), required=True, missing=None)
