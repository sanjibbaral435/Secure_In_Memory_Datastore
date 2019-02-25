#!/usr/bin/env python
# -*- coding: utf-8 -*-

# CAVEAT UTILITOR
#
# This file was automatically generated by TatSu.
#
#    https://pypi.python.org/pypi/tatsu/
#
# Any changes you make to it will be overwritten the next time
# the file is generated.


from __future__ import print_function, division, absolute_import, unicode_literals

from tatsu.buffering import Buffer
from tatsu.parsing import Parser
from tatsu.parsing import tatsumasu
from tatsu.util import re, generic_main  # noqa


KEYWORDS = {}  # type: ignore


class DatavaultLanguageBuffer(Buffer):
    def __init__(
        self,
        text,
        whitespace=None,
        nameguard=None,
        comments_re='\\/\\/.*',
        eol_comments_re=None,
        ignorecase=None,
        namechars='',
        **kwargs
    ):
        super(DatavaultLanguageBuffer, self).__init__(
            text,
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            namechars=namechars,
            **kwargs
        )


class DatavaultLanguageParser(Parser):
    def __init__(
        self,
        whitespace=None,
        nameguard=None,
        comments_re='\\/\\/.*',
        eol_comments_re=None,
        ignorecase=None,
        left_recursion=True,
        parseinfo=True,
        keywords=None,
        namechars='',
        buffer_class=DatavaultLanguageBuffer,
        **kwargs
    ):
        if keywords is None:
            keywords = KEYWORDS
        super(DatavaultLanguageParser, self).__init__(
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            left_recursion=left_recursion,
            parseinfo=parseinfo,
            keywords=keywords,
            namechars=namechars,
            buffer_class=buffer_class,
            **kwargs
        )

    @tatsumasu('Program')
    def _prog_(self):  # noqa
        self._token('as')
        self._token('principal')
        self._p_()
        self.name_last_node('user')
        self._token('password')
        self._s_()
        self.name_last_node('password')
        self._token('do')
        self._cmd_()
        self.name_last_node('command')
        self._token('***')
        self.ast._define(
            ['command', 'password', 'user'],
            []
        )

    @tatsumasu('Command')
    def _cmd_(self):  # noqa
        with self._choice():
            with self._option():
                self._token('exit')
                self.name_last_node('exit')
            with self._option():
                self._token('return')
                self.name_last_node('return_')
                self._expr_()
                self.name_last_node('command_expression')
            with self._option():
                self._prim_cmd_()
                self.name_last_node('primitive_command')
                self._cmd_()
                self.name_last_node('command')
            self._error('no available options')
        self.ast._define(
            ['command', 'command_expression', 'exit', 'primitive_command', 'return_'],
            []
        )

    @tatsumasu('Expression')
    def _expr_(self):  # noqa
        with self._choice():
            with self._option():
                self._value_()
                self.name_last_node('exp_value_raw')
            with self._option():
                self._token('[]')
                self.name_last_node('exp_value_list')
            with self._option():
                self._token('{')
                self._fieldvals_()
                self.name_last_node('exp_value_object')
                self._token('}')
            self._error('no available options')
        self.ast._define(
            ['exp_value_list', 'exp_value_object', 'exp_value_raw'],
            []
        )

    @tatsumasu('FieldValues')
    def _fieldvals_(self):  # noqa
        with self._choice():
            with self._option():
                self._x_()
                self.name_last_node('identifier')
                self._token('=')
                self._value_()
                self.name_last_node('contains')
                self._token(',')
                self._fieldvals_()
                self.name_last_node('rest')
            with self._option():
                self._x_()
                self.name_last_node('identifier')
                self._token('=')
                self._value_()
                self.name_last_node('contains')
            self._error('no available options')
        self.ast._define(
            ['contains', 'identifier', 'rest'],
            []
        )

    @tatsumasu('Value')
    def _value_(self):  # noqa
        with self._choice():
            with self._option():
                self._x_()
                self.name_last_node('raw_deep_identifier')
                self._token('.')
                self._y_()
                self.name_last_node('raw_deeper_identifier')
            with self._option():
                self._x_()
                self.name_last_node('raw_identifier')
            with self._option():
                self._s_()
                self.name_last_node('raw_string')
            self._error('no available options')
        self.ast._define(
            ['raw_deep_identifier', 'raw_deeper_identifier', 'raw_identifier', 'raw_string'],
            []
        )

    @tatsumasu('PrimitiveCommand')
    def _prim_cmd_(self):  # noqa
        with self._choice():
            with self._option():
                self._token('create')
                self.name_last_node('name')
                self._token('principal')
                self.name_last_node('name_ext')
                self._p_()
                self.name_last_node('username')
                self._s_()
                self.name_last_node('password')
            with self._option():
                self._token('change')
                self.name_last_node('name')
                self._token('password')
                self.name_last_node('name_ext')
                self._p_()
                self.name_last_node('username')
                self._s_()
                self.name_last_node('password')
            with self._option():
                self._token('set')
                self.name_last_node('name')
                self._token('delegation')
                self.name_last_node('name_ext')
                self._tgt_()
                self.name_last_node('target')
                self._q_()
                self.name_last_node('source_user')
                self._right_()
                self.name_last_node('permission')
                self._token('->')
                self._p_()
                self.name_last_node('user')
            with self._option():
                self._token('set')
                self.name_last_node('name')
                self._x_()
                self.name_last_node('identifier')
                self._token('=')
                self._expr_()
                self.name_last_node('expression')
            with self._option():
                self._token('append')
                self.name_last_node('name')
                self._token('to')
                self.name_last_node('name_ext')
                self._x_()
                self.name_last_node('identifier')
                self._token('with')
                self._expr_()
                self.name_last_node('expression')
            with self._option():
                self._token('local')
                self.name_last_node('name')
                self._x_()
                self.name_last_node('identifier')
                self._token('=')
                self._expr_()
                self.name_last_node('expression')
            with self._option():
                self._token('foreach')
                self.name_last_node('name')
                self._y_()
                self.name_last_node('each')
                self._token('in')
                self._x_()
                self.name_last_node('identifier')
                self._token('replacewith')
                self._expr_()
                self.name_last_node('expression')
            with self._option():
                self._token('delete')
                self.name_last_node('name')
                self._token('delegation')
                self.name_last_node('name_ext')
                self._tgt_()
                self.name_last_node('target')
                self._q_()
                self.name_last_node('source_user')
                self._right_()
                self.name_last_node('permission')
                self._token('->')
                self._p_()
                self.name_last_node('user')
            with self._option():
                self._token('default')
                self.name_last_node('name')
                self._token('delegator')
                self.name_last_node('name_ext')
                self._token('=')
                self._p_()
                self.name_last_node('user')
            self._error('no available options')
        self.ast._define(
            ['each', 'expression', 'identifier', 'name', 'name_ext', 'password', 'permission', 'source_user', 'target', 'user', 'username'],
            []
        )

    @tatsumasu()
    def _tgt_(self):  # noqa
        with self._choice():
            with self._option():
                self._token('all')
            with self._option():
                self._x_()
            self._error('no available options')

    @tatsumasu('Permission')
    def _right_(self):  # noqa
        with self._choice():
            with self._option():
                self._token('read')
                self.name_last_node('read')
            with self._option():
                self._token('write')
                self.name_last_node('write')
            with self._option():
                self._token('append')
                self.name_last_node('append')
            with self._option():
                self._token('delegate')
                self.name_last_node('delegate')
            self._error('no available options')
        self.ast._define(
            ['append', 'delegate', 'read', 'write'],
            []
        )

    @tatsumasu('str')
    def _s_(self):  # noqa
        self._pattern(r'"[A-Za-z0-9_ ,;\.?!-]*"')

    @tatsumasu('NoKwStr')
    def _x_(self):  # noqa
        self._pattern(r'[A-Za-z][A-Za-z0-9_]*')

    @tatsumasu('NoKwStr')
    def _p_(self):  # noqa
        self._pattern(r'[A-Za-z][A-Za-z0-9_]*')

    @tatsumasu('str')
    def _q_(self):  # noqa
        self._pattern(r'[A-Za-z][A-Za-z0-9_]*')

    @tatsumasu('str')
    def _r_(self):  # noqa
        self._pattern(r'[A-Za-z][A-Za-z0-9_]*')

    @tatsumasu('str')
    def _y_(self):  # noqa
        self._pattern(r'[A-Za-z][A-Za-z0-9_]*')


