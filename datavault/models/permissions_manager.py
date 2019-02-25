class PermissionManager(object):
    def __init__(self, item_store, user_store):
        self.item_store = item_store
        self.user_store = user_store
        self.permissions = {}
        self.default_delegator = "anyone"

    def add_permission(self, user, item, permission):
        if item.id not in self.permissions:
            self.permissions[item.id] = Permission()

        if permission == "delegate":
            self.permissions.get(item.id).delegate.add(user.username)

        elif permission == "read":
            self.permissions.get(item.id).read.add(user.username)

        elif permission == "append":
            self.permissions.get(item.id).append.add(user.username)
            self.permissions.get(item.id).read.add(user.username)

        elif permission == "write":
            self.permissions.get(item.id).read.add(user.username)
            self.permissions.get(item.id).append.add(user.username)
            self.permissions.get(item.id).write.add(user.username)

        else:
            return None

    def revoke_permission(self, user, item, permission):

        if permission == "delegate":
            self.permissions.get(item.id).delegate.discard(user.username)

        elif permission == "read":
            self.permissions.get(item.id).read.discard(user.username)
            self.permissions.get(item.id).append.discard(user.username)
            self.permissions.get(item.id).write.discard(user.username)

        elif permission == "append":
            self.permissions.get(item.id).append.discard(user.username)
            self.permissions.get(item.id).write.discard(user.username)

        elif permission == "write":
            self.permissions.get(item.id).write.discard(user.username)

        else:
            return None


class Permission(object):
    def __init__(self):
        self.read = set()
        self.write = set()
        self.append = set()
        self.delegate = set()
