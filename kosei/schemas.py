import colander


class SettingsItemSchema(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    source = colander.SchemaNode(colander.String())
    original = colander.SchemaNode(colander.String())


class SettingsSchema(colander.SequenceSchema):
    items = SettingsItemSchema()