class DatavaultLanguageSemantics(object):
    def prog(self, ast):  # noqa
        return ast

    def cmd(self, ast):  # noqa
        return ast

    def expr(self, ast):  # noqa
        return ast

    def fieldvals(self, ast):  # noqa
        return ast

    def value(self, ast):  # noqa
        return ast

    def prim_cmd(self, ast):  # noqa
        return ast

    def tgt(self, ast):  # noqa
        return ast

    def right(self, ast):  # noqa
        return ast

    def s(self, ast):  # noqa
        return ast

    def x(self, ast):  # noqa
        return ast

    def p(self, ast):  # noqa
        return ast

    def q(self, ast):  # noqa
        return ast

    def r(self, ast):  # noqa
        return ast

    def y(self, ast):  # noqa
        return ast


def main(filename, startrule, **kwargs):
    with open(filename) as f:
        text = f.read()
    parser = DatavaultLanguageParser()
    return parser.parse(text, startrule, filename=filename, **kwargs)


if __name__ == '__main__':
    import json
    from tatsu.util import asjson

    ast = generic_main(main, DatavaultLanguageParser, name='DatavaultLanguage')
    print('AST:')
    print(ast)
    print()
    print('JSON:')
    print(json.dumps(asjson(ast), indent=2))
    print()

