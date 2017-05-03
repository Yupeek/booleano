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
Tests for the operators.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises, raises

from booleano.operations import (Not, And, Or, Xor, Equal, NotEqual, LessThan,
    GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset)
from booleano.operations.operators import Operator
from booleano.operations.operands import String, Number, Set, Variable
from booleano.exc import InvalidOperationError

from tests import (TrafficLightVar, PedestriansCrossingRoad,
                   DriversAwaitingGreenLightVar, BoolVar)


class TestOperator(object):
    """Tests for the base Operator class."""
    
    def test_no_evaluation_implemented(self):
        """Evaluations must not be implemented by default."""
        op = Operator()
        assert_raises(NotImplementedError, op, None)
    
    def test_type(self):
        """Operator nodes must be known as operators."""
        op = Operator()
        ok_(op.is_operator())
        assert_false(op.is_operand())
    
    def test_node_type(self):
        """Operators are all branch nodes."""
        op = Operator()
        ok_(op.is_branch())
        assert_false(op.is_leaf())
    
    def test_python_bool(self):
        """Operators must not support Pythonic truth evaluation."""
        op = Operator()
        assert_raises(InvalidOperationError, bool, op)


class TestNot(object):
    """Tests for the :class:`Not`."""
    
    def test_constructor_with_boolean_operand(self):
        traffic_light = TrafficLightVar()
        Not(traffic_light)
    
    def test_constructor_with_operator(self):
        """The Not operator must also support operators as operands"""
        traffic_light = TrafficLightVar()
        Not(And(traffic_light, traffic_light))
    
    @raises(InvalidOperationError)
    def test_constructor_with_non_boolean_operand(self):
        # Constants cannot act as booleans
        constant = String("Paris")
        Not(constant)
    
    def test_evaluation(self):
        # Setup:
        traffic_light = TrafficLightVar()
        operation = Not(traffic_light)
        # Evaluation:
        ok_(operation( dict(traffic_light="") ))
        assert_false(operation( dict(traffic_light="green") ))
    
    def test_equivalent(self):
        """
        Two negation operations are equivalent if they evaluate the same 
        operand.
        
        """
        op1 = Not(BoolVar())
        op2 = Not(BoolVar())
        op3 = Not(PedestriansCrossingRoad())
        
        op1.check_equivalence(op2)
        op2.check_equivalence(op1)
        
        assert_raises(AssertionError, op1.check_equivalence, op3)
        assert_raises(AssertionError, op2.check_equivalence, op3)
        assert_raises(AssertionError, op3.check_equivalence, op1)
        assert_raises(AssertionError, op3.check_equivalence, op2)
        
        ok_(op1 == op2)
        ok_(op2 == op1)
        ok_(op1 != op3)
        ok_(op2 != op3)
        ok_(op3 != op1)
        ok_(op3 != op2)
    
    def test_string_representation(self):
        op1 = Not(BoolVar())
        op2 = Not(And(BoolVar(), BoolVar()))
        as_unicode1 = unicode(op1)
        as_unicode2 = unicode(op2)
        eq_(as_unicode1, "Not(Anonymous variable [BoolVar])")
        eq_(as_unicode1, str(op1))
        eq_(as_unicode2, "Not(And(Anonymous variable [BoolVar], " \
                         "Anonymous variable [BoolVar]))")
        eq_(as_unicode2, str(op2))
    
    def test_representation(self):
        # With an operand:
        op = Not(BoolVar())
        eq_(repr(op), '<Not <Anonymous variable [BoolVar]>>')
        # With an operation:
        op = Not(And(BoolVar(), BoolVar()))
        expected = "<Not <And <Anonymous variable [BoolVar]> " \
                             "<Anonymous variable [BoolVar]>>>"
        eq_(repr(op), expected)


