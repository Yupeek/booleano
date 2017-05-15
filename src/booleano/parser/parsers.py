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
Generic Pyparsing-based parser implementation.

"""

from __future__ import unicode_literals

import re

import six
import six.moves
from pyparsing import (CaselessLiteral, Combine, Forward, Group, Literal, OneOrMore, Optional, ParserElement, Regex,
                       StringEnd, StringStart, Suppress, Word, ZeroOrMore, delimitedList, nums, opAssoc,
                       operatorPrecedence, quotedString, removeQuotes)

from booleano.exc import BadExpressionError
from booleano.operations.operands.classes import Function
from booleano.operations.operands.constants import Number, Set, String
from booleano.operations.operands.placeholders import PlaceholderFunction, PlaceholderVariable
from booleano.operations.operators import (And, BelongsTo, Equal, GreaterEqual, GreaterThan, IsSubset, LessEqual,
                                           LessThan, Not, NotEqual, Or, Xor)
from booleano.parser.trees import ConvertibleParseTree, EvaluableParseTree

__all__ = ("EvaluableParser", "ConvertibleParser")

# Let's enable packrat. It could make parsing even 33810x faster!
ParserElement.enablePackrat()


class Parser(object):
    """
    Base class for parsers.

    """

    parse_tree_class = None

    def __init__(self, grammar):
        """

        :param grammar: The grammar used by the parser.
        :type grammar: :class:`booleano.parser.Grammar`

        """
        self._parser = None
        self._grammar = grammar

    def __call__(self, expression):
        """
        Parse ``expression`` and return its parse tree.

        :param expression: The expression to be parsed.
        :type expression: basestring
        :return: The parse tree.
        :rtype: ParseTree

        The parser will be built if it's not been built yet.

        """
        if not self._parser:
            self.build_parser()

        result = self._parser.parseString(expression, parseAll=True)
        root_node = result[0]
        return self.parse_tree_class(root_node)

    def build_parser(self):
        self._parser = (StringStart() + self.define_operation() + StringEnd())

    # Operand generators; used to create the grammar

    def define_operation(self):
        Suppress(self._grammar.get_token("group_start"))
        Suppress(self._grammar.get_token("group_end"))

        # Making the relational operations:
        t_eq = self._grammar.get_token("eq")
        t_ne = self._grammar.get_token("ne")
        t_lt = self._grammar.get_token("lt")
        t_gt = self._grammar.get_token("gt")
        t_le = self._grammar.get_token("le")
        t_ge = self._grammar.get_token("ge")
        eq = CaselessLiteral(t_eq)
        ne = CaselessLiteral(t_ne)
        lt = CaselessLiteral(t_lt)
        gt = CaselessLiteral(t_gt)
        le = CaselessLiteral(t_le)
        ge = CaselessLiteral(t_ge)
        relationals = eq ^ ne ^ le ^ ge ^ lt ^ gt
        # TODO: Avoid doing this:
        self.__relationals__ = {
            t_eq: Equal,
            t_ne: NotEqual,
            t_lt: LessThan,
            t_gt: GreaterThan,
            t_le: LessEqual,
            t_ge: GreaterEqual,
        }

        # Making the set-specific operations:
        t_belongs_to = self._grammar.get_token("belongs_to")
        t_is_subset = self._grammar.get_token("is_subset")
        belongs_to = CaselessLiteral(t_belongs_to)
        is_subset = CaselessLiteral(t_is_subset)
        membership = belongs_to ^ is_subset
        # TODO: Avoid doing this:
        self.__membership_operators__ = {
            t_belongs_to: BelongsTo,
            t_is_subset: IsSubset,
        }

        # Making the logical connectives:
        not_ = Suppress(self._grammar.get_token("not"))
        and_ = Suppress(self._grammar.get_token("and"))
        in_or = Suppress(self._grammar.get_token("or"))
        ex_or = Suppress(self._grammar.get_token("xor"))

        # Now let's prevent higher precedence operators from hiding those
        # operators with a lower precedence:
        relationals = ~membership + relationals

        operand = self.define_operand()

        operation = operatorPrecedence(
            operand,
            [
                (relationals, 2, opAssoc.LEFT, self.make_relational),
                (membership, 2, opAssoc.LEFT, self.make_membership),
                (not_, 1, opAssoc.RIGHT, self.make_not),
                (and_, 2, opAssoc.LEFT, self.make_and),
                (ex_or, 2, opAssoc.LEFT, self.make_xor),
                (in_or, 2, opAssoc.LEFT, self.make_or),
            ]
        )

        return operation

    def define_operand(self):
        """
        Return the syntax definition for an operand.

        An operand can be a variable, a string, a number or a set. A set
        is made of other operands, including other sets.

        **This method shouldn't be overridden**. Instead, override the syntax
        definitions for variables, strings and/or numbers.

        If you want to customize the sets, check :meth:`T_SET_START`,
        :meth:`T_SET_END` and :meth:`T_ELEMENT_SEPARATOR`.

        """
        identifier = self.define_identifier()
        operand = Forward()

        # Defining the sets:
        set_start = Suppress(self._grammar.get_token("set_start"))
        set_end = Suppress(self._grammar.get_token("set_end"))
        element_separator = self._grammar.get_token("element_separator")
        elements = delimitedList(operand, delim=element_separator)
        set_ = Group(set_start + Optional(elements) + set_end)
        set_.setParseAction(self.make_set)
        set_.setName("set")

        # Defining the variables:
        variable = identifier.copy()
        variable.setName("variable")
        variable.addParseAction(self.make_variable)

        # Defining the functions:
        function_name = identifier.setResultsName("function_name")
        function_name.setName("function_name")
        args_start = Suppress(self._grammar.get_token("arguments_start"))
        args_end = Suppress(self._grammar.get_token("arguments_end"))
        args_sep = self._grammar.get_token("arguments_separator")
        arguments = Optional(Group(delimitedList(operand, delim=args_sep)),
                             default=())
        arguments = arguments.setResultsName("arguments")
        arguments.setParseAction(lambda tokens: tokens[0])
        function = function_name + args_start + arguments + args_end
        function.setName("function")
        function.setParseAction(self.make_function)

        operand << (function | variable | self.define_number() |
                    self.define_string() | set_)

        return operand

    def define_string(self):
        """
        Return the syntax definition for a string.

        **Do not override this method**, it's not necessary: it already
        supports unicode strings. If you want to override the delimiters,
        check :attr:`T_QUOTES`.

        """
        string = quotedString.setParseAction(removeQuotes, self.make_string)
        string.setName("string")
        return string

    def define_number(self):
        """
        Return the syntax definition for a number in Arabic Numerals.

        Override this method to support numeral systems other than Arabic
        Numerals (0-9).

        Do not override this method just to change the character used to
        separate thousands and decimals: Use :attr:`T_THOUSANDS_SEPARATOR`
        and :attr:`T_DECIMAL_SEPARATOR`, respectively.

        """
        # Defining the basic tokens:

        def to_dot(t):
            return "."

        def to_plus(t):
            return "+"

        def to_minus(t):
            return "-"

        positive_sign = Literal(self._grammar.get_token("positive_sign"))
        positive_sign.setParseAction(to_plus)
        negative_sign = Literal(self._grammar.get_token("negative_sign"))
        negative_sign.setParseAction(to_minus)
        decimal_sep = Literal(self._grammar.get_token("decimal_separator"))
        decimal_sep.setParseAction(to_dot)
        thousands_sep = Suppress(self._grammar.get_token("thousands_separator"))
        digits = Word(nums)
        # Building the integers and decimals:
        sign = positive_sign | negative_sign
        thousands = Word(nums, max=3) + \
            OneOrMore(thousands_sep + Word(nums, exact=3))
        integers = thousands | digits
        decimals = decimal_sep + digits
        number = Combine(Optional(sign) + integers + Optional(decimals))
        number.setParseAction(self.make_number)
        number.setName("number")
        return number

    def define_identifier(self):
        """
        Return the syntax definition for an identifier.

        """
        # --- Defining the individual identifiers:
        # Getting all the Unicode numbers in a single string:
        unicode_numbers = "".join([six.unichr(n) for n in six.moves.range(0x10000)
                                   if six.unichr(n).isdigit()])
        unicode_number_expr = Regex("[%s]" % unicode_numbers, re.UNICODE)
        space_char = re.escape(self._grammar.get_token("identifier_spacing"))
        identifier0 = Regex("[\w%s]+" % space_char, re.UNICODE)
        # Identifiers cannot start with a number:
        identifier0 = Combine(~unicode_number_expr + identifier0)
        identifier0.setName("individual_identifier")

        # --- Defining the namespaces:
        namespace_sep = Suppress(self._grammar.get_token("namespace_separator"))
        namespace = Group(ZeroOrMore(identifier0 + namespace_sep))
        namespace.setName("namespace")

        # --- The full identifier, which could have a namespace:
        identifier = Combine(namespace.setResultsName("namespace_parts") +
                             identifier0.setResultsName("identifier"))
        identifier.setName("full_identifier")

        return identifier

    # Pyparsing post-parse actions

    def make_string(self, tokens):
        """Make a String constant using the token passed."""
        return String(tokens[0])

    def make_number(self, tokens):
        """Make a Number constant using the token passed."""
        return Number(tokens[0])

    def make_variable(self, tokens):
        """Make a variable using the tokens passed."""
        raise NotImplementedError("It's up to the actual parser to make "
                                  "the variables")

    def make_function(self, tokens):
        """Make a function using the tokens passed."""
        raise NotImplementedError("It's up to the actual parser to make "
                                  "the functions")

    def make_set(self, tokens):
        """Make a Set using the token passed."""
        return Set(*tokens[0])

    def make_relational(self, tokens):
        """Make a relational operation using the tokens passed."""
        left_op = tokens[0][0]
        operator = tokens[0][1]
        right_op = tokens[0][2]

        operation = self.__relationals__[operator]

        return operation(left_op, right_op)

    def make_membership(self, tokens):
        """
        Make a membership operation using the operands passed in ``tokens``.

        """
        element = tokens[0][0]
        operator = tokens[0][1]
        set_ = tokens[0][2]
        operation = self.__membership_operators__[operator]

        return operation(element, set_)

    def make_not(self, tokens):
        """Make an *Not* connective using the token passed."""
        return Not(tokens[0][0])

    def make_and(self, tokens):
        """Make an *And* connective using the tokens passed."""
        return self.__make_binary_connective__(And, tokens[0])

    def make_xor(self, tokens):
        """Make an *Xor* connective using the tokens passed."""
        return self.__make_binary_connective__(Xor, tokens[0])

    def make_or(self, tokens):
        """Make an *Or* connective using the tokens passed."""
        return self.__make_binary_connective__(Or, tokens[0])

    def __make_binary_connective__(self, operation_class, operands):
        """
        Return an operation represented by the binary connective
        ``operation_class`` and its ``operands``.

        """
        if len(operands) == 2:
            operation = operation_class(operands[0], operands[1])
        else:
            # We're going to build the operation from right to left, so it
            # can be evaluated from left to right (a LIFO approach).
            operation = operation_class(operands[-2], operands[-1])
            operands = operands[:-2]
            operands.reverse()
            for operand in operands:
                operation = operation_class(operand, operation)

        return operation

    #


class EvaluableParser(Parser):
    """
    Evaluable parser.

    """

    parse_tree_class = EvaluableParseTree

    def __init__(self, grammar, namespace):
        """

        :param grammar: The grammar used by the parser.
        :type grammar: :class:`booleano.parser.Grammar`
        :param namespace: The namespace that contains the objects used by the
            expressions to be parsed.
        :type namespace: :class:`booleano.parser.scope.Namespace`

        """
        self._namespace = namespace
        super(EvaluableParser, self).__init__(grammar)

    def make_variable(self, tokens):
        """
        Return the :class:`Variable` represented by the ``tokens`` passed.

        :return: The Booleano variable/constant represented in the ``tokens``.
        :rtype: Operand
        :raises ScopeError: If the variable's identifier is not found (including
            its parent namespace, if any).
        :raises BadExpressionError: If the identifier is found, but represents
            a function, not a variable.

        """
        var = self._namespace.get_object(tokens.identifier,
                                         tokens.namespace_parts)
        if isinstance(var, type) and issubclass(var, Function):
            orig_id = self.__get_original_identifier__(tokens)
            raise BadExpressionError(u'"%s" represents a function, not a '
                                     'variable' % orig_id)
        return var

    def make_function(self, tokens):
        """
        Return the :class:`Function` call represented by the ``tokens`` passed.

        :return: The Booleano function call represented in the ``tokens``.
        :rtype: Function
        :raises ScopeError: If the function name is not found (including its
            parent namespace, if any).
        :raises BadExpressionError: If the identifier is found, but represents
            a variable or constant, not a function call.

        """
        func_name = tokens.function_name
        func = self._namespace.get_object(func_name.identifier,
                                          func_name.namespace_parts)
        if not (isinstance(func, type) and issubclass(func, Function)):
            orig_id = self.__get_original_identifier__(func_name)
            raise BadExpressionError(u'"%s" is not a function' % orig_id)
        function_call = func(*tokens.arguments)
        return function_call

    def __get_original_identifier__(self, tokens):
        """Build the original identifier from a Pyparsing ``tokens``."""
        ns_sep = six.text_type(self._grammar.get_token("namespace_separator"))
        id_parts = list(tokens.namespace_parts) + [tokens.identifier]
        id_ = ns_sep.join(id_parts)
        return id_


class ConvertibleParser(Parser):
    """
    Convertible parser.

    """

    parse_tree_class = ConvertibleParseTree

    def make_variable(self, tokens):
        """Make a Placeholder variable using the token passed."""
        return PlaceholderVariable(tokens.identifier, tokens.namespace_parts)

    def make_function(self, tokens):
        """Make a Placeholder function using the token passed."""
        function = tokens.function_name
        return PlaceholderFunction(function.identifier,
                                   function.namespace_parts,
                                   *tokens.arguments)
