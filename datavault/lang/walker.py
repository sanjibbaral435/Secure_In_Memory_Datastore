from tatsu.model import NodeWalker
from datavault.lang.program_info import ProgramInfo

import datavault.lang.commands as commands


class DatavaultLangWalker(NodeWalker):
    def __init__(self, program_info=None):
        if program_info is None:
            program_info = ProgramInfo()

        self.program_info = program_info

    def walk_Program(self, node):
        self.program_info.username = node.user
        self.program_info.password = node.password[1:-1]
        self.walk(node.command)

    def walk_Command(self, node):
        if node.exit:
            self.program_info.commands.append(commands.Exit())
        elif node.return_:
            return_cmd = commands.Return(node.command_expression)
            self.program_info.commands.append(return_cmd)
        else:
            if node.primitive_command:
                self.walk(node.primitive_command)
            if node.command:
                self.walk(node.command)

    def walk_PrimitiveCommand(self, node):
        if node.name == 'set' and not node.name_ext:
            identifier = node.identifier
            value = node.expression

            if node.expression.exp_value_raw:
                value_type = 'string'
            elif node.expression.exp_value_list:
                value_type = 'list'
            else:
                value_type = 'object'

            set_command = commands.Set(identifier, value, value_type)
            self.program_info.commands.append(set_command)
        elif node.name == 'create' and node.name_ext == 'principal':
            new_name = node.username
            password = node.password[1:-1]
            create_prin_command = commands.CreatePrincipal(new_name, password)
            self.program_info.commands.append(create_prin_command)
        elif node.name == 'change' and node.name_ext == 'password':
            username = node.username
            password = node.password[1:-1]
            change_pwd_command = commands.ChangePassword(username, password)
            self.program_info.commands.append(change_pwd_command)
        elif node.name == 'append' and node.name_ext == 'to':
            var_name = node.identifier
            value = node.expression
            if node.expression.exp_value_raw:
                value_type = 'string'
            elif node.expression.exp_value_list:
                value_type = 'list'
            else:
                value_type = 'object'
            append_to_cmd = commands.AppendTo(var_name, value, value_type)
            self.program_info.commands.append(append_to_cmd)
        elif node.name == 'local' and not node.name_ext:
            identifier = node.identifier
            value = node.expression

            if node.expression.exp_value_raw:
                value_type = 'string'
            elif node.expression.exp_value_list:
                value_type = 'list'
            else:
                value_type = 'object'

            local_command = commands.Local(identifier, value, value_type)
            self.program_info.commands.append(local_command)
        elif node.name == 'foreach' and not node.name_ext:
            var_name = node.each
            container = node.identifier
            expression = node.expression
            foreach_command = commands.ForEach(var_name, container, expression)
            self.program_info.commands.append(foreach_command)
        elif node.name == 'default' and node.name_ext == 'delegator':
            user = node.user
            def_delegator = commands.DefaultDelegator(user)
            self.program_info.commands.append(def_delegator)
        elif node.name == 'set' and node.name_ext == 'delegation':
            target = node.target
            source_user = node.source_user
            if node.permission.write:
                permission = 'write'
            if node.permission.read:
                permission = 'read'
            if node.permission.append:
                permission = 'append'
            if node.permission.delegate:
                permission = 'delegate'
            user = node.user
            set_delegation = commands.SetDelegation(target, source_user, permission, user)
            self.program_info.commands.append(set_delegation)
        elif node.name == 'delete' and node.name_ext == 'delegation':
            target = node.target
            source_user = node.source_user
            permission = node.permission
            user = node.user
            delete_delegation = commands.DeleteDelegation(target, source_user, permission, user)
            self.program_info.commands.append(delete_delegation)
