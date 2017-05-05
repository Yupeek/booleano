# -*- coding: utf-8 -*-
#
# Copyright (c) 2009 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano/>.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, distribute with
# modifications, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written authorization.
"""
Test suite for the built-in parser implementation.

"""
from __future__ import unicode_literals

from nose.tools import eq_, assert_raises
import six

from booleano.operations.variables import BooleanVariable
from booleano.parser import Grammar, ConvertibleParser, EvaluableParser
from booleano.parser.scope import Namespace
from booleano.parser.parsers import Parser
from booleano.operations import (Not, And, Or, Xor, Equal, NotEqual, LessThan,
    GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset, String, Number,
    Set, Variable, Function, PlaceholderVariable, PlaceholderFunction)
from booleano.parser.testutils import BaseGrammarTest
from booleano.exc import ScopeError, BadExpressionError

from tests import (StringConverter, BoolVar, TrafficLightVar,
                   PedestriansCrossingRoad, DriversAwaitingGreenLightVar,
                   PermissiveFunction, TrafficViolationFunc)


class TestDefaultGrammar(BaseGrammarTest):
    """
    Tests for the parser of the default/generic grammar.
    
    """

    grammar = Grammar()

    expressions = {
        # Literals-only expressions:
        '  "a string" == 245    ': Equal(String("a string"), Number(245)),
        '   2 > 5   ': GreaterThan(Number(2), Number(5)),
        # Identifiers-only expressions:
        '  today > yesterday ': GreaterThan(PlaceholderVariable("today"),
                                            PlaceholderVariable("yesterday")),
        'time:today > time:yesterday ': GreaterThan(
            PlaceholderVariable("today", ("time", )),
            PlaceholderVariable("yesterday", ("time", ))),
        # Literals + non-literal expressions:
        'today > "1999-06-01"': GreaterThan(PlaceholderVariable("today"),
                                            String("1999-06-01")),
        'get_parents("Gustavo") == {"Liliana", "Carlos"}': Equal(
            PlaceholderFunction("get_parents", None, String("Gustavo")),
            Set(String("Liliana"), String("Carlos"))
            ),
        # Set-specific operations:
        u'"hi" ∈ {"hi", "bye"}': BelongsTo(
            String("hi"),
            Set(String("hi"), String("bye"))
            ),
        u'salutation ∈ {"hi", "bye"}': BelongsTo(
            PlaceholderVariable("salutation"),
            Set(String("hi"), String("bye"))
            ),
        u'"good morning" ∈ salutations': BelongsTo(
            String("good morning"),
            PlaceholderVariable("salutations")
            ),
        u'relatives:sister ∈ relatives:siblings': BelongsTo(
            PlaceholderVariable("sister", ("relatives", )),
            PlaceholderVariable("siblings", ("relatives", ))
            ),
        u'{"hi", "bye"} ⊂ {"hello", "hi", "bye"}': IsSubset(
            Set(String("hi"), String("bye")),
            Set(String("hello"), String("hi"), String("bye"))
            ),
        u'salutations ⊂ {"morning", "hi", "bye", "later"}': IsSubset(
            PlaceholderVariable("salutations"),
            Set(String("morning"), String("hi"), String("bye"), String("later"))
            ),
        u'{"hi", "bye"} ⊂ salutations': IsSubset(
            Set(String("hi"), String("bye")),
            PlaceholderVariable("salutations")
            ),
        u'relatives:siblings ⊂ relatives:everyone': IsSubset(
            PlaceholderVariable("siblings", ("relatives", )),
            PlaceholderVariable("everyone", ("relatives", ))
            ),
        # Relational operations:
        'now == today:time': Equal(PlaceholderVariable("now"),
                                   PlaceholderVariable("time", ("today", ))),
        '3.1416 == Pi': Equal(Number(3.1416), PlaceholderVariable("pi")),
        'Pi == 3.1416': Equal(PlaceholderVariable("pi"), Number(3.1416)),
        'days:today != days:yesterday': NotEqual(
            PlaceholderVariable("today", ("days",)),
            PlaceholderVariable("yesterday", ("days",))),
        '3.00 != Pi': NotEqual(Number(3.0), PlaceholderVariable("pi")),
        'Pi != 3.00': Equal(PlaceholderVariable("pi"), Number(3.00)),
        'days:today > days:yesterday': GreaterThan(
            PlaceholderVariable("today", ("days",)),
            PlaceholderVariable("yesterday", ("days",))),
        '3.00 > Pi': GreaterThan(Number(3.0), PlaceholderVariable("pi")),
        'Pi > 3.00': GreaterThan(PlaceholderVariable("pi"), Number(3.00)),
        'days:today < days:yesterday': LessThan(
            PlaceholderVariable("today", ("days",)),
            PlaceholderVariable("yesterday", ("days",))),
        '3.00 < Pi': LessThan(Number(3.0), PlaceholderVariable("pi")),
        'Pi < 3.00': LessThan(PlaceholderVariable("pi"), Number(3.00)),
        'days:today >= days:yesterday': GreaterEqual(
            PlaceholderVariable("today", ("days",)),
            PlaceholderVariable("yesterday", ("days",))),
        '3.00 >= Pi': GreaterEqual(Number(3.0), PlaceholderVariable("pi")),
        'Pi >= 3.00': GreaterEqual(PlaceholderVariable("pi"), Number(3.00)),
        'days:today <= days:yesterday': LessEqual(
            PlaceholderVariable("today", ("days",)),
            PlaceholderVariable("yesterday", ("days",))),
        '3.00 <= Pi': LessEqual(Number(3.0), PlaceholderVariable("pi")),
        'Pi <= 3.00': LessEqual(PlaceholderVariable("pi"), Number(3.00)),
        # Logical connectives:
        '~today_will_rain()': Not(PlaceholderFunction("today_will_rain")),
        '~(today_will_rain())': Not(PlaceholderFunction("today_will_rain")),
        '~ today_will_rain()': Not(PlaceholderFunction("today_will_rain")),
        '~~today_will_rain()': Not(Not(PlaceholderFunction("today_will_rain"))),
        '~ today_is_friday': Not(PlaceholderVariable("today_is_friday")),
        '~ time:days:today > "1999-06-01"': Not(
            GreaterThan(
                  PlaceholderVariable("today", ("time", "days")),
                  String("1999-06-01")
                  )
            ),
        '~ (time:days:today > "1999-06-01")': Not(
            GreaterThan(
                  PlaceholderVariable("today", ("time", "days")),
                  String("1999-06-01")
                  )
            ),
        '~ today_is_friday & today_will_rain': And(
            Not(PlaceholderVariable("today_is_friday")),
            PlaceholderVariable("today_will_rain")
            ),
        '~ today_is_friday & ~ today_will_rain': And(
            Not(PlaceholderVariable("today_is_friday")),
            Not(PlaceholderVariable("today_will_rain"))
            ),
        'today_is_friday & ~ today_will_rain': And(
            PlaceholderVariable("today_is_friday"),
            Not(PlaceholderVariable("today_will_rain"))
            ),
        '~ (today_is_friday & today_will_rain)': Not(And(
            PlaceholderVariable("today_is_friday"),
            PlaceholderVariable("today_will_rain")
            )),
        '~ X > 3 & Z < X': And(
            Not(GreaterThan(PlaceholderVariable("X"), Number(3))),
            LessThan(PlaceholderVariable("Z"), PlaceholderVariable("X"))
            ),
        '~ X > 3 & ~ Z < X': And(
            Not(GreaterThan(PlaceholderVariable("X"), Number(3))),
            Not(LessThan(PlaceholderVariable("Z"), PlaceholderVariable("X")))
            ),
        'X > 3 & ~ Z < X': And(
            GreaterThan(PlaceholderVariable("X"), Number(3)),
            Not(LessThan(PlaceholderVariable("Z"), PlaceholderVariable("X")))
            ),
        '~ (X > 3 & Z < X)': Not(And(
            GreaterThan(PlaceholderVariable("X"), Number(3)),
            LessThan(PlaceholderVariable("Z"), PlaceholderVariable("X"))
            )),
        '~ (X > 3 ^ Z < X)': Not(Xor(
            GreaterThan(PlaceholderVariable("X"), Number(3)),
            LessThan(PlaceholderVariable("Z"), PlaceholderVariable("X"))
            )),
        '~ (X > 3 | Z < X)': Not(Or(
            GreaterThan(PlaceholderVariable("X"), Number(3)),
            LessThan(PlaceholderVariable("Z"), PlaceholderVariable("X"))
            )),
        'today_will_rain() & Pi > 3.0': And(
            PlaceholderFunction("today_will_rain"),
            GreaterThan(PlaceholderVariable("Pi"), Number(3.0))
            ),
        'weather:today_rains & Pi > e & today_is_monday()': And(
            PlaceholderVariable("today_rains", ("weather", )),
            And(
                GreaterThan(PlaceholderVariable("Pi"), PlaceholderVariable("e")),
                PlaceholderFunction("today_is_monday")
                )
            ),
        'weather:today_rains & (Pi > e & today_is_monday())': And(
            PlaceholderVariable("today_rains", ("weather", )),
            And(
                GreaterThan(PlaceholderVariable("Pi"), PlaceholderVariable("e")),
                PlaceholderFunction("today_is_monday")
                )
            ),
        '(weather:today_rains & Pi > e) & today_is_monday()': And(
            And(
                PlaceholderVariable("today_rains", ("weather", )),
                GreaterThan(PlaceholderVariable("Pi"), PlaceholderVariable("e"))
                ),
            PlaceholderFunction("today_is_monday")
            ),
        'today_will_rain() ^ Pi > 3.0': Xor(
            PlaceholderFunction("today_will_rain"),
            GreaterThan(PlaceholderVariable("Pi"), Number(3.0))
            ),
        'weather:today_rains ^ Pi > e ^ today_is_monday()': Xor(
            PlaceholderVariable("today_rains", ("weather", )),
            Xor(
                GreaterThan(PlaceholderVariable("Pi"), PlaceholderVariable("e")),
                PlaceholderFunction("today_is_monday")
                )
            ),
        'weather:today_rains ^ (Pi > e ^ today_is_monday())': Xor(
            PlaceholderVariable("today_rains", ("weather", )),
            Xor(
                GreaterThan(PlaceholderVariable("Pi"), PlaceholderVariable("e")),
                PlaceholderFunction("today_is_monday")
                )
            ),
        '(weather:today_rains ^ Pi > e) ^ today_is_monday()': Xor(
            Xor(
                PlaceholderVariable("today_rains", ("weather", )),
                GreaterThan(PlaceholderVariable("Pi"), PlaceholderVariable("e"))
                ),
            PlaceholderFunction("today_is_monday")
            ),
        'today_will_rain() | Pi > 3.0': Or(
            PlaceholderFunction("today_will_rain"),
            GreaterThan(PlaceholderVariable("Pi"), Number(3.0))
            ),
        'weather:today_rains | Pi > e | today_is_monday()': Or(
            PlaceholderVariable("today_rains", ("weather", )),
            Or(
                GreaterThan(PlaceholderVariable("Pi"), PlaceholderVariable("e")),
                PlaceholderFunction("today_is_monday")
                )
            ),
        'weather:today_rains | (Pi > e | today_is_monday())': Or(
            PlaceholderVariable("today_rains", ("weather", )),
            Or(
                GreaterThan(PlaceholderVariable("Pi"), PlaceholderVariable("e")),
                PlaceholderFunction("today_is_monday")
                )
            ),
        '(weather:today_rains | Pi > e) | today_is_monday()': Or(
            Or(
                PlaceholderVariable("today_rains", ("weather", )),
                GreaterThan(PlaceholderVariable("Pi"), PlaceholderVariable("e"))
                ),
            PlaceholderFunction("today_is_monday")
            ),
        # Checking operator precedence rules:
        'today == "monday" & yesterday != "sunday" ^ Y > 0': Xor(
            And(
                Equal(PlaceholderVariable("today"), String("monday")),
                NotEqual(PlaceholderVariable("yesterday"), String("sunday"))
                ),
            GreaterThan(PlaceholderVariable("Y"), Number(0))
            ),
        '(today == "monday" & yesterday != "sunday") ^ Y > 0': Xor(
            And(
                Equal(PlaceholderVariable("today"), String("monday")),
                NotEqual(PlaceholderVariable("yesterday"), String("sunday"))
                ),
            GreaterThan(PlaceholderVariable("Y"), Number(0))
            ),
        'today == "monday" & (yesterday != "sunday" ^ Y > 0)': And(
            Equal(PlaceholderVariable("today"), String("monday")),
            Xor(
                NotEqual(PlaceholderVariable("yesterday"), String("sunday")),
                GreaterThan(PlaceholderVariable("Y"), Number(0))
                ),
            ),
        'today == "monday" ^ yesterday != "sunday" & Y > 0': Xor(
            Equal(PlaceholderVariable("today"), String("monday")),
            And(
                NotEqual(PlaceholderVariable("yesterday"), String("sunday")),
                GreaterThan(PlaceholderVariable("Y"), Number(0))
                ),
            ),
        'today == "monday" ^ (yesterday != "sunday" & Y > 0)': Xor(
            Equal(PlaceholderVariable("today"), String("monday")),
            And(
                NotEqual(PlaceholderVariable("yesterday"), String("sunday")),
                GreaterThan(PlaceholderVariable("Y"), Number(0))
                ),
            ),
        '(today == "monday" ^ yesterday != "sunday") & Y > 0': And(
            Xor(
                Equal(PlaceholderVariable("today"), String("monday")),
                NotEqual(PlaceholderVariable("yesterday"), String("sunday"))
                ),
            GreaterThan(PlaceholderVariable("Y"), Number(0))
            ),
        'today == "monday" & yesterday != "sunday" | Y > 0': Or(
            And(
                Equal(PlaceholderVariable("today"), String("monday")),
                NotEqual(PlaceholderVariable("yesterday"), String("sunday"))
                ),
            GreaterThan(PlaceholderVariable("Y"), Number(0))
            ),
        '(today == "monday" & yesterday != "sunday") | Y > 0': Or(
            And(
                Equal(PlaceholderVariable("today"), String("monday")),
                NotEqual(PlaceholderVariable("yesterday"), String("sunday"))
                ),
            GreaterThan(PlaceholderVariable("Y"), Number(0))
            ),
        'today == "monday" & (yesterday != "sunday" | Y > 0)': And(
            Equal(PlaceholderVariable("today"), String("monday")),
            Or(
                NotEqual(PlaceholderVariable("yesterday"), String("sunday")),
                GreaterThan(PlaceholderVariable("Y"), Number(0))
                ),
            ),
        'today == "monday" | yesterday != "sunday" & Y > 0': Or(
            Equal(PlaceholderVariable("today"), String("monday")),
            And(
                NotEqual(PlaceholderVariable("yesterday"), String("sunday")),
                GreaterThan(PlaceholderVariable("Y"), Number(0))
                ),
            ),
        'today == "monday" | (yesterday != "sunday" & Y > 0)': Or(
            Equal(PlaceholderVariable("today"), String("monday")),
            And(
                NotEqual(PlaceholderVariable("yesterday"), String("sunday")),
                GreaterThan(PlaceholderVariable("Y"), Number(0))
                ),
            ),
        '(today == "monday" | yesterday != "sunday") & Y > 0': And(
            Or(
                Equal(PlaceholderVariable("today"), String("monday")),
                NotEqual(PlaceholderVariable("yesterday"), String("sunday"))
                ),
            GreaterThan(PlaceholderVariable("Y"), Number(0))
            ),
        'today == "monday" ^ yesterday != "sunday" | Y > 0': Or(
            Xor(
                Equal(PlaceholderVariable("today"), String("monday")),
                NotEqual(PlaceholderVariable("yesterday"), String("sunday"))
                ),
            GreaterThan(PlaceholderVariable("Y"), Number(0))
            ),
        '(today == "monday" ^ yesterday != "sunday") | Y > 0': Or(
            Xor(
                Equal(PlaceholderVariable("today"), String("monday")),
                NotEqual(PlaceholderVariable("yesterday"), String("sunday"))
                ),
            GreaterThan(PlaceholderVariable("Y"), Number(0))
            ),
        'today == "monday" ^ (yesterday != "sunday" | Y > 0)': Xor(
            Equal(PlaceholderVariable("today"), String("monday")),
            Or(
                NotEqual(PlaceholderVariable("yesterday"), String("sunday")),
                GreaterThan(PlaceholderVariable("Y"), Number(0))
                ),
            ),
        'today == "monday" | yesterday != "sunday" ^ Y > 0': Or(
            Equal(PlaceholderVariable("today"), String("monday")),
            Xor(
                NotEqual(PlaceholderVariable("yesterday"), String("sunday")),
                GreaterThan(PlaceholderVariable("Y"), Number(0))
                ),
            ),
        'today == "monday" | (yesterday != "sunday" ^ Y > 0)': Or(
            Equal(PlaceholderVariable("today"), String("monday")),
            Xor(
                NotEqual(PlaceholderVariable("yesterday"), String("sunday")),
                GreaterThan(PlaceholderVariable("Y"), Number(0))
                ),
            ),
        '(today == "monday" | yesterday != "sunday") ^ Y > 0': Xor(
            Or(
                Equal(PlaceholderVariable("today"), String("monday")),
                NotEqual(PlaceholderVariable("yesterday"), String("sunday"))
                ),
            GreaterThan(PlaceholderVariable("Y"), Number(0))
            ),
        'W == 0   &   X != 1   ^   Y > 2   |   Z < 3': Or(
            Xor(
                And(
                    Equal(PlaceholderVariable("W"), Number(0)),
                    NotEqual(PlaceholderVariable("X"), Number(1))
                    ),
                GreaterThan(PlaceholderVariable("Y"), Number(2))
                ),
            LessThan(PlaceholderVariable("Z"), Number(3))
            ),
        'W == 0   |   X != 1   ^   Y > 2   &   Z < 3': Or(
            Equal(PlaceholderVariable("W"), Number(0)),
            Xor(
                NotEqual(PlaceholderVariable("X"), Number(1)),
                And(
                    GreaterThan(PlaceholderVariable("Y"), Number(2)),
                    LessThan(PlaceholderVariable("Z"), Number(3))
                    ),
                ),
            ),
        'W == 0   |   (X != 1   ^   (Y > 2   &   Z < 3))': Or(
            Equal(PlaceholderVariable("W"), Number(0)),
            Xor(
                NotEqual(PlaceholderVariable("X"), Number(1)),
                And(
                    GreaterThan(PlaceholderVariable("Y"), Number(2)),
                    LessThan(PlaceholderVariable("Z"), Number(3))
                    ),
                ),
            ),
        '(W == 0   |   X != 1)   ^   (Y > 2   &   Z < 3)': Xor(
            Or(
               Equal(PlaceholderVariable("W"), Number(0)),
               NotEqual(PlaceholderVariable("X"), Number(1))
               ),
            And(
                GreaterThan(PlaceholderVariable("Y"), Number(2)),
                LessThan(PlaceholderVariable("Z"), Number(3))
                )
            ),
        '(W == 0   |   X != 1   ^   Y > 2)   &   Z < 3': And(
            Or(
               Equal(PlaceholderVariable("W"), Number(0)),
               Xor(
                   NotEqual(PlaceholderVariable("X"), Number(1)),
                   GreaterThan(PlaceholderVariable("Y"), Number(2)),
                   )
               ),
            LessThan(PlaceholderVariable("Z"), Number(3))
            ),
        '((W == 0   |   X != 1)   ^   Y > 2)   &   Z < 3': And(
            Xor(
                Or(
                   Equal(PlaceholderVariable("W"), Number(0)),
                   NotEqual(PlaceholderVariable("X"), Number(1))
                   ),
                GreaterThan(PlaceholderVariable("Y"), Number(2))
                ),
            LessThan(PlaceholderVariable("Z"), Number(3))
            ),
        '(W == 0   |   (X != 1   ^   Y > 2))   &   Z < 3': And(
            Or(
                Equal(PlaceholderVariable("W"), Number(0)),
                Xor(
                   NotEqual(PlaceholderVariable("X"), Number(1)),
                   GreaterThan(PlaceholderVariable("Y"), Number(2))
                   )
                ),
            LessThan(PlaceholderVariable("Z"), Number(3))
            ),
        'W == 0   |   (X != 1   ^   Y > 2   &   Z < 3)': Or(
            Equal(PlaceholderVariable("W"), Number(0)),
            Xor(
                NotEqual(PlaceholderVariable("X"), Number(1)),
                And(
                    GreaterThan(PlaceholderVariable("Y"), Number(2)),
                    LessThan(PlaceholderVariable("Z"), Number(3))
                    )
                )
            ),
        'W == 0   |   (X != 1   ^   (Y > 2   &   Z < 3))': Or(
            Equal(PlaceholderVariable("W"), Number(0)),
            Xor(
                NotEqual(PlaceholderVariable("X"), Number(1)),
                And(
                    GreaterThan(PlaceholderVariable("Y"), Number(2)),
                    LessThan(PlaceholderVariable("Z"), Number(3))
                    )
                )
            ),
        'W == 0   |   ((X != 1   ^   Y > 2)   &   Z < 3)': Or(
            Equal(PlaceholderVariable("W"), Number(0)),
            And(
                Xor(
                    NotEqual(PlaceholderVariable("X"), Number(1)),
                    GreaterThan(PlaceholderVariable("Y"), Number(2)),
                    ),
                LessThan(PlaceholderVariable("Z"), Number(3))
                )
            ),
        # Let's make sure whitespace doesn't change anything:
        '''
        
        variable == "hi"
        
        ''': Equal(PlaceholderVariable("variable"), String("hi")),
        '''
        
        variable 
        == 
        
        "hi"
        
        ''': Equal(PlaceholderVariable("variable"), String("hi")),
        '''
        \t variable == "hi"
        &
        \t today_is_thursday()
        ''': And(
                 Equal(PlaceholderVariable("variable"), String("hi")),
                 PlaceholderFunction("today_is_thursday")
            ),
    }

    badformed_expressions = (
        "",
        " ",
        "\t",
        "\n",
        "\r",
        "== 3 4",
        "3 4 ==",
        )

    single_operands = {
        # ----- Strings
        '"oneword"': String("oneword"),
        '"double quotes"': String("double quotes"),
        "'single quotes'": String("single quotes"),
        "''": String(""),
        '""': String(""),
        "'something with \"quotes\"'": String('something with "quotes"'),
        '"something with \'quotes\'"': String("something with 'quotes'"),
        u'"áéíóúñçÁÉÍÓÚÑÇ"': String(u"áéíóúñçÁÉÍÓÚÑÇ"),
        u'"海納百川，有容乃大"': String(u"海納百川，有容乃大"),
        u"'مقالة مختارة'": String(u"مقالة مختارة"),
        u'"вільної енциклопедії"': String(u"вільної енциклопедії"),
        # ----- Numbers
        '1': Number(1),
        '01': Number(1),
        '5000': Number(5000),
        '+3': Number(3),
        '-3': Number(-3),
        '2.34': Number(2.34),
        '2.2': Number(2.2),
        '+3.1416': Number(3.1416),
        '-3.1416': Number(-3.1416),
        '5,000': Number(5000),
        '1,000,000.34': Number(1000000.34),
        '+1,000,000.22': Number(1000000.22),
        '-1,000,000.22': Number(-1000000.22),
        # ----- Sets:
        ' {} ': Set(),
        '{{}, {}}': Set(Set(), Set()),
        '{1,000, 3.05}': Set(Number(1000), Number(3.05)),
        '{1,234,567}': Set(Number(1234567)),
        '{23,24,25}': Set(Number(23), Number(24), Number(25)),
        '{100, 200, 300}': Set(Number(100), Number(200), Number(300)),
        '{1, 2, {"orange", "apple"}, 3}': Set(
            Number(1),
            Number(2),
            Number(3),
            Set(String("orange"), String("apple"))
            ),
        u'{"españa", {"caracas", {"las chimeneas", "el trigal"}}, "france"}': \
            Set(
                String(u"españa"),
                String("france"),
                Set(
                    String("caracas"),
                    Set(String("el trigal"), String("las chimeneas"))
                ),
            ),
        '{var1, var2}': Set(PlaceholderVariable("var1"),
                            PlaceholderVariable("var2")),
        '{var, "string"}': Set(PlaceholderVariable("var"), String("string")),
        '{3, var, "string"}': Set(Number(3), String("string"),
                                  PlaceholderVariable("var")),
        '{varA, funcB()}': Set(PlaceholderVariable("varA"),
                               PlaceholderFunction("funcB")),
        '{"hi", 3.1416, len({1, 2, 3, 5, 7}), var0}': Set(
            String("hi"),
            Number(3.1416),
            PlaceholderFunction("len", (), Set(
                Number(1), Number(2), Number(3), Number(5), Number(7))),
            PlaceholderVariable("var0")
            ),
        # ----- Variables:
        'today': PlaceholderVariable("today"),
        'camelCase': PlaceholderVariable("camelCase"),
        'with_underscore': PlaceholderVariable("with_underscore"),
        ' v1 ': PlaceholderVariable("v1"),
        'var1_here': PlaceholderVariable("var1_here"),
        u'résumé': PlaceholderVariable(u"résumé"),
        u'有容乃大': PlaceholderVariable(u"有容乃大"),
        '    spaces': PlaceholderVariable("spaces"),
        'spaces    ': PlaceholderVariable("spaces"),
        '  spaces  ': PlaceholderVariable("spaces"),
        '_protected_var': PlaceholderVariable("_protected_var"),
        '__private_var': PlaceholderVariable("__private_var"),
        'one_underscore': PlaceholderVariable("one_underscore"),
        'two__underscores__here': PlaceholderVariable("two__underscores__here"),
        'case_insensitive_var': PlaceholderVariable("CASE_INSENSITIVE_VAR"),
        'CASE_INSENSITIVE_VAR': PlaceholderVariable("case_insensitive_var"),
        'cAsE_iNsEnSiTiVe_VaR': PlaceholderVariable("CaSe_InSeNsItIvE_vAr"),
        u'MAYÚSCULA_minúscula': PlaceholderVariable(u"mayúscula_MINÚSCULA"),
        'ns:variable': PlaceholderVariable("variable", ("ns", )),
        'ns0:ns1:variable': PlaceholderVariable("variable", ("ns0", "ns1")),
        'ns0:ns1:ns2:variable': PlaceholderVariable("variable",
                                                    ("ns0", "ns1", "ns2")),
        'ns:sub_ns:variable': PlaceholderVariable("variable", ("ns", "sub_ns")),
        u'ñŝ0:ñŝ1:variable': PlaceholderVariable("variable", (u"ñŝ0", u"ñŝ1")),
        # ----- Functions:
        'stop()': PlaceholderFunction("stop"),
        'stop ()': PlaceholderFunction("stop"),
        'stop( )': PlaceholderFunction("stop"),
        'stop ( )': PlaceholderFunction("stop"),
        'camelCase()': PlaceholderFunction("camelCase"),
        'with_underscore()': PlaceholderFunction("with_underscore"),
        ' v1() ': PlaceholderFunction("v1"),
        'var1_here()': PlaceholderFunction("var1_here"),
        u'résumé()': PlaceholderFunction(u"résumé"),
        u'有容乃大()': PlaceholderFunction(u"有容乃大"),
        '    spaces()': PlaceholderFunction("spaces"),
        'spaces()    ': PlaceholderFunction("spaces"),
        '  spaces()  ': PlaceholderFunction("spaces"),
        '_protected_function()': PlaceholderFunction("_protected_function"),
        '__private_function()': PlaceholderFunction("__private_function"),
        'one_underscore()': PlaceholderFunction("one_underscore"),
        'two__underscores__()': PlaceholderFunction("two__underscores__"),
        'case_insensitive_func()': PlaceholderFunction("CASE_INSENSITIVE_FUNC"),
        'CASE_INSENSITIVE_FUNC()': PlaceholderFunction("case_insensitive_func"),
        'cAsE_iNsEnSiTiVe_FuNc()': PlaceholderFunction("CaSe_InSeNsItIvE_fUnC"),
        u'MAYÚSCULA_minúscula()': PlaceholderFunction(u"mayúscula_MINÚSCULA"),
        'func("argument")': PlaceholderFunction("func", (), String("argument")),
        'function("arg1", variable, 3)': PlaceholderFunction("function",
            (),
            String("arg1"),
            PlaceholderVariable("variable"),
            Number(3),
            ),
        'function("arg1", ns:variable, 3)': PlaceholderFunction(
            "function",
            (),
            String("arg1"),
            PlaceholderVariable("variable", ("ns", )),
            Number(3),
            ),
        'ns:function("arg1", ns:variable, 3)': PlaceholderFunction(
            "function",
            ("ns", ),
            String("arg1"),
            PlaceholderVariable("variable", ("ns", )),
            Number(3),
            ),
        'function("arg1", ns:sub_function(), 3.0)': PlaceholderFunction(
            "function",
            (),
            String("arg1"),
            PlaceholderFunction("sub_function", ("ns", )),
            Number(3),
            ),
        'ns:function("arg1", ns:sub_function(), 3.0)': PlaceholderFunction(
            "function",
            ("ns", ),
            String("arg1"),
            PlaceholderFunction("sub_function", ("ns", )),
            Number(3),
            ),
        'ns:function()': PlaceholderFunction("function", ("ns", )),
        'ns0:ns1:function()': PlaceholderFunction("function", ("ns0", "ns1")),
        'ns0:ns1:ns2:function()': PlaceholderFunction("function",
                                                      ("ns0", "ns1", "ns2")),
        'ns:sub_ns:function("with argument")': PlaceholderFunction("function",
            ("ns", "sub_ns"),
            String("with argument"),
            ),
        u'ñŝ:ñś1:function()': PlaceholderFunction("function", (u"ñŝ", u"ñś1")),
        u'ñŝ:ñś1:función()': PlaceholderFunction(u"función", (u"ñŝ", u"ñś1")),
    }

    invalid_operands = (
        # Invalid strings:
        '\'mixed quotes"',
        # Invalid numbers:
        "3 . 1416",
        "3. 1416",
        "3 .1416",
        "1,00",
        "12.4,500,000",
        # Invalid variables:
        "dashes-here-cant-you-see-them",
        "1st_variable",
        "25th_variable",
        "namespace-here:variable",
        "1stnamespace:var",
        "global:2ndlevel:var",
        "namespace:1st_variable",
        # Invalid functions:
        "func(",
        "func)",
        "func)(",
        "func[]",
        "func{}",
        "func(,)",
        "func(arg1, )",
        "func(, arg2)",
        "func(, arg2, )",
        "function-name()",
        "1st_function()",
        "25th_function()",
        "namespace-here:function()",
        "1stnamespace:function()",
        "global:2ndlevel:function()",
        "namespace:1st_function()",
        "foo( bad-namespace:baz() )",
        # Invalid sets:
        "[]",
        "{]",
        "[}",
        "}{",
        "{key: 'value'}",
        "[element1, element2, element3]",
        "{element 1, element 2}",
        "{element1; element2; element3}",
        "{element == 'string'}",
        # Default operators:
        "==",
        "!=",
        "<",
        ">",
        "<=",
        ">=",
        "~",
        "&",
        "^",
        "|",
        u"∈",
        u"⊂",
        # Miscellaneous:
        "-",
        "this is definitely not an operand",
    )

    def test_custom_tokens_against_trees(self):
        """
        All the custom tokens in the grammar must be taken into account by the
        parser.
        
        To test that custom tokens are used, and in order to test many scenarios
        writen few lines of code, we're going to convert operation nodes into
        boolean expressions (using the relevant grammar), and then these
        expressions will be parsed to check if the result is the original
        tree.
        
        """

        grammars = (
            # A grammar that overrides all the default tokens:
            Grammar(**{
                'not': "not", 'and': "and", 'xor': "xor", 'or': "or",
                'eq': "equals", 'ne': "different-from", 'lt': "less-than",
                'le': "less-equal", 'gt': "greater-than", 'ge': "greater-equal",
                'belongs_to': "belongs-to", 'is_subset': "is-subset-of",
                'set_start': "\\", 'set_end': "/", 'element_separator': ";",
                'arguments_start': "[", 'arguments_end': "]",
                'arguments_separator': ";", 'namespace_separator': ".",
                }
            ),
            # Now let's try a grammar where some operators represent the
            # initial characters of other operators:
            Grammar(**{
                'eq': "is", 'ne': "isn't", 'lt': "is less than",
                'gt': "is greater than", 'le': "is less than or equal to",
                'ge': "is greater than or equal to",
                'belongs_to': "is included in", 'is_subset': "is subset of",
                }
            )
        )

        for grammar_num in range(len(grammars)):
            grammar = grammars[grammar_num]
            parser = ConvertibleParser(grammar)
            convert_to_string = StringConverter(grammar)

            for operation in self.expressions.values():
                expression = convert_to_string(operation)

                # Using a Nose test generator:
                def check():
                    new_operation = parser(expression).root_node
                    eq_(operation, new_operation,
                        u'Original operation: %s --- Returned operation: %s' %
                        (repr(operation), repr(new_operation)))
                check.description = (u"The following expression is valid in "
                                     u"the grammar #%r: %r" % (grammar_num,
                                                               expression))

                yield check


