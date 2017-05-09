# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

import six
from nose.tools import ok_, assert_raises, assert_equal

from booleano.operations.variables import NumberVariable, BooleanVariable, StringVariable, DateVariable, \
    DateTimeVariable, SetVariable, NativeVariable
from booleano.parser.symbol_table_builder import SymbolTableBuilder
from booleano.parser import SymbolTable, Bind, Grammar
from booleano.parser.core import EvaluableParseManager


class TestNativeVariableEvaluableParseManager(object):
    """
    Tests for the :class:`EvaluableParseManager` with caching disabled.

    """

    # A symbol table to be used across the tests:
    symbol_table = SymbolTable(
        "root",
        (
            Bind("myint", NumberVariable("myint")),
            Bind("mybool", BooleanVariable("mybool")),
            Bind("mystring", StringVariable("mystring")),
            Bind("mydate", DateVariable("mydate")),
            Bind("mydate2", DateVariable("mydate2")),
            Bind("mydatetime", DateTimeVariable("mydatetime")),
            Bind("mydatetime2", DateTimeVariable("mydatetime2")),
            Bind("myset", SetVariable("myset")),
            Bind("myintbis", NumberVariable("myint")),
        ),
        SymbolTable(
            "sub",
            (
                Bind("myint", NumberVariable("sub.myint")),
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


class TestVariableSymbolTableBuilder(object):
    FakeVariable = type(str('FakeVariable'), (NativeVariable,), {})
    FakeVariableSub = type(str('FakeVariable'), (FakeVariable,), {})

    MyString = type(str('MyString'), (str,), {})
    MyStringVariable = type(str('MyStringVariable'), (NativeVariable,), {})

    def test_registering(self):
        vb = SymbolTableBuilder()
        ok_(len(vb.registered_variables) == 0)
        vb.register(int, self.FakeVariable)
        ok_(len(vb.registered_variables) == 1)
        vb.register(float, self.FakeVariable)
        ok_(len(vb.registered_variables) == 2)

        @vb.register(six.text_type)
        class TextVariable(NativeVariable):
            pass

        ok_(len(vb.registered_variables) == 3)

    def test_registering_error(self):
        vb = SymbolTableBuilder()
        vb.register(int, self.FakeVariable)
        assert_raises(Exception, vb.register, int, self.FakeVariableSub)

    def test_resolve_type(self):

        vb = SymbolTableBuilder()
        vb.register(str, self.FakeVariable)
        # sub class of str resolve to common FakeVariable
        assert_equal(vb.find_for_type(str), self.FakeVariable)
        assert_equal(vb.find_for_type(self.MyString), self.FakeVariable)

        # registering more concrete class: this one take precedence
        vb.register(self.MyString, self.MyStringVariable)
        assert_equal(vb.find_for_type(str), self.FakeVariable)
        assert_equal(vb.find_for_type(self.MyString), self.MyStringVariable)

    def test_creation_table(self):
        vb = SymbolTableBuilder()
        vb.register(six.text_type, self.FakeVariable)
        vb.register(int, self.FakeVariableSub)
        st = vb("root", {"name": "katara", "age": 15})
        assert_equal(st, SymbolTable('root', (
            Bind("name", self.FakeVariable),
            Bind("age", self.FakeVariableSub),
        )))

    def test_creation_table_unknown_type(self):
        vb = SymbolTableBuilder()
        vb.register(six.text_type, self.FakeVariable)
        vb.register(int, self.FakeVariableSub)
        assert_raises(Exception,
                      vb, "root", {"name": "katara", "age": 15.}
                      )