class TestAnd(object):
    """Tests for the And operator."""
    
    def test_constructor_with_operands(self):
        """The constructor must support actual operands as arguments"""
        And(BoolVar(), TrafficLightVar())
    
    def test_constructor_with_operators(self):
        """The constructor must support operators as arguments."""
        And(Not(BoolVar()), Not(TrafficLightVar()))
    
    def test_constructor_with_mixed_operands(self):
        """
        The constructor must support operators and actual operands as arguments.
        
        """
        And(BoolVar(), Not(TrafficLightVar()))
        And(Not(BoolVar()), TrafficLightVar())
    
    def test_with_both_results_as_true(self):
        operation = And(BoolVar(), TrafficLightVar())
        ok_(operation( dict(bool=True, traffic_light="red") ))
    
    def test_with_both_results_as_false(self):
        operation = And(BoolVar(), TrafficLightVar())
        assert_false(operation( dict(bool=False, traffic_light="") ))
    
    def test_with_mixed_results(self):
        operation = And(BoolVar(), TrafficLightVar())
        assert_false(operation( dict(bool=False, traffic_light="red") ))
    
    def test_evaluation_order(self):
        """
        For efficiency, the second operand must not be evaluated if the first
        one is False.
        
        """
        op1 = BoolVar()
        op2 = BoolVar()
        context = {'bool': False}
        And(op1, op2)(context)
        ok_(op1.evaluated)
        assert_false(op2.evaluated)
    
    def test_equivalent(self):
        """Two conjunctions are equivalent if they have the same operands."""
        op1 = And(BoolVar(), PedestriansCrossingRoad())
        op2 = And(PedestriansCrossingRoad(), BoolVar())
        op3 = And(DriversAwaitingGreenLightVar(), BoolVar())
        
        op1.check_equivalence(op2)
        op2.check_equivalence(op1)
        
        assert_raises(AssertionError, op1.check_equivalence, op3)
        assert_raises(AssertionError, op2.check_equivalence, op3)
        assert_raises(AssertionError, op3.check_equivalence, op1)
        assert_raises(AssertionError, op3.check_equivalence, op2)
        
        ok_(op1 == op2)
        ok_(op2 == op1)
        ok_(op1 != op3)
        ok_(op2 != op3)
        ok_(op3 != op1)
        ok_(op3 != op2)
    
    def test_string_representation(self):
        op = And(BoolVar(), BoolVar())
        as_unicode = unicode(op)
        eq_("And(Anonymous variable [BoolVar], Anonymous variable [BoolVar])",
            as_unicode)
        eq_(as_unicode, str(op))
        
        # Now with operators as operands:
        op = And(Not(BoolVar()), Not(BoolVar()))
        eq_("And(Not(Anonymous variable [BoolVar]), Not(Anonymous variable [BoolVar]))",
            unicode(op))
    
    def test_representation(self):
        op = And(BoolVar(), BoolVar())
        expected = "<And <Anonymous variable [BoolVar]> " \
                        "<Anonymous variable [BoolVar]>>"
        eq_(repr(op), expected)
        
        # Now with operators as operands:
        op = And(Not(BoolVar()), Not(BoolVar()))
        expected = "<And <Not <Anonymous variable [BoolVar]>> " \
                        "<Not <Anonymous variable [BoolVar]>>>"
        eq_(repr(op), expected)


