RESERVED_KEYWORDS = {
    'all', 'append', 'as',
    'change', 'create', 'default',
    'delegate', 'delegation',
    'delegator', 'delete', 'do',
    'exit', 'foreach', 'in', 'local',
    'password', 'principal', 'read',
    'replacewith', 'return', 'set',
    'to', 'write', '***'
}


class ReservedKeywordError(Exception):
    pass


class NoKwStr(str):
    def __init__(self, val):
        if val in RESERVED_KEYWORDS:
            raise ReservedKeywordError('"{}" is a reserved keyword'.format(val))
        super(NoKwStr, self).__init__(val)
