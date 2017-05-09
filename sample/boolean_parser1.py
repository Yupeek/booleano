#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from booleano.operations.operands.constants import Number
from booleano.parser.core import EvaluableParseManager
from booleano.parser.grammar import Grammar

from booleano.operations.variables import NumberVariable, StringVariable, DurationVariable, SetVariable
from booleano.parser.scope import SymbolTable, Bind

name = StringVariable("name")

symbols = SymbolTable(
    'my_table',
    [
        Bind('character', name),
    ],
    SymbolTable('character', [
        Bind('age', NumberVariable('age')),
        Bind('name', name),
        Bind('training', DurationVariable('training')),
        Bind('bending', SetVariable('bending')),
    ]),
    SymbolTable('consts', [
        Bind('majority', Number(18)),
    ])
)

grammar = Grammar(**{'and': 'and', 'or': 'or', 'belongs_to': 'in'})


# 2: create the parser with se symbol table and the grammar (customized)
parse_manager = EvaluableParseManager(symbols, grammar)
# 3: compile a expression
compiled_expression = parse_manager.parse(
    'character:age < consts:majority and '
    '"a" in character and '
    '('
    '    {"water"} in character:bending or '
    '    character:training > "3d4h"'
    ')'
)

sample = [
    {"name": "katara", "age": 14, "training": datetime.timedelta(days=24), "bending": {'water'}},
    {"name": "aang", "age": 112, "training": datetime.timedelta(days=6*365), "bending": {'water', 'earth', 'fire', 'air'}},
    {"name": "zuko", "age": 16, "training": datetime.timedelta(days=29), "bending": {'fire'}},
    {"name": "sokka", "age": 15, "training": datetime.timedelta(days=0), "bending": set()},
]

for character in sample:
    # 4 execute the cumpiled expression with a context
    print("%s => %s" % (character, compiled_expression(character)))