class TestOr(object):
    """Tests for the Or operator."""
    
    def test_constructor_with_operands(self):
        """The constructor must support actual operands as arguments"""
        Or(BoolVar(), TrafficLightVar())
    
    def test_constructor_with_operators(self):
        """The constructor must support operators as arguments."""
        Or(Not(BoolVar()), Not(TrafficLightVar()))
    
    def test_constructor_with_mixed_operands(self):
        """
        The constructor must support operators and actual operands as arguments.
        
        """
        Or(BoolVar(), Not(TrafficLightVar()))
        Or(Not(BoolVar()), TrafficLightVar())
    
    def test_with_both_results_as_true(self):
        operation = Or(BoolVar(), TrafficLightVar())
        ok_(operation( dict(bool=True, traffic_light="red") ))
    
    def test_with_both_results_as_false(self):
        operation = Or(BoolVar(), TrafficLightVar())
        assert_false(operation( dict(bool=False, traffic_light="") ))
    
    def test_with_mixed_results(self):
        operation = Or(BoolVar(), TrafficLightVar())
        ok_(operation( dict(bool=False, traffic_light="red") ))
    
    def test_evaluation_order(self):
        """
        For efficiency, the second operand must not be evaluated if the first
        one is True.
        
        """
        op1 = BoolVar()
        op2 = BoolVar()
        context = {'bool': True}
        Or(op1, op2)(context)
        ok_(op1.evaluated)
        assert_false(op2.evaluated)
    
    def test_equivalent(self):
        """
        Two inclusive disjunctions are equivalent if they have the same
        operands.
        
        """
        op1 = Or(BoolVar(), PedestriansCrossingRoad())
        op2 = Or(PedestriansCrossingRoad(), BoolVar())
        op3 = Or(DriversAwaitingGreenLightVar(), BoolVar())
        
        op1.check_equivalence(op2)
        op2.check_equivalence(op1)
        
        assert_raises(AssertionError, op1.check_equivalence, op3)
        assert_raises(AssertionError, op2.check_equivalence, op3)
        assert_raises(AssertionError, op3.check_equivalence, op1)
        assert_raises(AssertionError, op3.check_equivalence, op2)
        
        ok_(op1 == op2)
        ok_(op2 == op1)
        ok_(op1 != op3)
        ok_(op2 != op3)
        ok_(op3 != op1)
        ok_(op3 != op2)
    
    def test_string_representation(self):
        op = Or(BoolVar(), BoolVar())
        as_unicode = unicode(op)
        expected = "Or(Anonymous variable [BoolVar], " \
                   "Anonymous variable [BoolVar])"
        eq_(as_unicode, expected)
        eq_(as_unicode, str(op))
        
        # Now with operators as operands:
        op = Or(Not(BoolVar()), Not(BoolVar()))
        expected = "Or(Not(Anonymous variable [BoolVar]), " \
                      "Not(Anonymous variable [BoolVar]))"
        eq_(unicode(op), expected)
    
    def test_representation(self):
        op = Or(BoolVar(), BoolVar())
        expected = "<Or <Anonymous variable [BoolVar]> " \
                       "<Anonymous variable [BoolVar]>>"
        eq_(repr(op), expected)
        
        # Now with operators as operands:
        op = Or(Not(BoolVar()), Not(BoolVar()))
        expected = "<Or <Not <Anonymous variable [BoolVar]>> " \
                       "<Not <Anonymous variable [BoolVar]>>>"
        eq_(repr(op), expected)


class TestXor(object):
    """Tests for the Xor operator."""
    
    def test_constructor_with_operands(self):
        """The constructor must support actual operands as arguments"""
        Xor(BoolVar(), TrafficLightVar())
    
    def test_constructor_with_operators(self):
        """The constructor must support operators as arguments."""
        Xor(Not(BoolVar()), Not(TrafficLightVar()))
    
    def test_constructor_with_mixed_operands(self):
        """
        The constructor must support operators and actual operands as arguments.
        
        """
        Xor(BoolVar(), Not(TrafficLightVar()))
        Xor(Not(BoolVar()), TrafficLightVar())
    
    def test_with_both_results_as_true(self):
        operation = Xor(BoolVar(), TrafficLightVar())
        assert_false(operation( dict(bool=True, traffic_light="red") ))
    
    def test_with_both_results_as_false(self):
        operation = Xor(BoolVar(), TrafficLightVar())
        assert_false(operation( dict(bool=False, traffic_light="") ))
    
    def test_with_mixed_results(self):
        operation = Xor(BoolVar(), TrafficLightVar())
        ok_(operation( dict(bool=False, traffic_light="red") ))
    
    def test_equivalent(self):
        """
        Two exclusive disjunctions are equivalent if they have the same
        operands.
        
        """
        op1 = Xor(BoolVar(), PedestriansCrossingRoad())
        op2 = Xor(PedestriansCrossingRoad(), BoolVar())
        op3 = Xor(DriversAwaitingGreenLightVar(), BoolVar())
        
        op1.check_equivalence(op2)
        op2.check_equivalence(op1)
        
        assert_raises(AssertionError, op1.check_equivalence, op3)
        assert_raises(AssertionError, op2.check_equivalence, op3)
        assert_raises(AssertionError, op3.check_equivalence, op1)
        assert_raises(AssertionError, op3.check_equivalence, op2)
        
        ok_(op1 == op2)
        ok_(op2 == op1)
        ok_(op1 != op3)
        ok_(op2 != op3)
        ok_(op3 != op1)
        ok_(op3 != op2)
    
    def test_string_representation(self):
        op = Xor(BoolVar(), BoolVar())
        as_unicode = unicode(op)
        eq_("Xor(Anonymous variable [BoolVar], Anonymous variable [BoolVar])",
            as_unicode)
        eq_(as_unicode, str(op))
        
        # Now with an operators as operands:
        op = Xor(Not(BoolVar()), Not(BoolVar()))
        eq_("Xor(Not(Anonymous variable [BoolVar]), " \
            "Not(Anonymous variable [BoolVar]))",
            unicode(op))
    
    def test_representation(self):
        op = Xor(BoolVar(), BoolVar())
        expected = "<Xor <Anonymous variable [BoolVar]> " \
                   "<Anonymous variable [BoolVar]>>"
        eq_(repr(op), expected)
        
        # Now with operators as operands:
        op = Xor(Not(BoolVar()), Not(BoolVar()))
        expected = "<Xor <Not <Anonymous variable [BoolVar]>> "\
                   "<Not <Anonymous variable [BoolVar]>>>"
        eq_(repr(op), expected)


