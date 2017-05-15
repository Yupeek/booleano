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
Constant operands.

"""
from __future__ import unicode_literals

import six

from booleano.exc import InvalidOperationError
from booleano.operations.operands.core import Operand
from booleano.parser.symbol_table_builder import SymbolTableBuilder

__all__ = ["String", "Number", "Set"]

constants_symbol_table_builder = SymbolTableBuilder(use_key=False)


@constants_symbol_table_builder.register(type(None))
@six.python_2_unicode_compatible
class Constant(Operand):
    """
    Base class for constant operands.

    The only operation that is common to all the constants is equality (see
    :meth:`equals`).

    Constants don't rely on the context -- they are constant!

    if the value given to a Constant is None, all operation will resolve to False
    """

    operations = {'equality', 'inequality', 'boolean'}

    def __init__(self, constant_value):
        """

        :param constant_value: The Python value represented by the Booleano
            constant.
        :type constant_value: :class:`object`

        """
        self.constant_value = constant_value

    def to_python(self, context):
        """
        Return the value represented by this constant.

        """
        return self.constant_value

    def equals(self, value, context):
        """
        Check if this constant equals ``value``.

        """
        return self.constant_value is not None and self.constant_value == value

    def greater_than(self, value, context):
        return self.constant_value is not None and self.constant_value > value

    def less_than(self, value, context):
        return self.constant_value is not None and self.constant_value < value

    def check_equivalence(self, node):
        """
        Make sure constant ``node`` and this constant are equivalent.

        :param node: The other constant which may be equivalent to this one.
        :type node: Constant
        :raises AssertionError: If the constants are of different types or
            represent different values.

        """
        super(Constant, self).check_equivalence(node)
        assert node.constant_value == self.constant_value, u'Constants %s and %s represent different values' % (
            self,
            node
        )

    def __call__(self, context):
        """Does this variable evaluate to True?"""
        return bool(self.constant_value)

    def __str__(self):
        """Return the Unicode representation of this constant string."""
        return u'%r' % self.constant_value

    def __repr__(self):
        """Return the representation for this constant string."""
        return '<Constant %r>' % self.constant_value


@constants_symbol_table_builder.register(six.text_type)
@six.python_2_unicode_compatible
class String(Constant):
    u"""
    Constant string.
    this support native python resulution for membership, equiality and inequality
    """
    operations = {
        "equality",  # ==, !=
        "inequality",  # >, <, >=, <=
        "boolean",  # Logical values
        "membership",
    }

    def __init__(self, string):
        """

        :param string: The Python string to be represented by this Booleano
            string.
        :type string: :class:`basestring`

        ``string`` will be converted to :class:`unicode`, so it doesn't
        have to be a :class:`basestring` initially.

        """
        string = six.text_type(string)
        super(String, self).__init__(string)

    def equals(self, value, context):
        value = six.text_type(value)
        return super(String, self).equals(value, context)

    def belongs_to(self, value, context):
        value = six.text_type(value)
        return value in self.constant_value

    def is_subset(self, value, context):
        value = six.text_type(value)
        return value != self.constant_value and value in self.constant_value

    def greater_than(self, value, context):
        value = six.text_type(value)
        return self.constant_value > value

    def less_than(self, value, context):
        value = six.text_type(value)
        return self.constant_value < value

    def __call__(self, context):
        """Does this variable evaluate to True?"""
        return bool(six.text_type(self.constant_value))

    def __str__(self):
        """Return the Unicode representation of this constant string."""
        return u'"%s"' % self.constant_value

    def __repr__(self):
        """Return the representation for this constant string."""
        return '<String "%s">' % self.constant_value


@constants_symbol_table_builder.register(int)
@constants_symbol_table_builder.register(float)
@six.python_2_unicode_compatible
class Number(Constant):
    """
    Numeric constant.

    These constants support inequality operations; see :meth:`greater_than`
    and :meth:`less_than`.

    """

    operations = Constant.operations | set(['inequality'])

    def __init__(self, number):
        """

        :param number: The number to be represented, as a Python object.
        :type number: :class:`object`

        ``number`` is converted into a :class:`float` internally, so it can
        be an :class:`string <basestring>` initially.

        """
        number = float(number)
        super(Number, self).__init__(number)

    def equals(self, value, context):
        """
        Check if this numeric constant equals ``value``.

        :raises InvalidOperationError: If ``value`` can't be turned into a
            float.

        ``value`` will be turned into a float prior to the comparison, to
        support strings.

        """
        return super(Number, self).equals(self._to_number(value), context)

    def greater_than(self, value, context):
        """
        Check if this numeric constant is greater than ``value``.

        :raises InvalidOperationError: If ``value`` can't be turned into a
            float.

        ``value`` will be turned into a float prior to the comparison, to
        support strings.

        """
        return self.constant_value > self._to_number(value)

    def less_than(self, value, context):
        """
        Check if this numeric constant is less than ``value``.

        :raises InvalidOperationError: If ``value`` can't be turned into a
            float.

        ``value`` will be turned into a float prior to the comparison, to
        support strings.

        """
        return self.constant_value < self._to_number(value)

    def _to_number(self, value):
        """
        Convert ``value`` to a Python float and return the new value.

        :param value: The value to be converted into float.
        :return: The value as a float.
        :rtype: float
        :raises InvalidOperationError: If ``value`` can't be converted.

        """
        try:
            return float(value)
        except ValueError:
            raise InvalidOperationError('"%s" is not a number' % value)

    def __str__(self):
        """Return the Unicode representation of this constant number."""
        return six.text_type(self.constant_value)

    def __repr__(self):
        """Return the representation for this constant number."""
        return '<Number %s>' % self.constant_value


@constants_symbol_table_builder.register(set)
@constants_symbol_table_builder.register(frozenset)
@six.python_2_unicode_compatible
class Set(Constant):
    """
    Constant sets.

    These constants support membership operations; see :meth:`contains` and
    :meth:`is_subset`.

    """
    _is_leaf = False

    operations = Constant.operations | set(["inequality", "membership"])

    def __init__(self, *items):
        """

        :raises booleano.exc.InvalidOperationError: If at least one of the
            ``items`` is not an operand.

        """
        for item in items:
            if not isinstance(item, Operand):
                raise InvalidOperationError('Item "%s" is not an operand, so '
                                            'it cannot be a member of a set' %
                                            item)
        super(Set, self).__init__(set(items))

    def to_python(self, context):
        """
        Return a set made up of the Python representation of the operands
        contained in this set.

        """
        items = set(item.to_python(context) for item in self.constant_value)
        return items

    def equals(self, value, context):
        """Check if all the items in ``value`` are the same of this set."""
        value = set(value)
        return value == self.to_python(context)

    def less_than(self, value, context):
        """
        Check if this set has less items than the number represented in
        ``value``.

        :raises InvalidOperationError: If ``value`` is not an integer.

        """
        value = self._to_int(value)
        return len(self.constant_value) < value

    def greater_than(self, value, context):
        """
        Check if this set has more items than the number represented in
        ``value``.

        :raises InvalidOperationError: If ``value`` is not an integer.

        """
        value = self._to_int(value)
        return len(self.constant_value) > value

    def belongs_to(self, value, context):
        """
        Check that this constant set contains the ``value`` item.

        """
        for item in self.constant_value:
            try:
                if item.equals(value, context):
                    return True
            except InvalidOperationError:
                continue
        return False

    def is_subset(self, value, context):
        """
        Check that the ``value`` set is a subset of this constant set.

        """
        for item in value:
            if not self.belongs_to(item, context):
                return False
        return True

    def check_equivalence(self, node):
        """
        Make sure set ``node`` and this set are equivalent.

        :param node: The other set which may be equivalent to this one.
        :type node: Set
        :raises AssertionError: If ``node`` is not a set or it's a set
            with different elements.

        """
        Operand.check_equivalence(self, node)

        unmatched_elements = list(self.constant_value)
        assert len(unmatched_elements) == len(node.constant_value), 'Sets %s and %s do not have ' \
                                                                    'the same cardinality' % (
            unmatched_elements,
            node
        )

        # Checking that each element is represented by a mock operand:
        for element in node.constant_value:
            for key in range(len(unmatched_elements)):
                if unmatched_elements[key] == element:
                    del unmatched_elements[key]
                    break

        assert 0 == len(unmatched_elements), 'No match for the following elements: %s' % unmatched_elements

    def __str__(self):
        """Return the Unicode representation of this constant set."""
        elements = [six.text_type(element) for element in self.constant_value]
        elements = u", ".join(elements)
        return "{%s}" % elements

    def __repr__(self):
        """Return the representation for this constant set."""
        elements = [repr(element) for element in self.constant_value]

        elements = ", ".join(elements)
        if elements:
            elements = " " + elements
        return '<Set%s>' % elements

    @classmethod
    def _to_int(cls, value):
        """
        Convert ``value`` is to integer if possible.

        :param value: The value to be verified.
        :return: ``value`` as integer.
        :rtype: int
        :raises InvalidOperationError: If ``value`` is not an integer.

        This is a workaround for Python < 2.6, where floats didn't have the
        ``.is_integer()`` method.

        """
        try:
            value_as_int = int(value)
            is_int = value_as_int == float(value)
        except (ValueError, TypeError):
            is_int = False
        if not is_int:
            raise InvalidOperationError("To compare the amount of items in a "
                                        "set, the operand %s has to be an "
                                        "integer" % repr(value))
        return value_as_int
