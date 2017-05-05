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
Tests for the parsing managers.

"""
from __future__ import unicode_literals

import datetime
from nose.tools import eq_, ok_, assert_false, assert_raises

from booleano.operations.variables import IntegerVariable, StringVariable, DateVariable, SetVariable, BooleanVariable, \
    DateTimeVariable
from booleano.parser import (SymbolTable, Bind, Grammar, ParseManager,
                             EvaluableParseManager, ConvertibleParseManager)
from booleano.parser.trees import EvaluableParseTree, ConvertibleParseTree
from booleano.operations import (Not, And, Or, Xor, Equal, NotEqual, LessThan,
    GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset, String, Number,
    Set, Variable, Function, PlaceholderVariable, PlaceholderFunction)
from booleano.exc import GrammarError

from tests import (BoolVar, TrafficLightVar, PedestriansCrossingRoad,
    DriversAwaitingGreenLightVar, PermissiveFunction, TrafficViolationFunc,
    LoggingHandlerFixture)


class TestBaseManager(object):
    """Tests for the base :class:`ParseManager`."""

    def test_abstract_methods(self):
        mgr = ParseManager(Grammar())
        assert_raises(NotImplementedError, mgr._define_parser, None, "es")


class TestEvaluableParseManager(object):
    """
    Tests for the :class:`EvaluableParseManager` with caching disabled.

    """

    # A symbol table to be used across the tests:
    symbol_table = SymbolTable("root",
        (
            Bind("boolean", BoolVar(), es="booleano"),
            Bind("message", String("Hello world"), es="mensaje"),
            Bind("foo", PermissiveFunction, es="fulano"),
        ),
        SymbolTable("traffic",
            (
                Bind("traffic_light", TrafficLightVar(), es=u"semáforo"),
                Bind("pedestrians_crossing_road", PedestriansCrossingRoad(),
                     es="peatones_cruzando_calle"),
                Bind("drivers_awaiting_green", DriversAwaitingGreenLightVar(),
                     es="conductores_esperando_verde"),
                Bind("traffic_violation", TrafficViolationFunc,
                     es=u"infracción"),
            ),
            es=u"tráfico"
        ),
    )

    def test_parsing_with_no_localized_grammars(self):
        mgr = EvaluableParseManager(self.symbol_table, Grammar())
        parse_tree1 = mgr.parse('message == "2009-07-13"')
        parse_tree2 = mgr.parse('message == "2009-07-13"', None)
        expected_tree = EvaluableParseTree(Equal(String("Hello world"),
                                                 String("2009-07-13")))
        eq_(parse_tree1, parse_tree2)
        eq_(parse_tree1, expected_tree)

    def test_parsing_with_localized_grammars(self):
        castilian_grammar = Grammar(decimal_separator=",",
                                    thousands_separator=".")
        mgr = EvaluableParseManager(self.symbol_table, Grammar(),
                                    es=castilian_grammar)
        parse_tree = mgr.parse(u"tráfico:peatones_cruzando_calle <= 3,00", "es")
        expected_tree = EvaluableParseTree(
            LessEqual(PedestriansCrossingRoad(), Number(3.0)))
        eq_(parse_tree, expected_tree)

    def test_parsing_with_undefined_grammar_but_available_translations(self):
        """
        When an expression is written in an unsupported grammar, a parser
        based on the generic grammar must be created and used.

        The respective translated bindings must be used if available.

        """
        log_handler = LoggingHandlerFixture()
        mgr = EvaluableParseManager(self.symbol_table, Grammar())
        # Castilian grammar is not supported:
        parse_tree = mgr.parse(u"tráfico:peatones_cruzando_calle <= 3.0", "es")
        expected_tree = EvaluableParseTree(
            LessEqual(PedestriansCrossingRoad(), Number(3)))
        eq_(parse_tree, expected_tree)
        # Checking the log:
        info = "Generated parser for unknown grammar %s" % repr(u'es')

        ok_(info in log_handler.handler.messages['info'])
        log_handler.undo()

    def test_parsing_with_undefined_grammar_and_no_translated_bindings(self):
        """
        When an expression is written in an unsupported grammar, a parser
        based on the generic grammar must be created and used.

        If there are no translated bindings, the default names must be used.

        """
        log_handler = LoggingHandlerFixture()
        mgr = EvaluableParseManager(self.symbol_table, Grammar())
        # French grammar is not supported:
        parse_tree = mgr.parse("traffic:pedestrians_crossing_road <= 3.0", "fr")
        expected_tree = EvaluableParseTree(
            LessEqual(PedestriansCrossingRoad(), Number(3)))
        eq_(parse_tree, expected_tree)
        # Checking the log:
        info = "Generated parser for unknown grammar %s" % repr('fr')
        ok_(info in log_handler.handler.messages['info'])
        log_handler.undo()

    def test_parsing_with_defined_grammar_but_no_available_translations(self):
        """
        When an expression is written in an supported grammar but there are no
        translated bindings, the default names must be used along with the
        custom grammar.

        """
        french_grammar = Grammar(decimal_separator=",", thousands_separator=".")
        mgr = EvaluableParseManager(self.symbol_table, Grammar(),
                                    fr=french_grammar)
        # French grammar is not supported:
        parse_tree = mgr.parse("traffic:pedestrians_crossing_road <= 3,0", "fr")
        expected_tree = EvaluableParseTree(
            LessEqual(PedestriansCrossingRoad(), Number(3)))
        eq_(parse_tree, expected_tree)

    def test_adding_grammar(self):
        """It should be possible to add grammars after instantiation."""
        castilian_grammar = Grammar(decimal_separator=",",
                                    thousands_separator=".")
        mgr = EvaluableParseManager(self.symbol_table, Grammar())
        mgr.add_parser("es", castilian_grammar)
        parse_tree = mgr.parse(u'tráfico:peatones_cruzando_calle <= 3,00', "es")
        expected_tree = EvaluableParseTree(
            LessEqual(PedestriansCrossingRoad(), Number(3.0)))
        eq_(parse_tree, expected_tree)

    def test_adding_existing_grammar(self):
        """There can't be duplicate/overlapped parsers."""
        mgr = EvaluableParseManager(self.symbol_table, Grammar(), es=Grammar())
        assert_raises(GrammarError, mgr.add_parser, "es", Grammar())

    def test_evaluating_expressions(self):
        """Managers should be able to evaluate the expressions too."""
        mgr = EvaluableParseManager(self.symbol_table, Grammar())
        context = {'pedestrians_crossroad': (u"gustavo", u"carla")}
        evaluation1 = mgr.evaluate("traffic:pedestrians_crossing_road <= 3",
                                   None, context)
        evaluation2 = mgr.evaluate(u'"carla" ∈ traffic:pedestrians_crossing_road',
                                   None, context)
        evaluation3 = mgr.evaluate("traffic:pedestrians_crossing_road > 2",
                                   None, context)
        ok_(evaluation1)
        ok_(evaluation2)
        assert_false(evaluation3)