class TestNonConnectiveBinaryOperators(object):
    """
    Tests for non-connective, binary operators.
    
    This is, all the binary operators, excluding And, Or and Xor.
    
    For these tests, I'll use the equality operator to avoid importing the
    base :class:`BinaryOperator`.
    
    """
    
    def test_constructor_with_constants(self):
        """The order must not change when the parameters are constant."""
        l_op = String("hola")
        r_op = String("chao")
        operation = Equal(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variables(self):
        """The order must not change when the parameters are variable."""
        l_op = BoolVar()
        r_op = BoolVar()
        operation = Equal(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variable_before_constant(self):
        """
        The order must not change when the first argument is a variable and the
        other is a constant.
        
        """
        l_op = BoolVar()
        r_op = String("hello")
        operation = Equal(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variable_before_constant(self):
        """
        The order must change when the first argument is a constant and the
        other is a variable.
        
        """
        l_op = String("hello")
        r_op = BoolVar()
        operation = Equal(l_op, r_op)
        eq_(r_op, operation.master_operand)
        eq_(l_op, operation.slave_operand)
    
    def test_equivalent(self):
        """
        Two binary operators are equivalent if they have the same operands.
        
        """
        op1 = Equal(BoolVar(), PedestriansCrossingRoad())
        op2 = Equal(PedestriansCrossingRoad(), BoolVar())
        op3 = Equal(DriversAwaitingGreenLightVar(), BoolVar())
        
        op1.check_equivalence(op2)
        op2.check_equivalence(op1)
        
        assert_raises(AssertionError, op1.check_equivalence, op3)
        assert_raises(AssertionError, op2.check_equivalence, op3)
        assert_raises(AssertionError, op3.check_equivalence, op1)
        assert_raises(AssertionError, op3.check_equivalence, op2)
        
        ok_(op1 == op2)
        ok_(op2 == op1)
        ok_(op1 != op3)
        ok_(op2 != op3)
        ok_(op3 != op1)
        ok_(op3 != op2)
    
    def test_string_representation(self):
        op = Equal(String(u"¿qué hora es?"), BoolVar())
        eq_(u'Equal(Anonymous variable [BoolVar], "¿qué hora es?")',
            unicode(op))
        eq_(str(op), 'Equal(Anonymous variable [BoolVar], "¿qué hora es?")')
    
    def test_representation(self):
        op = Equal(String(u"¿qué hora es?"), BoolVar())
        expected = '<Equal <Anonymous variable [BoolVar]> ' \
                          '<String "¿qué hora es?">>'
        eq_(repr(op), expected)


class TestEqual(object):
    """Tests for the Equality operator."""
    
    def test_constants_evaluation(self):
        operation1 = Equal(String("hola"), String("hola"))
        operation2 = Equal(String("hola"), String("chao"))
        ok_(operation1(None))
        assert_false(operation2(None))
    
    def test_variables_evaluation(self):
        operation = Equal(PedestriansCrossingRoad(),
                                     DriversAwaitingGreenLightVar())
        
        # The pedestrians awaiting the green light to cross the street are
        # the same drivers... Must be a parallel universe!
        context = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("carla", "gustavo")
        }
        ok_(operation(context))
        
        # The pedestrians are different from the drivers... That's my universe!
        context = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("liliana", "carlos")
        }
        assert_false(operation(context))
    
    def test_mixed_evaluation(self):
        operation = Equal(
            PedestriansCrossingRoad(),
            Set(String("gustavo"), String("carla"))
        )
        
        # The same people:
        context = {'pedestrians_crossroad': ("gustavo", "carla")}
        ok_(operation(context))
        
        # Other people:
        context = {'pedestrians_crossroad': ("liliana", "carlos")}
        assert_false(operation(context))


class TestNotEqual(object):
    """Tests for the "not equal" operator."""
    
    def test_constants_evaluation(self):
        operation1 = NotEqual(String("hola"), String("chao"))
        operation2 = NotEqual(String("hola"), String("hola"))
        ok_(operation1(None))
        assert_false(operation2(None))
    
    def test_variables_evaluation(self):
        operation = NotEqual(PedestriansCrossingRoad(),
                                     DriversAwaitingGreenLightVar())
        
        # The pedestrians are different from the drivers... That's my universe!
        context = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("liliana", "carlos")
        }
        ok_(operation(context))
        
        # The pedestrians awaiting the green light to cross the street are
        # the same drivers... Must be a parallel universe!
        context = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("carla", "gustavo")
        }
        assert_false(operation(context))
    
    def test_mixed_evaluation(self):
        operation = NotEqual(
            PedestriansCrossingRoad(),
            Set(String("gustavo"), String("carla"))
        )
        
        # Other people:
        context = {'pedestrians_crossroad': ("liliana", "carlos")}
        ok_(operation(context))
        
        # The same people:
        context = {'pedestrians_crossroad': ("gustavo", "carla")}
        assert_false(operation(context))


