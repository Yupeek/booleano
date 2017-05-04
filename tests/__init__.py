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
Test suite for Booleano.

This module contains utilities shared among the whole test suite.

"""

from __future__ import unicode_literals
import six

if six.PY2:  # pragma: nocover
    import sys
    reload(sys)
    sys.setdefaultencoding("utf-8")


import logging
from collections import OrderedDict



from booleano.operations.converters import BaseConverter
from booleano.operations import (Not, And, Or, Xor, Equal, NotEqual, LessThan,
    GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset, String, Number,
    Set, Variable, Function, PlaceholderVariable, PlaceholderFunction)
from booleano.exc import InvalidOperationError, BadCallError


#{ Mock variables


class BoolVar(Variable):
    """
    Mock variable which represents the boolean value stored in a context item
    called ``bool``.
    
    """
    operations = set(("boolean", "equality"))
    
    def __init__(self):
        self.evaluated = False
        super(BoolVar, self).__init__()
    
    def to_python(self, context):
        """Return the value of the ``bool`` context item"""
        self.evaluated = True
        return context['bool']
    
    def equals(self, value, context):
        """Does ``value`` equal this boolean variable?"""
        self.evaluated = True
        return context['bool'] == value
    
    def __call__(self, context):
        """Does the value of context item ``bool`` evaluate to True?"""
        self.evaluated = True
        return bool(context['bool'])


class TrafficLightVar(Variable):
    """
    Variable that represents a traffic light.
    
    """
    
    operations = set(("equality", "boolean"))
    
    valid_colors = ("red", "amber", "green")
    
    def to_python(self, context):
        """Return the string that represents the current light color"""
        return context['traffic_light']
    
    def __call__(self, context):
        """Is the traffic light working?"""
        return bool(context['traffic_light'])
    
    def equals(self, value, context):
        """Does the traffic light's color equal to ``value``?"""
        if value not in self.valid_colors:
            raise InvalidOperationError("Traffic lights can't be %s" % value)
        return value == context['traffic_light']


class VariableSet(Variable):
    """
    Base class for a variable which finds its value in one of the context.
    
    Descendants have to define the context item that contains the set, in
    the ``people_set`` attribute.
    
    """
    
    operations = set(("equality", "inequality", "boolean", "membership"))
    
    def to_python(self, context):
        set_ = set(context[self.people_set])
        return set_
    
    def __call__(self, context):
        set_ = set(context[self.people_set])
        return bool(set_)
    
    def equals(self, value, context):
        set_ = set(context[self.people_set])
        value = set(value)
        return value == set_
    
    def less_than(self, value, context):
        set_ = context[self.people_set]
        return len(set_) < value
    
    def greater_than(self, value, context):
        set_ = context[self.people_set]
        return len(set_) > value
    
    def belongs_to(self, value, context):
        set_ = context[self.people_set]
        return value in set_
    
    def is_subset(self, value, context):
        value = set(value)
        set_ = set(context[self.people_set])
        return value.issubset(set_)


class PedestriansCrossingRoad(VariableSet):
    """Variable that represents the pedestrians crossing the street."""
    
    people_set = "pedestrians_crossroad"


class DriversAwaitingGreenLightVar(VariableSet):
    """
    Variable that represents the drivers waiting for the green light to
    cross the crossroad.
    
    """
    
    people_set = "drivers_trafficlight"


#{ Mock functions


class PermissiveFunction(Function):
    """
    A mock function operator which accepts any type of arguments.
    
    """
    
    operations = set(["boolean"])
    
    required_arguments = ("arg0", )
    
    optional_arguments = OrderedDict([('oarg0', Set()), ('oarg1', Number(1))])
    
    def check_arguments(self):
        """Do nothing -- Allow any kind of arguments."""
        pass
    
    def to_python(self, context):
        return self.arguments
    
    def __call__(self, context):
        return True


class TrafficViolationFunc(Function):
    """
    Function operator that checks if there are drivers/pedestrians crossing
    the crossroad when their respective traffic light is red.
    
    """
    
    operations = set(["boolean"])
    
    required_arguments = ("light", )
    
    def check_arguments(self):
        assert isinstance(self.arguments['light'], String)
        light = self.arguments['light'].constant_value
        if light not in ("pedestrians", "drivers"):
            raise BadCallError("Only pedestrians and drivers have lights")
    
    def to_python(self, context):
        return self.arguments
    
    def __call__(self, context):
        if self.arguments['light'] == "pedestrians":
            return context['pedestrians_light'] == "red" and \
                   len(context['people_crossing'])
        # It's the drivers' light.
        return context['drivers_light'] == "red" and \
               len(context['cars_crossing'])


#{ Miscellaneous stuff


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""
    
    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())
    
    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


class LoggingHandlerFixture(object):
    """Manager of the :class:`MockLoggingHandler`s."""
    
    def __init__(self):
        self.logger = logging.getLogger("booleano")
        self.handler = MockLoggingHandler()
        self.logger.addHandler(self.handler)
    
    def undo(self):
        self.logger.removeHandler(self.handler)


