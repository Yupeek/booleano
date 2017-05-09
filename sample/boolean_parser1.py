#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

from booleano.operations.operands.constants import Number
from booleano.operations.variables import NumberVariable, StringVariable, DateVariable, SetVariable
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


# 1: create a static Symbol Table
root_table = SymbolTable(
    "root",
    (
        # variablet taken from context
        Bind("age", NumberVariable('age')),
        Bind("name", StringVariable('name')),
        Bind("birthdate", DateVariable("birthdate")),
        Bind("tags", SetVariable("tags")),
        # constants
        Bind("majority", Number(18)),
    )
)


# 2: create the parser with se symbol table and the grammar (customized)
parse_manager = EvaluableParseManager(root_table, Grammar(belongs_to='in'))
# 3: compile a expression
compiled_expression = parse_manager.parse('age < majority & "o" in name & birthdate > "1983-02-02"')

for character in sample:
    # 4 execute the cumpiled expression with a context
    print("%s => %s" % (character, compiled_expression(character)))
