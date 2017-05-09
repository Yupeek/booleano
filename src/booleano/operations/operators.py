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
Built-in operators.

"""
from __future__ import unicode_literals

import six

from booleano.operations.core import OperationNode
from booleano.operations.operands import Variable

__all__ = ("Not", "And", "Or", "Xor", "Equal", "NotEqual", "LessThan",
           "GreaterThan", "LessEqual", "GreaterEqual", "BelongsTo", "IsSubset")


class Operator(OperationNode):
    """
    Base class for logical operators.

    The operands to be used by the operator must be passed in the constructor.

    """
    _is_leaf = False

    def is_operator(self):
        """
        Check if this node is an operation.

        :rtype: bool

        """
        return True


@six.python_2_unicode_compatible
class UnaryOperator(Operator):
    """
    Base class for unary logical operators.

    """

    def __init__(self, operand):
        """
        Check that ``operand`` supports all the required operations before
        storing it.

        :param operand: The operand handled by this operator.
        :type operand: :class:`booleano.operations.Operand`

        """
        self.operand = operand

    def check_equivalence(self, node):
        """
        Make sure unary operator ``node`` and this unary operator are
        equivalent.

        :param node: The other operator which may be equivalent to this one.
        :type node: UnaryOperator
        :raises AssertionError: If ``node`` is not a unary operator or if it's
            an unary operator but doesn't have the same operand as this one.

        """
        super(UnaryOperator, self).check_equivalence(node)
        assert node.operand == self.operand, 'Operands of unary operations %s and %s are not equivalent' % (
            node,
            self
        )

    def __hash__(self):
        return id(self)

    def __str__(self):
        """
        Return the Unicode representation for this operator and its operand.

        """
        operand = six.text_type(self.operand)
        return u"%s(%s)" % (self.__class__.__name__, operand)

    def __repr__(self):
        """Return the representation for this operator and its operand."""
        operand = repr(self.operand)
        return "<%s %s>" % (self.__class__.__name__, operand)


@six.python_2_unicode_compatible
class BinaryOperator(Operator):
    """
    Base class for binary logical operators.

    In binary operations, the two operands are marked as "master" or "slave".
    The binary operator will make the *master operand* perform the requested
    operation using the Python value of the *slave operand*. This is found by
    the :meth:`organize_operands` method, which can be overridden.

    .. attribute:: master_operand

        The instance attribute that represents the master operand.

    .. attribute:: slave_operand

        The instance attribute that represents the slave operand.

    """

    def __init__(self, left_operand, right_operand):
        """
        Instantiate this operator, finding the master operand among
        ``left_operand`` and ``right_operand``.

        :param left_operand: The left-hand operand handled by this operator.
        :type left_operand: :class:`booleano.operations.Operand`
        :param right_operand: The right-hand operand handled by this operator.
        :type right_operand: :class:`booleano.operations.Operand`

        """
        master, slave = self.organize_operands(left_operand, right_operand)
        self.master_operand = master
        self.slave_operand = slave

    def organize_operands(self, left_operand, right_operand):
        """
        Find the master and slave operands among the ``left_operand`` and
        ``right_operand`` operands.

        :param left_operand: The left-hand operand handled by this operator.
        :type left_operand: :class:`booleano.operations.Operand`
        :param right_operand: The right-hand operand handled by this operator.
        :type right_operand: :class:`booleano.operations.Operand`
        :return: A pair where the first item is the master operand and the
            second one is the slave.
        :rtype: tuple

        In practice, they are only distinguished when one of the operands is a
        variable and the other is a constant. In such situations, the variable
        becomes the master operand and the constant becomes the slave operand.

        When both operands are constant or both are variable, the left-hand
        operand becomes the master and the right-hand operand becomes the slave.

        """
        l_var = isinstance(left_operand, Variable)
        r_var = isinstance(right_operand, Variable)

        if l_var == r_var or l_var:
            # Both operands are variable/constant, OR the left-hand operand is
            # a variable and the right-hand operand is a constant.
            return (left_operand, right_operand)

        # The right-hand operand is the variable and the left-hand operand the
        # constant:
        return (right_operand, left_operand)

    def check_equivalence(self, node):
        """
        Make sure binary operator ``node`` and this binary operator are
        equivalent.

        :param node: The other operator which may be equivalent to this one.
        :type node: BinaryOperator
        :raises AssertionError: If ``node`` is not a binary operator or if it's
            an binary operator but doesn't have the same operands as this one.

        """
        super(BinaryOperator, self).check_equivalence(node)
        same_operands = (
            (
                node.master_operand == self.master_operand and
                node.slave_operand == self.slave_operand
            ) or (
                node.master_operand == self.slave_operand and
                self.master_operand == node.slave_operand
            )
        )
        assert same_operands, 'Operands of binary operations %s and %s are not equivalent' % (
            node,
            self
        )

    def __str__(self):
        """
        Return the Unicode representation for this binary operator, including
        its operands.

        """
        return u"%s(%s, %s)" % (self.__class__.__name__, self.master_operand,
                                self.slave_operand)

    def __repr__(self):
        """
        Return the representation for this binary operator, including its
        operands.

        """
        return "<%s %s %s>" % (self.__class__.__name__,
                               repr(self.master_operand),
                               repr(self.slave_operand))


# Unary operators


class Not(UnaryOperator):
    """
    The logical negation (``~``).

    Negate the boolean representation of an operand.

    """

    def __init__(self, operand):
        """

        :raises booleano.exc.InvalidOperationError: If ``operand`` doesn't have
            a logical value.

        """
        operand.check_logical_support()
        super(Not, self).__init__(operand)

    def __call__(self, context):
        """
        Return the negate of the truth value for the operand.

        :param context: The evaluation context.
        :type context: object

        """
        return not self.operand(context)


# Binary operators


class _ConnectiveOperator(BinaryOperator):
    """
    Logic connective to turn the left-hand and right-hand operands into
    boolean operations, so we can manipulate their truth value easily.

    """

    def __init__(self, left_operand, right_operand):
        """

        :raises booleano.exc.InvalidOperationError: If ``left_operand`` or
            ``right_operand`` doesn't have logical values.

        """
        left_operand.check_logical_support()
        right_operand.check_logical_support()
        super(_ConnectiveOperator, self).__init__(left_operand, right_operand)


class And(_ConnectiveOperator):
    """
    The logical conjunction (``AND``).

    Connective that checks if two operations evaluate to ``True``.

    With this binary operator, the operands can be actual operands or
    operations.

    """

    def __call__(self, context):
        """
        Check if both operands evaluate to ``True``.

        :param context: The evaluation context.
        :type context: objects

        """
        return self.master_operand(context) and self.slave_operand(context)


class Or(_ConnectiveOperator):
    """
    The logical inclusive disjunction (``OR``).

    Connective that check if at least one, out of two operations, evaluate to
    ``True``.

    With this binary operator, the operands can be actual operands or
    operations.

    """

    def __call__(self, context):
        """
        Check if at least one of the operands evaluate to ``True``.

        :param context: The evaluation context.
        :type context: object

        """
        return self.master_operand(context) or self.slave_operand(context)


class Xor(_ConnectiveOperator):
    """
    The logical exclusive disjunction (``XOR``).

    Connective that checks if only one, out of two operations, evaluate to
    ``True``.

    With this binary operator, the operands can be actual operands or
    operations.

    """

    def __call__(self, context):
        """
        Check that only one of the operands evaluate to ``True``.

        :param context: The evaluation context.
        :type context: object

        """
        return self.master_operand(context) ^ self.slave_operand(context)


class Equal(BinaryOperator):
    """
    The equality operator (``==``).

    Checks that two operands are equivalent.

    For example: ``3 == 3``.

    """

    def __init__(self, left_operand, right_operand):
        """

        :param left_operand: The left-hand operand handled by this operator.
        :type left_operand: :class:`booleano.operations.Operand`
        :param right_operand: The right-hand operand handled by this operator.
        :type right_operand: :class:`booleano.operations.Operand`
        :raises booleano.exc.InvalidOperationError: If the master operand
            between ``left_operand`` or ``right_operand`` doesn't support
            equality operations.

        """
        super(Equal, self).__init__(left_operand, right_operand)
        self.master_operand.check_operation("equality")

    def __call__(self, context):
        value = self.slave_operand.to_python(context)
        return self.master_operand.equals(value, context)


# (x <> y) <=> ~(x == y)
class NotEqual(Equal):
    """
    The "not equal to" operator (``!=``).

    Checks that two operands are not equivalent.

    For example: ``3 != 2``.

    """

    def __call__(self, context):
        return not super(NotEqual, self).__call__(context)


class _InequalityOperator(BinaryOperator):
    """
    Handle inequalities (``<``, ``>``) and switch the operation if the operands
    are rearranged.

    """

    def __init__(self, left_operand, right_operand, comparison):
        """
        Switch the ``comparison`` if the operands are rearranged.

        :param left_operand: The original left-hand operand in the inequality.
        :param right_operand: The original right-hand operand in the
            inequality.
        :param comparison: The symbol for the particular inequality (i.e.,
            "<" or ">").
        :raises InvalidOperationError: If the master operand doesn't support
            inequalities.

        If the operands are rearranged by :meth:`organize_operands`, then
        the operation must be switched (e.g., from "<" to ">").

        This will also "compile" the comparison operation; otherwise, it'd have
        to be calculated on a per evaluation basis.

        """
        super(_InequalityOperator, self).__init__(left_operand, right_operand)

        self.master_operand.check_operation("inequality")

        if left_operand != self.master_operand:
            # The operands have been rearranged! Let's invert the comparison:
            if comparison == "<":
                comparison = ">"
            else:
                comparison = "<"

        # "Compiling" the comparison:
        if comparison == ">":
            self.comparison = self._greater_than
        else:
            self.comparison = self._less_than

    def __call__(self, context):
        return self.comparison(context)

    def _greater_than(self, context):
        """Check if the master operand is greater than the slave"""
        value = self.slave_operand.to_python(context)
        return self.master_operand.greater_than(value, context)

    def _less_than(self, context):
        """Check if the master operand is less than the slave"""
        value = self.slave_operand.to_python(context)
        return self.master_operand.less_than(value, context)


class LessThan(_InequalityOperator):
    """
    The "less than" operator (``<``).

    For example: ``2 < 3``.

    """

    def __init__(self, left_operand, right_operand):
        super(LessThan, self).__init__(left_operand, right_operand, "<")


class GreaterThan(_InequalityOperator):
    """
    The "greater than" operator (``>``).

    For example: ``3 > 2``.

    """

    def __init__(self, left_operand, right_operand):
        super(GreaterThan, self).__init__(left_operand, right_operand, ">")


# (x <= y) <=> ~(x > y)
class LessEqual(GreaterThan):
    """
    The "less than or equal to" operator (``<=``).

    For example: ``2 <= 3``.

    """

    def __call__(self, context):
        return not super(LessEqual, self).__call__(context)


# (x >= y) <=> ~(x < y)
class GreaterEqual(LessThan):
    """
    The "greater than or equal to" operator (``>=``).

    For example: ``2 >= 2``.

    """

    def __call__(self, context):
        return not super(GreaterEqual, self).__call__(context)


class _SetOperator(BinaryOperator):
    """
    Base class for set-related operators.

    """

    def __init__(self, left_operand, right_operand):
        """

        :raises booleano.exc.InvalidOperationError: If ``right_operand``
            doesn't support membership operations.

        """
        super(_SetOperator, self).__init__(left_operand, right_operand)
        self.master_operand.check_operation("membership")

    def organize_operands(self, left_operand, right_operand):
        """Set the set (right-hand operand) as the master operand."""
        return (right_operand, left_operand)


class BelongsTo(_SetOperator):
    """
    The "belongs to" operator (``∈``).

    For example: ``"valencia" ∈ {"caracas", "maracay", "valencia"}``.

    """

    def __call__(self, context):
        value = self.slave_operand.to_python(context)
        return self.master_operand.belongs_to(value, context)


class IsSubset(_SetOperator):
    """
    The "is a subset of" operator (``⊂``).

    For example: ``{"valencia", "aragua"} ⊂ {"caracas", "aragua", "valencia"}``.

    """

    def __call__(self, context):
        value = self.slave_operand.to_python(context)
        return self.master_operand.is_subset(value, context)
