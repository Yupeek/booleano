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
Class instance placeholders.

A placeholder operand is an object whose evaluation is not done by Booleano
(i.e., the parse tree is handled directly). As a consequence, the Booleano
parser won't verify its existence.

"""
from __future__ import unicode_literals

import six

from booleano.exc import BadCallError, InvalidOperationError
from booleano.operations.core import OPERATIONS
from booleano.operations.operands.core import Operand

__all__ = ("PlaceholderVariable", "PlaceholderFunction")


class PlaceholderInstance(Operand):
    """
    Base class for placeholders of Booleano class instances.

    Initially, placeholder operands support all the operations. It's up to the
    converter to verify if the instance is used correctly.

    """

    operations = OPERATIONS

    def __init__(self, name, namespace_parts=None):
        """

        :param name: The name for this placeholder.
        :type name: basestring
        :param namespace_parts: The identifiers in the namespace that contains
            the placeholder.
        :type namespace_parts: tuple

        """
        self.name = name.lower()
        self.namespace_parts = tuple(namespace_parts or ())

    def check_equivalence(self, node):
        """
        Check that placeholder ``node`` is equivalent to this one.

        :raises AssertionError: If ``node`` is not a placeholder or if it's
            a placeholder but its name is not equal to current one's.

        """
        super(PlaceholderInstance, self).check_equivalence(node)
        assert (
            self.name == node.name and
            self.namespace_parts == node.namespace_parts), \
            'Placeholders "%s" and "%s" are not equivalent' % (self, node)

    def no_evaluation(self, *args, **kwargs):
        """
        Raise an InvalidOperationError exception.

        This method should be called when trying to perform an evaluation on
        a placeholder.

        """
        raise InvalidOperationError("Placeholders cannot be evaluated!")

    # All the evaluation-related operation raise an InvalidOperationError
    to_python = __call__ = equals = less_than = greater_than = belongs_to = is_subset = no_evaluation

    def _namespace_to_unicode(self):
        """Return the namespace as a single Unicode string."""
        return u":".join(self.namespace_parts)


@six.python_2_unicode_compatible
class PlaceholderVariable(PlaceholderInstance):
    """
    Placeholder variable.

    """

    def __str__(self):
        """Return the Unicode representation for this placeholder variable."""
        msg = 'Placeholder variable "%s"' % self.name
        if self.namespace_parts:
            ns = self._namespace_to_unicode()
            msg = "%s at %s" % (msg, ns)
        return msg

    def __repr__(self):
        """Return the representation for this placeholder variable."""
        msg = '<Placeholder variable "%s"' % self.name
        if self.namespace_parts:
            ns = self._namespace_to_unicode()
            msg = '%s at namespace="%s"' % (msg, ns)
        return msg + ">"


@six.python_2_unicode_compatible
class PlaceholderFunction(PlaceholderInstance):
    """
    Placeholder for a function call.

    """
    _is_leaf = False

    def __init__(self, function_name, namespace_parts=None, *arguments):
        """

        :param function_name: The name of the function to be represented.
        :type function_name: basestring
        :param namespace_parts: The identifiers in the namespace that contains
            the placeholder function.
        :type namespace_parts: tuple
        :raises BadCallError: If one of the ``arguments`` is not an
            :class:`Operand`.

        """
        for argument in arguments:
            if not isinstance(argument, Operand):
                raise BadCallError(u'Placeholder function "%s" received a '
                                   'non-operand argument: %s' %
                                   (function_name, argument))
        self.arguments = arguments
        super(PlaceholderFunction, self).__init__(function_name,
                                                  namespace_parts)

    def check_equivalence(self, node):
        """
        Check that placeholder function ``node`` is equivalent to the current
        placeholder function.

        :raises AssertionError: If ``node`` is not a placeholder function, or
            if it's a placeholder function but represents a different function.

        """
        super(PlaceholderFunction, self).check_equivalence(node)
        assert self.arguments == node.arguments, \
            'Placeholder functions "%s" and "%s" were called with ' \
            'different arguments' % (self, node)

    def __str__(self):
        """Return the Unicode representation for this placeholder function."""
        args = [six.text_type(arg) for arg in self.arguments]
        args = ", ".join(args)
        msg = 'Placeholder function call "%s"(%s)' % (self.name, args)
        if self.namespace_parts:
            ns = self._namespace_to_unicode()
            msg = "%s at %s" % (msg, ns)
        return msg

    def __repr__(self):
        """Return the representation for this placeholder function."""
        args = [repr(arg) for arg in self.arguments]
        args = ", ".join(args)
        func_name = self.name
        msg = '<Placeholder function call "%s"(%s)' % (func_name, args)
        if self.namespace_parts:
            ns = self._namespace_to_unicode()
            msg = '%s at namespace="%s"' % (msg, ns)
        return msg + ">"