class AntiConverter(BaseConverter):
    """
    A parse tree converter that returns the original parse tree, ignoring the
    namespaces in the constants.
    
    This is the simplest way to check the converter.
    
    """
    
    def convert_not(self, operand):
        return Not(operand)
    
    def convert_and(self, master_operand, slave_operand):
        return And(master_operand, slave_operand)
    
    def convert_or(self, master_operand, slave_operand):
        return Or(master_operand, slave_operand)
    
    def convert_xor(self, master_operand, slave_operand):
        return Xor(master_operand, slave_operand)
    
    def convert_equal(self, master_operand, slave_operand):
        return Equal(master_operand, slave_operand)
    
    def convert_not_equal(self, master_operand, slave_operand):
        return NotEqual(master_operand, slave_operand)
    
    def convert_less_than(self, master_operand, slave_operand):
        return LessThan(master_operand, slave_operand)
    
    def convert_greater_than(self, master_operand, slave_operand):
        return GreaterThan(master_operand, slave_operand)
    
    def convert_less_equal(self, master_operand, slave_operand):
        return LessEqual(master_operand, slave_operand)
    
    def convert_greater_equal(self, master_operand, slave_operand):
        return GreaterEqual(master_operand, slave_operand)
    
    def convert_belongs_to(self, master_operand, slave_operand):
        return BelongsTo(slave_operand, master_operand,)
    
    def convert_is_subset(self, master_operand, slave_operand):
        return IsSubset(slave_operand, master_operand)
    
    def convert_string(self, text):
        return String(text)
    
    def convert_number(self, number):
        return Number(number)
    
    def convert_set(self, *elements):
        return Set(*elements)
    
    def convert_variable(self, name, namespace_parts):
        return PlaceholderVariable(name, namespace_parts)
    
    def convert_function(self, name, namespace_parts, *arguments):
        return PlaceholderFunction(name, namespace_parts, *arguments)


class StringConverter(BaseConverter):
    """
    Parse tree converter that turns the tree back into a string, based on a
    given grammar.
    
    """
    
    def __init__(self, grammar):
        """
        Set up the converter.
        
        :param grammar: The grammar to be used.
        :type grammar: Grammar
        
        """
        self.grammar = grammar
    
    def convert_not(self, operand):
        return u"%s %s" % (self.grammar.get_token("not"), operand)
    
    def __make_binary_infix__(self,
                              operator_token,
                              master_operand,
                              slave_operand):
        """Make a binary infix expression."""
        token = self.grammar.get_token(operator_token)
        group_start = self.grammar.get_token("group_start")
        group_end = self.grammar.get_token("group_end")
        all_tokens = (group_start, master_operand, token, slave_operand,
                      group_end)
        expression = u" ".join(all_tokens)
        return expression
    
    def convert_and(self, master_operand, slave_operand):
        return self.__make_binary_infix__("and", master_operand, slave_operand)
    
    def convert_or(self, master_operand, slave_operand):
        return self.__make_binary_infix__("or", master_operand, slave_operand)
    
    def convert_xor(self, master_operand, slave_operand):
        return self.__make_binary_infix__("xor", master_operand, slave_operand)
    
    def convert_equal(self, master_operand, slave_operand):
        return self.__make_binary_infix__("eq", master_operand, slave_operand)
    
    def convert_not_equal(self, master_operand, slave_operand):
        return self.__make_binary_infix__("ne", master_operand, slave_operand)
    
    def convert_less_than(self, master_operand, slave_operand):
        return self.__make_binary_infix__("lt", master_operand, slave_operand)
    
    def convert_greater_than(self, master_operand, slave_operand):
        return self.__make_binary_infix__("gt", master_operand, slave_operand)
    
    def convert_less_equal(self, master_operand, slave_operand):
        return self.__make_binary_infix__("le", master_operand, slave_operand)
    
    def convert_greater_equal(self, master_operand, slave_operand):
        return self.__make_binary_infix__("ge", master_operand, slave_operand)
    
    def convert_belongs_to(self, master_operand, slave_operand):
        return self.__make_binary_infix__("belongs_to", slave_operand,
                                          master_operand)
    
    def convert_is_subset(self, master_operand, slave_operand):
        return self.__make_binary_infix__("is_subset", slave_operand,
                                          master_operand)
    
    def convert_string(self, text):
        return u'"%s"' % text
    
    def convert_number(self, number):
        # TODO: Number properties such as decimal separator must be taken into
        # account.
        return six.text_type(number)
    
    def convert_set(self, *elements):
        element_sep = self.grammar.get_token("element_separator") + " "
        elements = element_sep.join(elements)
        set_start = self.grammar.get_token("set_start")
        set_end = self.grammar.get_token("set_end")
        return set_start + elements + set_end
    
    def convert_variable(self, name, namespace_parts):
        return self.__build_identifier__(name, namespace_parts)
    
    def convert_function(self, name, namespace_parts, *arguments):
        identifier = self.__build_identifier__(name, namespace_parts)
        arg_start = self.grammar.get_token("arguments_start")
        arg_end = self.grammar.get_token("arguments_end")
        arg_sep = self.grammar.get_token("arguments_separator") + " "
        arguments = arg_sep.join(arguments)
        return identifier + arg_start + arguments + arg_end
    
    def __build_identifier__(self, name, namespace_parts):
        if not namespace_parts:
            return name
        ns_sep = self.grammar.get_token("namespace_separator")
        namespace = ns_sep.join(namespace_parts)
        identifier = namespace + ns_sep + name
        return identifier


#}