class TestBaseParser(object):
    """
    Tests for the parsers' abstract base class.
    
    """

    def test_abstract_methods(self):
        parser = Parser(Grammar())
        assert_raises(NotImplementedError, parser.make_variable, None)
        assert_raises(NotImplementedError, parser.make_function, None)


class TestEvaluableParser(object):
    """Tests for the evaluable parser."""
    
    global_objects = {
        'bool': BoolVar(),
        'message': String("Hello world"),
        'foo': PermissiveFunction,
    }
    
    traffic_objects = {
        'traffic_light': TrafficLightVar(),
        'pedestrians_crossing_road': PedestriansCrossingRoad(),
        'drivers_awaiting_green_light': DriversAwaitingGreenLightVar(),
        'traffic_violation': TrafficViolationFunc,
    }
    
    root_namespace = Namespace(global_objects,
        {
        'traffic': Namespace(traffic_objects),
        })
    
    parser = EvaluableParser(Grammar(), root_namespace)
    
    #{ Tests for the parse action that makes the variables
    
    def test_existing_variable_without_namespace(self):
        parse_tree = self.parser("~ bool")
        eq_(parse_tree.root_node, Not(self.global_objects['bool']))
    
    def test_existing_variable_with_namespace(self):
        parse_tree = self.parser('traffic:traffic_light == "green"')
        expected_node = Equal(self.traffic_objects['traffic_light'],
                              String("green"))
        eq_(parse_tree.root_node, expected_node)
    
    def test_non_existing_variable_without_namespace(self):
        assert_raises(ScopeError, self.parser, "~ non_existing_var")
    
    def test_non_existing_variable_with_namespace(self):
        assert_raises(ScopeError, self.parser, "~ traffic:non_existing_var")
    
    def test_variable_in_non_existing_namespace(self):
        assert_raises(ScopeError, self.parser, "~ bar:foo")
    
    def test_function_instead_of_variable(self):
        # "foo" is a function, so it cannot be used as a variable (without
        # parenthesis):
        try:
            self.parser('~ foo')
        except BadExpressionError as exc:
            eq_('"foo" represents a function, not a variable', six.text_type(exc))
        else:
            assert 0, '"foo" is a function, not a variable!'
    
    def test_named_constant(self):
        """Named constants must be supported."""
        parse_tree = self.parser('message == "Hello earth"')
        expected_node = Equal(String("Hello world"), String("Hello earth"))
        eq_(parse_tree.root_node, expected_node)
    
    #{ Tests for the parse action that makes the functions
    
    def test_existing_function_without_namespace(self):
        parse_tree = self.parser('~ foo("baz")')
        eq_(parse_tree.root_node, Not(PermissiveFunction(String("baz"))))
    
    def test_existing_function_with_namespace(self):
        parse_tree = self.parser('~ traffic:traffic_violation("pedestrians")')
        expected_node = Not(TrafficViolationFunc(String("pedestrians")))
        eq_(parse_tree.root_node, expected_node)
    
    def test_non_existing_function_without_namespace(self):
        assert_raises(ScopeError, self.parser, "~ non_existing_function()")
    
    def test_non_existing_function_with_namespace(self):
        assert_raises(ScopeError, self.parser, "~ traffic:non_existing_func()")
    
    def test_function_in_non_existing_namespace(self):
        assert_raises(ScopeError, self.parser, "~ bar:foo(123)")
    
    def test_variable_instead_of_function(self):
        # "bool" is a variable, so it cannot be used as a function (with
        # parenthesis):
        try:
            self.parser('~ bool()')
        except BadExpressionError as exc:
            eq_('"bool" is not a function', six.text_type(exc))
        else:
            assert 0, '"bool" is a variable, not a function!'
    
    #}