class TestNativeVariableEvaluableParseManager(object):
    """
    Tests for the :class:`EvaluableParseManager` with caching disabled.

    """

    # A symbol table to be used across the tests:
    symbol_table = SymbolTable(
        "root",
        (
            Bind("myint", IntegerVariable("myint")),
            Bind("mybool", BooleanVariable("mybool")),
            Bind("mystring", StringVariable("mystring")),
            Bind("mydate", DateVariable("mydate")),
            Bind("mydate2", DateVariable("mydate2")),
            Bind("mydatetime", DateTimeVariable("mydatetime")),
            Bind("mydatetime2", DateTimeVariable("mydatetime2")),
            Bind("myset", SetVariable("myset")),
            Bind("myintbis", IntegerVariable("myint")),
        ),
        SymbolTable(
            "sub",
            (
                Bind("myint", IntegerVariable("sub.myint")),
            ),
        )
    )

    mgr = EvaluableParseManager(symbol_table, Grammar(belongs_to='in', is_subset='is subset of'))

    def test_variable_values_myint(self):
        ok_(self.mgr.parse('myint > 0')({'myint': 1}))
        ok_(not self.mgr.parse('myint > 0')({'myint': 0}))
        ok_(self.mgr.parse('myint == 1')({'myint': 1}))
        ok_(not self.mgr.parse('myint == 1')({'myint': 0}))
        ok_(self.mgr.parse('myint < 1')({'myint': 0}))
        ok_(not self.mgr.parse('myint < 0')({'myint': 2}))

    def test_variable_values_mybool(self):
        ok_(self.mgr.parse('mybool')({'mybool': True}))
        ok_(not self.mgr.parse('mybool')({'mybool': False}))
        ok_(self.mgr.parse('mybool > 0')({'mybool': True}))
        ok_(not self.mgr.parse('mybool > 0')({'mybool': False}))
        ok_(self.mgr.parse('mybool == 1')({'mybool': True}))
        ok_(not self.mgr.parse('mybool == 1')({'mybool': False}))
        ok_(self.mgr.parse('mybool < 1')({'mybool': False}))
        ok_(not self.mgr.parse('mybool < 0')({'mybool': True}))

    def test_variable_values_mystring(self):
        mystring = {'mystring': "hello"}
        # equiality
        ok_(self.mgr.parse('mystring == "hello"')(mystring))
        ok_(not self.mgr.parse('mystring != "hello"')(mystring))
        ok_(self.mgr.parse('mystring != "hell"')(mystring))
        ok_(not self.mgr.parse('mystring == "hell"')(mystring))
        # inequality
        ok_(self.mgr.parse('mystring >  "hella"')(mystring))
        ok_(self.mgr.parse('mystring <  "hellz"')(mystring))
        ok_(self.mgr.parse('mystring <  "hellz"')(mystring))
        ok_(self.mgr.parse('mystring <= "hello"')(mystring))
        ok_(self.mgr.parse('mystring >= "hello"')(mystring))
        # inequality reversed
        ok_(self.mgr.parse('"hella" <  mystring')(mystring))
        ok_(self.mgr.parse('"hellz" >  mystring')(mystring))
        ok_(self.mgr.parse('"hellz" >  mystring')(mystring))
        ok_(self.mgr.parse('"hello" >= mystring')(mystring))
        ok_(self.mgr.parse('"hello" >= mystring')(mystring))
        # bool
        ok_(self.mgr.parse('mystring')(mystring))
        ok_(not self.mgr.parse('~ mystring')(mystring))
        ok_(not self.mgr.parse('mystring')({'mystring': ''}))
        ok_(self.mgr.parse('~ mystring')({'mystring': ''}))
        # membership
        ok_(self.mgr.parse('mystring is subset of "zhelloy"')(mystring))
        ok_(not self.mgr.parse('mystring is subset of "zhellai"')(mystring))
        ok_(not self.mgr.parse('mystring is subset of "hello"')(mystring))
        ok_(self.mgr.parse('mystring in "ahelloa"')(mystring))
        ok_(self.mgr.parse('mystring in "hello"')(mystring))
        ok_(not self.mgr.parse('mystring in "hola"')(mystring))
        # inversed membership
        ok_(self.mgr.parse('"he" in mystring')(mystring))
        ok_(self.mgr.parse('"lo" in mystring')(mystring))
        ok_(not self.mgr.parse('"li" in mystring')(mystring))
        ok_(self.mgr.parse('"he" is subset of mystring')(mystring))
        ok_(self.mgr.parse('"lo" is subset of mystring')(mystring))
        ok_(not self.mgr.parse('"li" is subset of mystring')(mystring))
        ok_(not self.mgr.parse(' "hello" is subset of mystring')(mystring))

    def test_variable_values_date(self):
        mydate = {
            'mydate': datetime.date(2017, 1, 15),
            'mydate2': datetime.date(2017, 1, 17),
        }
        ok_(self.mgr.parse('mydate')(mydate))

        ok_(self.mgr.parse('mydate < "2017-01-18"')(mydate))
        ok_(self.mgr.parse('mydate < "18-01-2017"')(mydate))
        ok_(not self.mgr.parse('mydate < "12-01-2017"')(mydate))
        ok_(self.mgr.parse('mydate > "12-01-2017"')(mydate))

        ok_(self.mgr.parse('mydate == "15-01-2017"')(mydate))
        ok_(not self.mgr.parse('mydate == 1')(mydate))
        ok_(not self.mgr.parse('mydate == "13-01-2017"')(mydate))
        ok_(self.mgr.parse('mydate < mydate2')(mydate))
        ok_(not self.mgr.parse('mydate > mydate2')(mydate))
        ok_(not self.mgr.parse('mydate == mydate2')(mydate))

    def test_variable_values_datetime(self):
        mydatetime = {
            'mydatetime': datetime.datetime(2017, 1, 15, 12, 25),
            'mydatetime2': datetime.datetime(2017, 1, 17, 12, 23),
        }
        ok_(self.mgr.parse('mydatetime')(mydatetime))

        ok_(self.mgr.parse('mydatetime < "2017-01-15 12:25:02"')(mydatetime))
        ok_(self.mgr.parse('mydatetime > "2017-01-15 12:24:52"')(mydatetime))
        ok_(self.mgr.parse('mydatetime < "2017-01-15 13:00:00"')(mydatetime))
        ok_(self.mgr.parse('mydatetime < "18-01-2017 12:25:02"')(mydatetime))
        ok_(self.mgr.parse('mydatetime < "18-01-2017 12:25:02"')(mydatetime))
        ok_(not self.mgr.parse('mydatetime < "12-01-2017 12:25:02"')(mydatetime))
        ok_(self.mgr.parse('mydatetime > "12-01-2017 12:25:02"')(mydatetime))

        ok_(self.mgr.parse('mydatetime == "15-01-2017 12:25:00"')(mydatetime))
        ok_(not self.mgr.parse('mydatetime == 1')(mydatetime))
        ok_(not self.mgr.parse('mydatetime == "13-01-2017 12:25:02"')(mydatetime))
        ok_(self.mgr.parse('mydatetime < mydatetime2')(mydatetime))
        ok_(not self.mgr.parse('mydatetime > mydatetime2')(mydatetime))
        ok_(not self.mgr.parse('mydatetime == mydatetime2')(mydatetime))

    def test_variable_values_set(self):
        myset = {
            "myset": {1, 2, 3},
        }
        ok_(self.mgr.parse("1 is subset of myset ")(myset))
        ok_(self.mgr.parse("{1, 2} is subset of myset ")(myset))
        ok_(not self.mgr.parse("{1, 2, 3} is subset of myset ")(myset))
        ok_(self.mgr.parse("1 in myset ")(myset))
        ok_(self.mgr.parse("{1, 2} in myset ")(myset))
        ok_(self.mgr.parse("{1, 2, 3} in myset ")(myset))

    def test_variable_values_namespaced(self):
        myints = {
            "myint": 1,
            "sub.myint": 4
        }
        ok_(self.mgr.parse('sub:myint > 3')(myints))
        ok_(self.mgr.parse('sub:myint < 5')(myints))
        ok_(self.mgr.parse('sub:myint == 4')(myints))
        ok_(self.mgr.parse('sub:myint > myint')(myints))
        ok_(not self.mgr.parse('sub:myint < myint')(myints))
        ok_(not self.mgr.parse('sub:myint == myint')(myints))






