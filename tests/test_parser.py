#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import unittest

from tatsu.model import ModelBuilderSemantics

from datavault.lang import parser
from datavault.lang import walker

"""Tests for `datavault.parser` package."""


class TestParser(unittest.TestCase):
    """Tests for `datavault` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_basic_parser(self):
        """Test the Parser."""

        raw_command = """
            as principal bob password "B0BPWxxd" do
               set z = "bobs string"
               set x = "another string"
               return x
            ***
        """
        p = parser.DatavaultLanguageParser()

        p.parse(raw_command, rule_name='prog', semantics=ModelBuilderSemantics())

    def test_walker_program(self):
        """
        Tests the program method of the walker.

        :return:
        """
        walker_ = walker.DatavaultLangWalker()

        raw_command = """
            as principal bob password "B0BPWxxd" do
               set z = "bobs string"
               set x = "another string"
               return x
            ***
        """
        p = parser.DatavaultLanguageParser()

        ast = p.parse(raw_command, rule_name='prog', semantics=ModelBuilderSemantics())
        credentials = walker_.walk(ast)

        self.assertEquals(credentials.user, 'bob')
        self.assertEquals(credentials.password, '"B0BPWxxd"')

    def test_complicated(self):
        """
        Tests a more complicated command
        """

        raw_command = """
            as principal admin password "admin" do
                set records = []
                append to records with { name = "mike", date = "1-1-90" }
                append to records with { name = "sandy", date = "1-1-90" }
                append to records with { name = "dave", date = "1-1-85" }
                return records
            ***
        """
        p = parser.DatavaultLanguageParser()

        p.parse(raw_command, rule_name='prog', semantics=ModelBuilderSemantics())

    def test_comments(self):
        """
        Tests whether parser accepts comments
        """

        raw_command = """
            as principal admin password "admin" do
                set records = [] // first comment
                append to records with { name = "mike", date = "1-1-90" }
                // second comment
                append to records with { name = "sandy", date = "1-1-90" }
                append to records with { name = "dave", date = "1-1-85" }
                return records
            ***
            // done
        """
        p = parser.DatavaultLanguageParser()

        p.parse(raw_command, rule_name='prog', semantics=ModelBuilderSemantics())


if __name__ == "__main__":
    unittest.main()
