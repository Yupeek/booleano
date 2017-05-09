#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import datetime

import sys

import pyparsing

from booleano.operations.operands.constants import Number, constants_symbol_table_builder
from booleano.operations.variables import NumberVariable, StringVariable, DateVariable, SetVariable, \
    variable_symbol_table_builder
from booleano.parser.scope import SymbolTable, Bind

from booleano.parser import Grammar
from booleano.parser.core import EvaluableParseManager

# our sample data to test. matching the SymbolTable
sample = [
    {"name": "katara", "age": 14, "birthdate": datetime.date(1985, 1, 1)},
    {"name": "aang", "age": 112, "birthdate": datetime.date(1888, 1, 1)},
    {"name": "zuko", "age": 16, "birthdate": datetime.date(1983, 1, 1)},
    {"name": "sokka", "age": 15, "birthdate": datetime.date(1984, 1, 1)},
]

consts = {
    'majority': 18,
    'very old': 99
}

# 1: create a static Symbol Table
# this variable use the VariableSymbolTableBuilder to build a symbol table from variables and consts
root_table = SymbolTable(
    'root',
    [],
    variable_symbol_table_builder('var', sample[0]),
    constants_symbol_table_builder('const', consts)
)

# 2: create the parser with se symbol table and the grammar (customized)

grammar = Grammar(belongs_to='in')
parse_manager = EvaluableParseManager(root_table, grammar)
# 3: compile a expression

# check the command line args
if len(sys.argv) == 1:
    stmt = 'var:age < const:majority & "o" in var:name & var:birthdate > "1983-02-02"'
    print("try something like %s '%s'" % (sys.argv[0], stmt))

else:
    stmt = " ".join(sys.argv[1:])

print("searching with expression %r" % stmt)
try:
    compiled_expression = parse_manager.parse(stmt)
except pyparsing.ParseException as e:
    attrs = dict(
        expr=stmt,
        e=e,
        tild='^',
        grammar="\n".join("%s => '%s'" % (k, v) for k, v in grammar.get_all_tokens().items())
    )
    msg = "error while parsing the expression {expr} at {e.lineno}:{e.col}: {e}\n" \
          "{e.line}\n" \
          "{tild:->{e.col}}\n" \
          " valid grammar : {grammar}".format(**attrs)
    print(msg)
    exit(2)
else:
    # run the rule for all sample data
    for character in sample:
        res = compiled_expression(character)
        code = '32' if res else '31'
        print('\033[%sm%r\x1b[0m' % (code, character))