class TestConvertibleParseManager(object):
    """
    Tests for the :class:`ConvertibleParseManager` with caching disabled.

    """

    def test_parsing_with_no_localized_grammars(self):
        mgr = ConvertibleParseManager(Grammar())
        parse_tree1 = mgr.parse('message == "2009-07-13"')
        parse_tree2 = mgr.parse('message == "2009-07-13"', None)
        expected_tree = ConvertibleParseTree(
            Equal(PlaceholderVariable("message"), String("2009-07-13")))
        eq_(parse_tree1, parse_tree2)
        eq_(parse_tree1, expected_tree)

    def test_parsing_with_localized_grammars(self):
        castilian_grammar = Grammar(decimal_separator=",",
                                    thousands_separator=".")
        mgr = ConvertibleParseManager(Grammar(), es=castilian_grammar)
        parse_tree = mgr.parse(u"tráfico:peatones_cruzando_calle <= 3,00", "es")
        expected_tree = ConvertibleParseTree(LessEqual(
            PlaceholderVariable("peatones_cruzando_calle", (u"tráfico", )),
            Number(3.0)
        ))
        eq_(parse_tree, expected_tree)


class TestManagersWithCaching(object):
    """
    Tests for the parse managers with caching enabled.

    """

    def setUp(self):
        castilian_grammar = Grammar(decimal_separator=",",
                                    thousands_separator=".")
        self.manager = ConvertibleParseManager(Grammar(), cache_limit=3,
                                               es=castilian_grammar)

    def test_empty_by_default(self):
        """The cache must be empty by default."""
        eq_(self.manager._cache.counter, 0)
        eq_(len(self.manager._cache.cache_by_locale), 0)
        eq_(len(self.manager._cache.latest_expressions), 0)

    def test_parsing_not_yet_cached_result(self):
        """Not yet cached trees must be cached after parsing."""
        # The first parse:
        expr1 = 'today == "2009-07-13"'
        locale1 = "es_VE"
        tree1 = self.manager.parse(expr1, locale1)
        eq_(self.manager._cache.counter, 1)
        eq_(len(self.manager._cache.cache_by_locale[locale1]), 1)
        eq_(self.manager._cache.cache_by_locale[locale1][expr1], tree1)
        eq_(self.manager._cache.latest_expressions, [(locale1, expr1)])
        # The second parse:
        expr2 = 'yesterday > "1999-06-01"'
        locale2 = "es_ES"
        tree2 = self.manager.parse(expr2, locale2)
        eq_(self.manager._cache.counter, 2)
        eq_(len(self.manager._cache.cache_by_locale[locale2]), 1)
        eq_(self.manager._cache.cache_by_locale[locale2][expr2], tree2)
        eq_(self.manager._cache.latest_expressions, [(locale2, expr2),
                                                     (locale1, expr1)])

    def test_parsing_already_cached_result(self):
        """Already parsed expressions must not be parsed again."""
        expr = 'today == "2009-07-13"'
        locale = "es_VE"
        # Parsing it twice:
        tree1 = self.manager.parse(expr, locale)
        tree2 = self.manager.parse(expr, locale)
        eq_(tree1, tree2)
        # Checking the cache:
        eq_(self.manager._cache.counter, 1)
        eq_(len(self.manager._cache.cache_by_locale[locale]), 1)
        eq_(self.manager._cache.cache_by_locale[locale][expr], tree1)
        eq_(self.manager._cache.latest_expressions, [(locale, expr)])

    def test_limit_reached(self):
        """
        When the cache limit has been reached, the oldest items must be removed.

        """
        expr1 = 'today == "2009-07-13"'
        expr2 = 'yesterday < "2009-07-13"'
        expr3 = 'tomorrow > "2009-07-13"'
        expr4 = 'today > "1999-01-06"'
        # Parsing the expressions:
        tree1 = self.manager.parse(expr1)
        tree2 = self.manager.parse(expr2)
        tree3 = self.manager.parse(expr3)
        tree4 = self.manager.parse(expr4)
        # Checking the cache:
        eq_(self.manager._cache.counter, 3)
        eq_(len(self.manager._cache.cache_by_locale[None]), 3)
        eq_(self.manager._cache.cache_by_locale[None][expr2], tree2)
        eq_(self.manager._cache.cache_by_locale[None][expr3], tree3)
        eq_(self.manager._cache.cache_by_locale[None][expr4], tree4)
        latest = [(None, expr4), (None, expr3), (None, expr2)]
        eq_(self.manager._cache.latest_expressions, latest)

    def test_limit_reached_in_different_locales(self):
        """
        When the cache limit has been reached among all the locales, the
        oldest items must be removed.

        """
        expr1 = 'today == "2009-07-13"'
        expr2 = 'yesterday < "2009-07-13"'
        expr3 = 'tomorrow > "2009-07-13"'
        expr4 = 'hoy > "1999-01-06"'
        # Parsing the expressions:
        tree1 = self.manager.parse(expr1)
        tree2 = self.manager.parse(expr2, "fr")
        tree3 = self.manager.parse(expr3)
        tree4 = self.manager.parse(expr4, "es")
        # Checking the cache:
        eq_(self.manager._cache.counter, 3)
        eq_(len(self.manager._cache.cache_by_locale[None]), 1)
        eq_(len(self.manager._cache.cache_by_locale['es']), 1)
        eq_(len(self.manager._cache.cache_by_locale['fr']), 1)
        eq_(self.manager._cache.cache_by_locale['fr'][expr2], tree2)
        eq_(self.manager._cache.cache_by_locale[None][expr3], tree3)
        eq_(self.manager._cache.cache_by_locale['es'][expr4], tree4)
        latest = [("es", expr4), (None, expr3), ("fr", expr2)]
        eq_(self.manager._cache.latest_expressions, latest)

    def test_unlimited_caching(self):
        """
        The cache may have no limit.

        If so, the cache counter will be disabled.

        """
        manager = ConvertibleParseManager(Grammar(), cache_limit=None)
        manager.parse('today == "2009-07-13"')
        manager.parse('yesterday < "2009-07-13"')
        manager.parse('tomorrow > "2009-07-13"')
        manager.parse('hoy > "1999-01-06"')
        manager.parse('ayer > "1999-01-06"')
        # Checking the cache:
        eq_(manager._cache.counter, 5)
        eq_(len(manager._cache.cache_by_locale[None]), 5)
        eq_(len(manager._cache.latest_expressions), 5)

