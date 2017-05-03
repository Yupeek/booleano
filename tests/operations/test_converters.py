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
Tests for the parse tree converters.

"""
from nose.tools import eq_, assert_raises, raises

from booleano.operations.converters import BaseConverter
from booleano.operations import (Not, And, Or, Xor, Equal, NotEqual, LessThan,
    GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset, String, Number,
    Set, Variable, Function, PlaceholderVariable, PlaceholderFunction)
from booleano.exc import ConversionError

from tests import AntiConverter


#{ The tests themselves


class TestBaseConverter(object):
    """Tests for the base class of the converters."""
    
    def test_no_default_conversion(self):
        """No node is convertible by default."""
        conv = BaseConverter()
        assert_raises(NotImplementedError, conv.convert_string, None)
        assert_raises(NotImplementedError, conv.convert_number, None)
        assert_raises(NotImplementedError, conv.convert_set, None)
        assert_raises(NotImplementedError, conv.convert_variable, None, ())
        assert_raises(NotImplementedError, conv.convert_function, None, ())
        assert_raises(NotImplementedError, conv.convert_not, None)
        assert_raises(NotImplementedError, conv.convert_and, None, None)
        assert_raises(NotImplementedError, conv.convert_or, None, None)
        assert_raises(NotImplementedError, conv.convert_xor, None, None)
        assert_raises(NotImplementedError, conv.convert_equal, None, None)
        assert_raises(NotImplementedError, conv.convert_not_equal, None, None)
        assert_raises(NotImplementedError, conv.convert_less_than, None, None)
        assert_raises(NotImplementedError, conv.convert_greater_than, None,
                      None)
        assert_raises(NotImplementedError, conv.convert_less_equal, None, None)
        assert_raises(NotImplementedError, conv.convert_greater_equal, None,
                      None)
        assert_raises(NotImplementedError, conv.convert_belongs_to, None, None)
        assert_raises(NotImplementedError, conv.convert_is_subset, None, None)


class TestActualConverter(object):
    """Tests for an actual converter."""
    
    parse_trees = (
        # Operands alone:
        String("this is a string"),
        String(u"¡Estás viendo un texto en castellano aquí!"),
        Number(12345),
        Number(123.45),
        Set(String("hola"), PlaceholderVariable("today", None), Number(4)),
        Set(),
        PlaceholderVariable("tomorrow", None),
        PlaceholderFunction("today_is_gonna_rain", None),
        PlaceholderFunction("distance", None,
                            PlaceholderFunction("where_am_i", None),
                            String("Paris")),
        # Unary operators:
        Not(PlaceholderFunction("near_paris",
                                None,
                                PlaceholderVariable("moon", None))),
        # Binary operators:
        And(
            PlaceholderFunction("in_europe", None),
            PlaceholderFunction("in_spain", None)
            ),
        And(
            Or(
               Equal(
                     PlaceholderVariable("venezuela", None),
                     String("Venezuela")
                     ),
               PlaceholderFunction("today_is_gonna_rain", None)),
            Xor(
                Equal(
                      PlaceholderVariable("venezuela", None),
                      String("Venezuela")
                      ),
                PlaceholderFunction("today_is_gonna_rain", None))
            ),
        Or(
           PlaceholderFunction("in_europe", None),
           PlaceholderFunction("in_spain", None)
           ),
        Or(
            And(
               Equal(
                     PlaceholderVariable("venezuela", None), 
                     String("Venezuela")
                     ),
               PlaceholderFunction("today_is_gonna_rain", None)),
            Xor(
                Equal(
                      PlaceholderVariable("venezuela", None), 
                      String("Venezuela")
                      ),
                PlaceholderFunction("today_is_gonna_rain", None))
            ),
        Xor(
            PlaceholderFunction("in_europe", None), 
            PlaceholderFunction("in_spain", None)
            ),
        Xor(
            Or(
               Equal(
                     PlaceholderVariable("venezuela", None), 
                     String("Venezuela")
                     ),
               PlaceholderFunction("today_is_gonna_rain", None)),
            And(
                Equal(
                      PlaceholderVariable("venezuela", None),
                      String("Venezuela")
                      ),
                PlaceholderFunction("today_is_gonna_rain", None))
            ),
        Equal(PlaceholderVariable("venezuela", None), String("Venezuela")),
        NotEqual(
                 PlaceholderVariable("venezuela", None), 
                 PlaceholderVariable("here", None)
                 ),
        LessThan(Number(2), PlaceholderVariable("counter", None)),
        GreaterThan(Number(2), PlaceholderVariable("counter", None)),
        LessEqual(Number(2), PlaceholderVariable("counter", None)),
        GreaterEqual(Number(2), PlaceholderVariable("counter", None)),
        BelongsTo(Number(4), Set(Number(3), String("no"), Number(0))),
        IsSubset(Set(), Set(Number(3), String("no"), Number(0))),
    )
    
    def test_conversions(self):
        """Check that each parse tree is converted back to its original form."""
        for parse_tree in self.parse_trees:
            
            # Let's use a Nose test generator:
            def check():
                conversion = ANTI_CONVERTER(parse_tree)
                eq_(parse_tree, conversion,
                    'Parse tree %s changed to %s' % (repr(parse_tree),
                                                     repr(conversion)))
            check.description = ("Parse tree %s shouldn't change" %
                                 repr(parse_tree))
            
            yield check
    
    @raises(ConversionError)
    def test_converting_non_node(self):
        """Only nodes are tried to be converted."""
        ANTI_CONVERTER(12345)


#{ Test utilities


ANTI_CONVERTER = AntiConverter()


#}

