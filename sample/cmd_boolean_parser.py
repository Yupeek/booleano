#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import datetime

import sys

import pyparsing

from booleano.operations.operands.constants import Number
from booleano.operations.variables import IntegerVariable, StringVariable, DateVariable, SetVariable
from booleano.parser.scope import SymbolTable, Bind

from booleano.parser import Grammar, EvaluableParseManager

# our sample data to test. matching the SymbolTable
sample = [
    {"name": "katara", "age": 14, "birthdate": datetime.date(1985, 1, 1)},
    {"name": "aang", "age": 112, "birthdate": datetime.date(1888, 1, 1)},
    {"name": "zuko", "age": 16, "birthdate": datetime.date(1983, 1, 1)},
    {"name": "sokka", "age": 15, "birthdate": datetime.date(1984, 1, 1)},
]

# 1: create a static Symbol Table
root_table = SymbolTable(
    "root",
    (
        # variablet taken from context
        Bind("age", IntegerVariable('age')),
        Bind("name", StringVariable('name')),
        Bind("birthdate", DateVariable("birthdate")),
        Bind("tags", SetVariable("tags")),
        # constants
        Bind("majority", Number(18)),
    )
)

# 2: create the parser with se symbol table and the grammar (customized)

grammar = Grammar(belongs_to='in')
parse_manager = EvaluableParseManager(root_table, grammar)
# 3: compile a expression
compiled_expression = parse_manager.parse('age < majority & "o" in name & birthdate > "1983-02-02"')

# check the command line args
if len(sys.argv) == 1:
    print("try something like %s '\"a\" in name'" % sys.argv[0])
    exit(1)

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
