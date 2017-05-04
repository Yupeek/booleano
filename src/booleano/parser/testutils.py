# -*- coding: utf-8 -*-

# Copyright (c) 2009 by Gustavo Narea <http://gustavonarea.net/>.

# This file is part of Booleano <http://code.gustavonarea.net/booleano/>.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, distribute with
# modifications, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written authorization.
"""
Semi-automatic utilities to test Booleano grammars and parsers.

"""
from __future__ import unicode_literals

from nose.tools import eq_, raises
from pyparsing import ParseException

from booleano.parser.parsers import ConvertibleParser

__all__ = ("BaseGrammarTest", )


class BaseGrammarTest(object):
    """
    Base test case for a grammar and the expressions its parser could handle.

    Subclasses must define all the following attributes for the test case to
    work.

    .. attribute:: grammar

        An instance of the grammar to be tested. **This attribute must be set
        in the subclasses**, like this::

            from booleano.parser import Grammar

            class TestMyGrammar(BaseGrammarTest):

                grammar = Grammar(ne="<>")

        :type: :class:`booleano.parser.Grammar`

    .. attribute:: expressions

        A dictionary with all the valid expressions recognized by the grammar,
        where each key is the expression itself and its item is the mock
        representation of the operation.

        :type: dict

    .. attribute:: badformed_expressions

        A list of expressions that are bad-formed in the :attr:`grammar`.

        :type: list

    .. attribute:: single_operands

        A dictionary where the key is an expression that contains a single
        operand (i.e., no operator) and the item is the :term:`root node` of the
        expected :term:`parse tree`.

        :type: dict

    .. attribute:: invalid_operands

        A list of expressions which contain a single operand and it is invalid.

        :type: list

    """

    def __init__(self, *args, **kwargs):
        super(BaseGrammarTest, self).__init__(*args, **kwargs)
        # Let's use the convertible parser to ease testing:
        self.parser = ConvertibleParser(self.grammar)

    def test_expressions(self):
        """Valid expressions should yield the expected parse tree."""
        for expression, expected_node in self.expressions.items():

            # Making a Nose test generator:
            def check():
                tree = self.parser(expression)
                expected_node.check_equivalence(tree.root_node)
            check.description = 'Operation "%s" should yield "%s"' % \
                                (repr(expression), expected_node)

            yield check

    def test_badformed_expressions(self):
        """Expressions with an invalid syntax must not yield a parse tree."""
        for expression in self.badformed_expressions:

            # Making a Nose test generator:
            @raises(ParseException)
            def check():
                self.parser(expression)
            check.description = "'%s' is an invalid expression" % expression

            yield check

    def test_single_operands(self):
        """
        Expressions made up of a single operand must yield the expected operand.

        """
        operand_parser = self.parser.define_operand().parseString

        for expression, expected_operand in self.single_operands.items():

            # Making a Nose test generator:
            def check():
                node = operand_parser(expression, parseAll=True)
                eq_(1, len(node))
                expected_operand.check_equivalence(node[0])
            check.description = ('Single operand "%s" should return %s' %
                                 (expression, expected_operand))

            yield check

    def test_invalid_operands(self):
        """
        Expressions representing invalid operands must not yield a parse tree.

        """
        operand_parser = self.parser.define_operand().parseString
        for expression in self.invalid_operands:

            # Making a Nose test generator:
            @raises(ParseException)
            def check():
                operand_parser(expression, parseAll=True)
            check.description = ('"%s" is an invalid operand' %
                                 expression)

            yield check
