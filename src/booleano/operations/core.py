# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging

import six

from booleano.exc import InvalidOperationError

logger = logging.getLogger(__name__)

OPERATIONS = {"equality", "inequality", "boolean", "membership"}
"""
The known/supported operations.
"""


@six.python_2_unicode_compatible
class OperationNode(object):
    """
    Base class for the individual elements available in a boolean operation
    (i.e., operands and operations).

    It can also be seen as the base class for each node in the parse trees.

    """
    _is_leaf = None

    def __call__(self, context):
        """
        Evaluate the operation, by passing the ``context`` to the inner
        operands/operators.

        :param context: The evaluation context.
        :type context: object
        :return: The logical value of the operation node.
        :rtype: bool

        """
        raise NotImplementedError()

    def check_logical_support(self):
        """
        Make sure this node has and can return its logical value.

        :raises booleano.exc.InvalidOperationError: If the node is an
            **operand** which doesn't support boolean operations.

        All the operators have logical values.

        """
        if self.is_operand():
            self.check_operation("boolean")

    def is_leaf(self):
        """
        Check if this is a leaf node.

        :rtype: bool

        Leaf nodes are those that don't contain other nodes (operands or
        operators): :class:`String`, :class:`Number`, :class:`Variable` and
        :class:`PlaceholderVariable`.

        """
        assert self._is_leaf is not None, "subclass of OperationNode must provide _is_leaf with true or false"
        return self._is_leaf

    def is_branch(self):
        """
        Check if this is a branch node.

        :rtype: bool

        Branch nodes are those that contain other nodes (operands or operators):
        All the operators, plus :class:`Set`, :class:`Function` and
        :class:`PlaceholderFunction`.

        """
        return not self.is_leaf()

    def is_operand(self):
        """
        Check if this node is an operand.

        :rtype: bool

        """
        return False

    def is_operator(self):
        """
        Check if this node is an operation.

        :rtype: bool

        """
        return False

    def check_equivalence(self, node):
        """
        Make sure ``node`` and this node are equivalent.

        :param node: The other node which may be equivalent to this one.
        :type node: :class:`OperationNode`
        :raises AssertionError: If both nodes have different classes.

        Operands and operations must extend this method to check for other
        attributes specific to such nodes.

        """
        error_msg = 'Nodes "%s" and "%s" are not equivalent'
        assert isinstance(node, self.__class__), error_msg % (repr(node),
                                                              repr(self))

    def __hash__(self):
        return id(self)

    def __bool__(self):
        """
        Cancel the pythonic truth evaluation by raising an exception.

        :raises InvalidOperationError: To cancel the pythonic truth evaluation.

        This is disabled in order to prevent users from mistakenly assuming
        they can evaluate operation nodes à la Python, which could lead to
        serious problems because they'd always evaluate to ``True``.

        Operation nodes must be evaluated passing the context explicitly.

        """
        raise InvalidOperationError("Operation nodes do not support Pythonic "
                                    "truth evaluation")

    __nonzero__ = __bool__

    def __eq__(self, other):
        """
        Check if the ``other`` node is equivalent to this one.

        :return: Whether they are equivalent.
        :rtype: bool

        """
        try:
            self.check_equivalence(other)
            return True
        except AssertionError:
            return False

    def __ne__(self, other):
        """
        Check if the ``other`` node is not equivalent to this one.

        :return: Whether they are not equivalent.
        :rtype: bool

        """
        try:
            self.check_equivalence(other)
            return False
        except AssertionError:
            return True

    def __str__(self):
        """
        Return the Unicode representation for this node.

        :raises NotImplementedError: If the Unicode representation is not
            yet implemented.

        """
        return "<%s>" % type(self).__name__

    def __repr__(self):
        """
        Raise a NotImplementedError to force descendants to set the
        representation explicitly.

        """
        raise NotImplementedError("Node %s doesn't have an "
                                  "representation" % type(self))