class TestInequalities(object):
    """
    Tests for common functionalities in the inequality operators.
    
    Because we shouldn't the base :class:`_InequalityOperator`, we're going to
    use one of its subclasses: LessThan.
    
    """
    
    def test_constructor_with_constants(self):
        """The order must not change when the parameters are constant."""
        l_op = Number(3)
        r_op = Number(4)
        operation = LessThan(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variables(self):
        """The order must not change when the parameters are variables."""
        l_op = PedestriansCrossingRoad()
        r_op = DriversAwaitingGreenLightVar()
        operation = LessThan(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variable_before_constant(self):
        """
        The order must not change when the first parameter is a variable and
        the second is a constant.
        
        """
        l_op = PedestriansCrossingRoad()
        r_op = Number(2)
        operation = LessThan(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)


class TestLessThan(object):
    """Tests for the evaluation of "less than" operations."""
    
    def test_constructor_with_constant_before_variable(self):
        """
        The order *must* change when the first parameter is a constant and
        the second is a variable.
        
        """
        l_op = Number(2)
        r_op = PedestriansCrossingRoad()
        operation = LessThan(l_op, r_op)
        eq_(r_op, operation.master_operand)
        eq_(l_op, operation.slave_operand)
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = LessThan(l_op, r_op)
        assert_false(operation(None))
    
    def test_two_constants(self):
        l_op = Number(3)
        r_op = Number(4)
        operation = LessThan(l_op, r_op)
        ok_(operation(None))
    
    def test_two_variables(self):
        l_op = PedestriansCrossingRoad()
        r_op = NumVar()
        operation = LessThan(l_op, r_op)
        
        # |{"carla"}| < 2   <=>   1 < 2
        context = {
            'pedestrians_crossroad': ("carla", ),
            'num': 2,
        }
        ok_(operation(context))
        
        # |{"carla", "carlos"}| < 1   <=>   2 < 1
        context = {
            'pedestrians_crossroad': ("carla", "carlos"),
            'num': 1,
        }
        assert_false(operation(context))
    
    def test_mixed_arguments(self):
        l_op = PedestriansCrossingRoad()
        r_op = Number(2)
        operation = LessThan(l_op, r_op)
        
        # |{"carla"}| < 2   <=>   1 < 2
        context = {'pedestrians_crossroad': ("carla", )}
        ok_(operation(context))
        
        # |{"carla", "carlos", "liliana"}| < 2   <=>   3 < 2
        context = {'pedestrians_crossroad': ("carla", "carlos", "liliana")}
        assert_false(operation(context))


class TestGreaterThan(object):
    """Tests for the evaluation of "greater than" operations."""
    
    def test_constructor_with_constant_before_variable(self):
        """
        The order *must* change when the first parameter is a constant and
        the second is a variable.
        
        """
        l_op = Number(2)
        r_op = PedestriansCrossingRoad()
        operation = GreaterThan(l_op, r_op)
        eq_(r_op, operation.master_operand)
        eq_(l_op, operation.slave_operand)
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = GreaterThan(l_op, r_op)
        assert_false(operation(None))
    
    def test_two_constants(self):
        l_op = Number(4)
        r_op = Number(3)
        operation = GreaterThan(l_op, r_op)
        ok_(operation(None))
    
    def test_two_variables(self):
        l_op = PedestriansCrossingRoad()
        r_op = NumVar()
        operation = GreaterThan(l_op, r_op)
        
        # |{"carla", "yolmary"}| > 1   <=>   2 > 1
        context = {
            'pedestrians_crossroad': ("carla", "yolmary"),
            'num': 1,
        }
        ok_(operation(context))
        
        # |{"carla", "carlos"}| > 3   <=>   2 > 3
        context = {
            'pedestrians_crossroad': ("carla", "carlos"),
            'num': 3,
        }
        assert_false(operation(context))
    
    def test_mixed_arguments(self):
        l_op = PedestriansCrossingRoad()
        r_op = Number(2)
        operation = GreaterThan(l_op, r_op)
        
        # |{"carla", "yolmary", "manuel"}| > 2   <=>   3 > 2
        context = {'pedestrians_crossroad': ("carla", "yolmary", "manuel")}
        ok_(operation(context))
        
        # |{"carla"}| > 2   <=>   1 > 2
        context = {'pedestrians_crossroad': ("carla", )}
        assert_false(operation(context))


class TestLessEqual(object):
    """Tests for the evaluation of "less than or equal to" operations."""
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = LessEqual(l_op, r_op)
        ok_(operation(None))
    
    def test_two_constants(self):
        l_op = Number(3)
        r_op = Number(4)
        operation = LessEqual(l_op, r_op)
        ok_(operation(None))
    
    def test_two_variables(self):
        l_op = PedestriansCrossingRoad()
        r_op = NumVar()
        operation = LessEqual(l_op, r_op)
        
        # |{"carla"}| < 2   <=>   1 < 2
        context = {
            'pedestrians_crossroad': ("carla", ),
            'num': 2,
        }
        ok_(operation(context))
        
        # |{"carla", "carlos"}| < 1   <=>   2 < 1
        context = {
            'pedestrians_crossroad': ("carla", "carlos"),
            'num': 1,
        }
        assert_false(operation(context))
    
    def test_mixed_arguments(self):
        l_op = PedestriansCrossingRoad()
        r_op = Number(2)
        operation = LessEqual(l_op, r_op)
        
        # |{"carla"}| < 2   <=>   1 < 2
        context = {'pedestrians_crossroad': ("carla", )}
        ok_(operation(context))
        
        # |{"carla", "carlos", "liliana"}| < 2   <=>   1 < 2
        context = {'pedestrians_crossroad': ("carla", "carlos", "liliana")}
        assert_false(operation(context))


class TestGreaterEqual(object):
    """Tests for the evaluation of "greater than or equal to" operations."""
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = GreaterEqual(l_op, r_op)
        ok_(operation(None))
    
    def test_two_constants(self):
        l_op = Number(4)
        r_op = Number(3)
        operation = GreaterEqual(l_op, r_op)
        ok_(operation(None))
    
    def test_two_variables(self):
        l_op = PedestriansCrossingRoad()
        r_op = NumVar()
        operation = GreaterEqual(l_op, r_op)
        
        # |{"carla", "yolmary"}| > 1   <=>   2 > 1
        context = {
            'pedestrians_crossroad': ("carla", "yolmary"),
            'num': 1,
        }
        ok_(operation(context))
        
        # |{"carla", "carlos"}| > 3   <=>   2 > 3
        context = {
            'pedestrians_crossroad': ("carla", "carlos"),
            'num': 3,
        }
        assert_false(operation(context))
    
    def test_mixed_arguments(self):
        l_op = PedestriansCrossingRoad()
        r_op = Number(2)
        operation = GreaterEqual(l_op, r_op)
        
        # |{"carla", "yolmary", "manuel"}| > 2   <=>   3 > 2
        context = {'pedestrians_crossroad': ("carla", "yolmary", "manuel")}
        ok_(operation(context))
        
        # |{"carla"}| > 2   <=>   1 > 2
        context = {'pedestrians_crossroad': ("carla", )}
        assert_false(operation(context))


class TestBelongsTo(object):
    """Tests for the ``∈`` set operator."""
    
    def test_item_and_set(self):
        item = Number(3)
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = BelongsTo(item, set_)
        eq_(operation.master_operand, set_)
        eq_(operation.slave_operand, item)
    
    def test_item_and_non_set(self):
        item = String("Paris")
        set_ = String("France")
        assert_raises(InvalidOperationError, BelongsTo, item, set_)
    
    def test_constant_evaluation(self):
        item = Number(3)
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = BelongsTo(item, set_)
        ok_(operation(None))
    
    def test_variable_evaluation(self):
        item = NumVar()
        set_ = PedestriansCrossingRoad()
        operation = BelongsTo(item, set_)
        
        # 4 ∈ {"madrid", 4}
        context = {
            'num': 4,
            'pedestrians_crossroad': ("madrid", 4)
        }
        ok_(operation(context))
        
        # 4 ∈ {"madrid", "paris", "london"}
        context = {
            'num': 4,
            'pedestrians_crossroad': ("madrid", "paris", "london")
        }
        assert_false(operation(context))


class TestIsSubset(object):
    """Tests for the ``⊂`` set operator."""
    
    def test_set_and_set(self):
        subset = Set(Number(2), Number(4))
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = IsSubset(subset, set_)
        eq_(operation.master_operand, set_)
        eq_(operation.slave_operand, subset)
    
    def test_non_set_and_non_set(self):
        subset = String("Paris")
        set_ = String("France")
        assert_raises(InvalidOperationError, IsSubset, subset, set_)
    
    def test_constant_evaluation(self):
        subset = Set(Number(3), Number(1), Number(7))
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = IsSubset(subset, set_)
        ok_(operation(None))
    
    def test_variable_evaluation(self):
        subset = DriversAwaitingGreenLightVar()
        set_ = PedestriansCrossingRoad()
        operation = IsSubset(subset, set_)
        
        # {"carla"} ⊂ {"carla", "andreina"}
        context = {
            'drivers_trafficlight': ("carla", ),
            'pedestrians_crossroad': ("andreina", "carla")
        }
        ok_(operation(context))
        
        # {"liliana", "carlos"} ⊂ {"manuel", "yolmary", "carla"}
        context = {
            'drivers_trafficlight': ("liliana", "carlos"),
            'pedestrians_crossroad': ("manuel", "yolmary", "carla")
        }
        assert_false(operation(context))


#{ Mock objects


class NumVar(Variable):
    """
    Mock variable which represents a numeric value stored in a context item
    called ``num``.
    
    """
    
    operations = set(["equality", "inequality"])
    
    def to_python(self, context):
        return context['num']
    
    def equals(self, value, context):
        return context['num'] == value
    
    def less_than(self, value, context):
        return context['num'] < value
    
    def greater_than(self, value, context):
        return context['num'] > value


#}
