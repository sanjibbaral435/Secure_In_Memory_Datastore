from datavault.models.user import User


class UserStore(dict):

    def __init__(self, admin_password='admin'):
        self['admin'] = User(username='admin', password=admin_password)
