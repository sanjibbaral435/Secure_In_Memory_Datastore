class Item(object):
    def __init__(self, id=None, value=None, type=None, scope=None):
        self.id = id
        self.value = value
        self.type = type
        self.scope = scope

    def __repr__(self):
        return '<Item id={}, value={}, type={}, scope={}>'.format(
            self.id,
            self.value,
            self.type,
            self.scope
        )

    def get_type(self):
        if isinstance(self.value, str):
            return 'string'
        if isinstance(self.value, dict):
            return 'record'
        if isinstance(self.value, list):
            return 'list'
        if isinstance(self.value, Item):
            return self.value.get_type()

# scope is either local or global
# type is either string, record or list
