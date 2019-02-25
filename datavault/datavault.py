# -*- coding: utf-8 -*-
import logging
import pickle

import simplecrypt

from tatsu.util import asjson
from connection import ConnectionHandler, VaultServer
from lang.commands import Local, CreatePrincipal, ChangePassword, Set, AppendTo, ForEach, SetDelegation, \
    DeleteDelegation, DefaultDelegator, Exit, Return
from models.item import Item
from models.item_store import ItemStore
from models.permissions_manager import PermissionManager
from models.user import User
from models.user_store import UserStore
from response import Response


class PermissionError(Exception):
    pass


class NoSuchVariableError(Exception):
    pass


class NoSuchUserError(Exception):
    pass


class InvalidOperationError(Exception):
    pass


class InvalidTypeError(Exception):
    pass


class DuplicateKeyError(Exception):
    pass


def get_deep(hash_map, *keys):
    return reduce(lambda value, key: value.get(key) if value else None, keys, hash_map)


class DataVault(object):
    def __init__(self, host='0.0.0.0', port=8080, admin_password='admin'):
        self.host = host
        self.port = port
        self.server = None
        self.item_store = ItemStore()
        self.user_store = UserStore(admin_password=admin_password)
        self.permissions = PermissionManager(self.item_store, self.user_store)
        self.backup_path = None

    def start(self):
        logging.debug('Starting a server on %s:%s', self.host, self.port)
        self.server = VaultServer((self.host, self.port), self, ConnectionHandler)
        self.server.serve_forever()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()

    def actual_port(self):
        if self.server:
            return self.server.socket.getsockname()[1]

    def add_user(self, username, password):
        u = User(username, password)
        self.user_store[username] = u

    def add_item(self, id, value, type, scope):
        if isinstance(value, Item):
            import traceback
            traceback.print_stack()
        i = Item(id, value, type, scope)
        self.item_store[id] = i

    def delete_item(self, id):
        del self.item_store[id]

    def add_item_object(self, item):
        self.item_store[item.id] = item

    def command_process(self, program_info, command):
        if program_info.username not in self.user_store:
            return Response("FAILED")
        elif program_info.password != self.user_store[program_info.username].password:
            return Response("DENIED")
        else:
            caller = program_info.username
            if isinstance(command, Local):
                return self._run_local(caller, command)
            elif isinstance(command, CreatePrincipal):
                return self._run_create_principal(caller, command)
            elif isinstance(command, ChangePassword):
                return self._run_change_password(program_info, caller, command)
            elif isinstance(command, Set):
                return self._run_set(caller, command)
            elif isinstance(command, AppendTo):
                return self._run_append_to(caller, command)
            elif isinstance(command, ForEach):
                return self._run_for_each(caller, command)
            elif isinstance(command, SetDelegation):
                return self._run_set_delegation(caller, command)
            elif isinstance(command, DeleteDelegation):
                return self._run_delete_delegation(caller, command)
            elif isinstance(command, DefaultDelegator):
                return self._run_default_delegator(caller, command)
            elif isinstance(command, Exit):
                return self._run_exit(caller, command)
            elif isinstance(command, Return):
                return self._run_return(caller, command)

    def _run_set(self, caller, command):
        try:
            item = self.evaluate(command.value, caller)
        except KeyError:
            return Response('FAILED')
        except InvalidTypeError:
            return Response('FAILED')
        except NoSuchUserError:
            return Response('FAILED')
        except NoSuchVariableError:
            return Response('FAILED')
        except InvalidOperationError:
            return Response('FAILED')
        except DuplicateKeyError:
            return Response('FAILED')
        except PermissionError:
            return Response('DENIED')
        else:
            if command.var_name in self.item_store:
                if self._has_permission("write", self.item_store[command.var_name], self.user_store[caller]) is False:
                    return Response('DENIED')
                else:
                    tgt = self.item_store[command.var_name]
                    if isinstance(item, Item):
                        tgt.value = item.value
                    else:
                        tgt.value = item
                    self.delete_item(tgt.id)
                    self.add_item_object(tgt)

            else:
                self.add_item(command.var_name, item, None, "global")
                if caller != "admin":
                    # if it's created & curr_principal != admin delegate permissions from admin to cur_principal
                    command = SetDelegation(command.var_name, "admin", "write", caller)
                    response = self._run_set_delegation("admin", command)

                    if response != "SET_DELEGATION":
                        logging.error('Oops, got an invalid response: {}'.format(response))

                    command = SetDelegation(command.var_name, "admin", "read", caller)
                    self._run_set_delegation("admin", command)

                    if response != "SET_DELEGATION":
                        logging.error('Oops, got an invalid response: {}'.format(response))

                    command = SetDelegation(command.var_name, "admin", "append", caller)
                    self._run_set_delegation("admin", command)

                    if response != "SET_DELEGATION":
                        logging.error('Oops, got an invalid response: {}'.format(response))

                    command = SetDelegation(command.var_name, "admin", "delegation", caller)
                    self._run_set_delegation("admin", command)

                    if response != "SET_DELEGATION":
                        logging.error('Oops, got an invalid response: {}'.format(response))

            return Response('SET')

    def _run_create_principal(self, caller, command):
        if caller != "admin":
            return Response('DENIED')
        elif command.username in self.user_store:
            return Response('FAILED')
        else:
            new_user = User(command.username, command.password)
            self.user_store[command.username] = new_user

            if self.permissions.default_delegator != "anyone":
                source_user = self.permissions.default_delegator

                command_set = SetDelegation("all", source_user, "read", command.username)
                response = self._run_set_delegation(caller, command_set)

                if response.status != "SET_DELEGATION":
                    logging.error('Invalid set delegation response when running Set command: {}'.format(response))

                command_set = SetDelegation("all", source_user, "write", command.username)
                response = self._run_set_delegation(caller, command_set)

                if response.status != "SET_DELEGATION":
                    logging.error('Invalid set delegation response when running Set command: {}'.format(response))

                command_set = SetDelegation("all", source_user, "append", command.username)
                response = self._run_set_delegation(caller, command_set)

                if response.status != "SET_DELEGATION":
                    logging.error('Invalid set delegation response when running Set command: {}'.format(response))

                command_set = SetDelegation("all", source_user, "delegation", command.username)
                response = self._run_set_delegation(caller, command_set)

                if response.status != "SET_DELEGATION":
                    logging.error('Invalid set delegation response when running Set command: {}'.format(response))

            return Response('CREATE_PRINCIPAL')

    def _run_change_password(self, program_info, caller, command):
        if command.username not in self.user_store:
            return Response('FAILED')
        elif caller == "admin" or caller == command.username:
            self.user_store[command.username].password = command.new_password
            if caller == command.username:
                program_info.password = command.new_password
            return Response('CHANGE_PASSWORD')
        else:
            return Response('DENIED')

    def _run_local(self, caller, command):
        try:
            if command.var_name not in self.item_store:
                value = self.evaluate(command.value, caller)
                if isinstance(value, Item):
                    value = value.value
                self.add_item(command.var_name, value, None, "local")
                return Response('LOCAL')
            else:
                return Response('FAILED')
        except KeyError:
            return Response('FAILED')
        except InvalidTypeError:
            return Response('FAILED')
        except NoSuchUserError:
            return Response('FAILED')
        except NoSuchVariableError:
            return Response('FAILED')
        except InvalidOperationError:
            return Response('FAILED')
        except DuplicateKeyError:
            return Response('FAILED')
        except PermissionError:
            return Response('DENIED')

    def _run_append_to(self, caller, command):
        if command.var_name not in self.item_store:
            return Response('FAILED')

        # either write or append permission is required to append
        elif not self._has_permission("write", self.item_store[command.var_name],
                                      self.user_store[caller]) and not self._has_permission("append", self.item_store[
            command.var_name], self.user_store[caller]):
            return Response('DENIED')
        else:
            try:
                item = self.evaluate(command.value, caller)
            except KeyError:
                return Response('FAILED')
            except InvalidTypeError:
                return Response('FAILED')
            except NoSuchUserError:
                return Response('FAILED')
            except NoSuchVariableError:
                return Response('FAILED')
            except InvalidOperationError:
                return Response('FAILED')
            except DuplicateKeyError:
                return Response('FAILED')
            except PermissionError:
                return Response('DENIED')
            else:
                original_item = self.item_store[command.var_name].value
                if isinstance(original_item, list):
                    if isinstance(item, list):
                        original_item.extend(item)
                    elif isinstance(item, Item):
                        if item.get_type() == 'list':
                            original_item.extend(item.value)
                        else:
                            original_item.append(item.value)
                    else:
                        original_item.append(item)
                    return Response('APPEND')
                else:
                    return Response('FAILED')

    def _run_for_each(self, caller, command):
        if command.container not in self.item_store:
            return Response('FAILED')

        elif self._has_permission("write", self.item_store[command.container], self.user_store[caller]) is False:
            return Response('DENIED')
        elif self._has_permission("read", self.item_store[command.container], self.user_store[caller]) is False:
            return Response('DENIED')
        elif command.var_name in self.item_store:
            return Response('FAILED')
        elif not isinstance(self.item_store[command.container].value, list):
            return Response('FAILED')
        else:
            container = self.item_store[command.container]
            new_list = []
            for each_item in container.value:
                self.add_item(command.var_name, each_item, None, "local")
                try:
                    changed_item = self.evaluate(command.replace_with, caller)
                except KeyError:
                    return Response('FAILED')
                except InvalidTypeError:
                    return Response('FAILED')
                except NoSuchUserError:
                    return Response('FAILED')
                except NoSuchVariableError:
                    return Response('FAILED')
                except InvalidOperationError:
                    return Response('FAILED')
                except DuplicateKeyError:
                    return Response('FAILED')
                except PermissionError:
                    return Response('DENIED')
                new_list.append(changed_item)
            self.delete_item(command.var_name)
            self.item_store[command.container].value = new_list
            return Response('FOREACH')

    def _run_set_delegation(self, caller, command):
        if command.source_user not in self.user_store or command.target_user not in self.user_store:
            return Response('FAILED')
        elif command.target != 'all' and self.item_store[command.target].scope == "local" and command.target not in self.item_store:
            return Response('FAILED')
        elif caller != "admin" and caller != command.source_user:
            return Response('DENIED')
        elif caller == command.source_user and \
                not self._has_permission(command.permission, self.item_store[command.target],
                                         self.user_store[command.source_user]):
            return Response('DENIED')
        else:
            if command.target == "all":
                for item in self._get_items_with_this_permission(command.permission, self.user_store[command.source_user]):
                    new_command = SetDelegation(item, command.source_user, command.permission, command.target_user)
                    rsp = self._run_set_delegation(caller, new_command)
                    if rsp.status != 'SET_DELEGATION':
                        return rsp
                if command.target_user != 'anyone':
                    return Response('SET_DELEGATION')
            if command.target_user == "anyone":
                for usr in self.user_store:
                    command.target_user = usr
                    rsp = self._run_set_delegation(caller, command)
                    if rsp.status != 'SET_DELEGATION':
                        return rsp
                return Response('SET_DELEGATION')
            elif self._has_permission(command.permission, self.item_store[command.target],
                                      self.user_store[command.source_user]):
                self.permissions.add_permission(self.user_store[command.target_user], self.item_store[command.target],
                                                command.permission)
                return Response('SET_DELEGATION')
            else:
                return Response('DENIED')

    def _run_delete_delegation(self, caller, command):
        if command.source_user not in self.user_store or command.target_user not in self.user_store:
            return Response('FAILED')
        elif command.target not in self.item_store or self.item_store[command.target].scope == "local":
            return Response('FAILED')
        elif caller != "admin" and caller != command.source_user and caller != command.target_user:
            return Response('DENIED')
        elif caller == command.source_user and self._has_permission(command.permission, self.item_store[command.target],
                                                                    self.user_store[command.source_user]) is False:
            return Response('DENIED')
        else:
            if command.target == "all":
                for item in self._get_items_with_this_permission(command.permission, self.user_store[command.source_user]):
                    command.target = item
                    self._run_delete_delegation(caller, command)
            elif command.target_user == "anyone":
                for usr in self.user_store:
                    command.target_user = usr
                    self._run_delete_delegation(caller, command)
            elif self._has_permission("delegation", self.item_store[command.target],
                                      self.user_store[command.source_user]):
                self.permissions.revoke_permission(command.target_user, self.item_store[command.target],
                                                   command.permission)
                return Response('DELETE_DELEGATION')
            else:
                return Response('DENIED')

    def _run_default_delegator(self, caller, command):
        if command.username not in self.user_store:
            return Response('FAILED')
        elif caller != "admin":
            return Response('DENIED')
        else:
            self.permissions.default_delegator = command.username
            return Response('DEFAULT_DELEGATOR')

    def _run_exit(self, caller, command):
        if caller == "admin":
            return Response('EXITING')
        else:
            return Response('DENIED')

    def _run_return(self, caller, command):
        if caller not in self.user_store:
            return Response('FAILED')
        try:
            value = self.evaluate(command.value, self.user_store[caller])
        except KeyError:
            return Response('FAILED')
        except InvalidTypeError:
            return Response('FAILED')
        except NoSuchUserError:
            return Response('FAILED')
        except NoSuchVariableError:
            logging.debug('Trying to return something, but no such variable exists')
            return Response('FAILED')
        except InvalidOperationError:
            return Response('FAILED')
        except DuplicateKeyError:
            return Response('FAILED')
        except PermissionError:
            return Response('DENIED')
        else:
            return Response("RETURNING", value)

    def _get_items_with_this_permission(self, perm, principal):
        a = []
        for item in self.permissions.item_store:
            if perm == "delegate":
                if principal.username in self.permissions.permissions.get(item).delegate:
                    a.append(item)
            elif perm == "read":
                if principal.username in self.permissions.permissions.get(item).read:
                    a.append(item)
            elif perm == "append":
                if principal.username in self.permissions.permissions.get(item).append:
                    a.append(item)
            elif perm == "write":
                if principal.username in self.permissions.permissions.get(item).write:
                    a.append(item)
        return a

    def _has_permission(self, perm, item, principal):
        if isinstance(principal, str):
            try:
                principal = self.user_store[principal]
            except KeyError:
                return False

        if principal.username == "admin":
            return True

        if isinstance(item, str):
            item = self.item_store[item]

        if item.id not in self.permissions.permissions:
            return False

        if perm == "delegate":
            if principal.username in self.permissions.permissions.get(item.id).delegate:
                return True
        elif perm == "read":
            if principal.username in self.permissions.permissions.get(item.id).read:
                return True

        elif perm == "append":
            if principal.username in self.permissions.permissions.get(item.id).append:
                return True

        elif perm == "write":
            if principal.username in self.permissions.permissions.get(item.id).write:
                return True

        return False

    def evaluate(self, expression, principal):
        if expression.exp_value_raw:
            return self._get_value(expression.exp_value_raw, principal)
        elif expression.exp_value_list:
            return []  # apparently, we can only have empty list expressions
        elif expression.exp_value_object:
            return self._evaluate_expression_object(expression.exp_value_object, principal)

    def _evaluate_expression_object(self, exp_value_object, principal, prev_identifiers=None):
        if prev_identifiers == None:
            prev_identifiers = set()

        obj = {}
        identifier = exp_value_object.identifier

        if identifier in prev_identifiers:
            raise DuplicateKeyError('Found a record containing duplicate key: {}'.format(identifier))

        val = self._get_value(exp_value_object.contains, principal)

        if isinstance(val, list):
            raise InvalidTypeError('Value of a record key may not be a list')
        if isinstance(val, dict):
            raise InvalidTypeError('Value of a record key may not be another record')
        if isinstance(val, Item):
            _type = val.get_type()
            if _type != 'string':
                raise InvalidTypeError('Value of a record key may not be a {}'.format(_type))
        obj[identifier] = val
        if exp_value_object.rest:
            prev_identifiers.add(identifier)
            rest = self._evaluate_expression_object(exp_value_object.rest, principal, prev_identifiers)
            if rest:
                for k in rest:
                    obj[k] = rest[k]
        return obj

    def _get_value(self, value, principal):
        if value.raw_identifier:
            if value.raw_identifier in self.item_store:
                if self._has_permission('read', value.raw_identifier, principal):
                    return self.item_store[value.raw_identifier]
                else:
                    raise PermissionError('User {} is not allowed to access {}'.format(principal, value.raw_identifier))
            else:
                raise NoSuchVariableError('No such variable exists: {}'.format(value.raw_identifier))
        elif value.raw_deep_identifier:
            if value.raw_deep_identifier in self.item_store:
                item_val = self.item_store[value.raw_deep_identifier].value
                if not isinstance(item_val, dict):
                    raise InvalidOperationError('Identifier {} is '
                                                'not an object, so cannot access nested '
                                                'attribute "{}"'.format(value.raw_deep_identifier,
                                                                        value.raw_deeper_identifier))
                try:
                    return item_val[value.raw_deeper_identifier]
                except KeyError:
                    raise NoSuchVariableError('Nested record processing failed for key: {}'.format(value.raw_deeper_identifier))
            else:
                raise NoSuchVariableError('No such variable exists: {}'.format(value.raw_identifier))
        elif value.raw_string:
            return value.raw_string[1:-1]  # remove the starting and ending quotes

    def _get_admin_password(self):
        if 'admin' in self.user_store:
            return self.user_store['admin'].password
        raise NoSuchUserError('No user: "admin"')

    def backup(self):
        try:
            key = self._get_admin_password()
        except NoSuchUserError:
            logging.error('Unable to perform a backup, admin user does not exist')
        else:
            permissions_backup = pickle.dumps(self.permissions)
            with open('/tmp/datavault.bak', 'wb') as permissions_backup_file:
                permissions_backup_file.write(simplecrypt.encrypt(key, permissions_backup))

    def restore(self):
        try:
            key = self._get_admin_password()
        except NoSuchUserError:
            logging.error('Unable to perform a restore, admin user does not exist')
        else:
            try:
                with open('/tmp/datavault.bak', 'rb') as permissions_backup_file:
                    ciphertext = permissions_backup_file.read()
                    pickled = simplecrypt.decrypt(key, ciphertext)
                    old_permission_mgr = pickle.loads(pickled)
                    self.item_store = old_permission_mgr.item_store
                    self.user_store = old_permission_mgr.user_store
                    self.permissions = old_permission_mgr
                    logging.debug('Restored old state')

            except IOError:
                logging.error('Unable to restore backup!')
                return
