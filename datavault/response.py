import json

from models.item import Item


class _Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Item):
            return o.value
        return json.JSONEncoder.default(self, o)


VALID_STATUSES = {
    'SUCCESS',
    'DENIED',
    'FAILED',
    'CREATE_PRINCIPAL',
    'SET_DELEGATION',
    'DELETE_DELEGATION',
    'CHANGE_PASSWORD',
    'EXITING',
    'DEFAULT_DELEGATOR',
    'LOCAL',
    'SET',
    'RETURNING',
    'APPEND',
    'FOREACH'
}


class Response(object):
    def __init__(self, status, output=None):
        if status not in VALID_STATUSES:
            raise TypeError('Invalid status provided')
        self.status = status
        self.output = output

    def to_json(self):
        if self.output is not None:
            _response = {'status': self.status, 'output': self.output}
        else:
            _response = {'status': self.status}
        return json.dumps(_response, cls=_Encoder)
