# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging

from booleano.operations.operands.constants import constants_symbol_table_builder
from booleano.operations.variables import variable_symbol_table_builder
from booleano.parser.core import EvaluableParseManager
from booleano.parser.grammar import Grammar

logger = logging.getLogger(__name__)


def get_boolean_evaluator(statment, variables=None, constants=None, grammar_tokens=None):
    """
    an fast and easy to use helper to build a parser with variables and constants.
    return a callable which take a dict of value (for the variables).

    the returning scope will cotains the variables as is, and the constants into the namespace ``const:``

    ie:  'age < const:majority & "o" in name & birthdate > "1983-02-02"'

    :param str statment: the statment to use
    :param list|tuple variables:  the sample of variables
    :param dict constants:  the value for the consts
    :param dict grammar_tokens: all extra parameters must be a valid grammar token replacements. (is_subset='in')
    :return: the parse tree that, if called, return a boolean result
    :rtype: :class:`booleano.parser.trees.ParseTree`
    """

    grammar_tokens = grammar_tokens or {}
    grammar = Grammar(**grammar_tokens)
    if variables is None:
        variables = [{}]

    root_table = variable_symbol_table_builder('root', variables[0])

    """:type: booleano.parser.scope.SymbolTable"""
    if constants:
        root_table.add_subtable(
            constants_symbol_table_builder('const', constants),
        )

    parse_manager = EvaluableParseManager(root_table, grammar)
    return parse_manager.parse(statment)


def eval_boolean(statment, variables=None, constants=None, grammar_tokens=None):
    """
    a slow but easy to use boolean evaluation helper.
    :param statment: the boolean statment to evaluate
    :param variables: the dict of variables
    :param constants: the dict of constants.
    :return: the Truth of the statment with the given variables
    :rtype: bool
    """
    return get_boolean_evaluator(statment, (variables or {},), constants, grammar_tokens)(variables)
