class BaseCommand(object):
    def __repr__(self):
        return str(vars(self))


class CreatePrincipal(BaseCommand):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class ChangePassword(BaseCommand):
    def __init__(self, username, new_password):
        self.username = username
        self.new_password = new_password


class Set(BaseCommand):
    def __init__(self, var_name, value, value_type):
        self.var_name = var_name
        self.value = value
        self.value_type = value_type


class AppendTo(BaseCommand):
    def __init__(self, var_name, value, value_type):
        self.var_name = var_name
        self.value = value
        self.value_type = value_type


class Local(BaseCommand):
    def __init__(self, var_name, value, value_type):
        self.var_name = var_name
        self.value = value
        self.value_type = value_type


class ForEach(BaseCommand):
    def __init__(self, var_name, container, replace_with):
        self.var_name = var_name
        self.container = container
        self.replace_with = replace_with


class SetDelegation(BaseCommand):
    def __init__(self, target, source_user, permission, target_user):
        self.target = target
        self.source_user = source_user
        self.permission = permission
        self.target_user = target_user


class DeleteDelegation(BaseCommand):
    def __init__(self, target, source_user, permission, target_user):
        self.target = target
        self.source_user = source_user
        self.permission = permission
        self.target_user = target_user


class DefaultDelegator(BaseCommand):
    def __init__(self, name):
        self.username = name


class Exit(BaseCommand):
    def __init__(self):
        pass


class Return(BaseCommand):
    def __init__(self, value):
        self.value = value
