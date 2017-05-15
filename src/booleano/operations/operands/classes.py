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
Booleano classes.

There are two types of Booleano classes:
 - Variable.
 - Function.

**Python classes and Booleano classes are two different things!**

"""
from __future__ import unicode_literals

from collections import OrderedDict

import six

from booleano.exc import BadCallError, BadFunctionError
from booleano.operations.operands.core import Operand, _OperandMeta

__all__ = ["Variable", "Function"]


class Class(Operand):
    """
    Base class for Booleano's anonymous classes.

    The classes are anonymous because the have no notion of binding. From the
    Wikipedia:

        In most languages, a class is bound to a name or identifier upon
        definition. However, some languages allow classes to be defined without
        names. Such a class is called an anonymous class (analogous to named vs.
        anonymous functions).

    """

    # Only actual classes should be checked.
    bypass_operation_check = True


@six.python_2_unicode_compatible
class Variable(Class):
    """
    Developer-defined variable.

    """

    # Only actual variables should be checked.
    bypass_operation_check = True

    def __str__(self):
        """Return the Unicode representation of this variable."""
        return 'Anonymous variable [%s]' % self.__class__.__name__

    def __repr__(self):
        """Represent this variable."""
        return "<Anonymous variable [%s]>" % self.__class__.__name__


class _FunctionMeta(_OperandMeta):
    """
    Pre-process user-defined functions right after they've been defined.

    """

    def __init__(cls, name, bases, ns):
        """
        Calculate the arity of the function and create an utility variable
        which will contain all the valid arguments.

        Also checks that there are no duplicate arguments and that each argument
        is an operand.

        """
        # A few short-cuts:
        req_args = ns.get("required_arguments", cls.required_arguments)
        opt_args = ns.get("optional_arguments", cls.optional_arguments)
        if len(opt_args) > 1 and not isinstance(opt_args, OrderedDict):
            raise BadFunctionError('optional_arguments must be a `collection.OrderedDict` instance')
        rargs_set = set(req_args)
        oargs_set = set(opt_args.keys())
        # Checking that are no duplicate entries:
        if len(rargs_set) != len(req_args) or rargs_set & oargs_set:
            raise BadFunctionError('Function "%s" has duplicate arguments'
                                   % name)
        # Checking that the default values for the optional arguments are all
        # operands:
        for (key, value) in opt_args.items():
            if not isinstance(value, Operand):
                raise BadFunctionError('Default value for argument "%s" in '
                                       'function %s is not an operand' %
                                       (key, name))
        # Merging all the arguments into a single list for convenience:
        cls.all_args = tuple(list(req_args) + list(opt_args.keys()))
        # Finding the arity:
        cls.arity = len(cls.all_args)
        # Calling the parent constructor:
        super(_FunctionMeta, cls).__init__(name, bases, ns)


@six.python_2_unicode_compatible
class Function(six.with_metaclass(_FunctionMeta, Class)):
    """
    Base class for **calls** of developer-defined, n-ary functions.

    Instances of this Python class represent calls of the function, not the
    function itself.

    Subclasses must override :meth:`check_arguments` to verify the validity of
    the arguments, or to do nothing if it's not necessary. They must also
    define :attr:`required_arguments` and :attr:`optional_arguments`.

    """

    # Only actual functions should be checked.
    bypass_operation_check = True
    _is_leaf = False

    required_arguments = ()
    """
    The names of the required arguments.

    :type: tuple

    For example, if you have a binary function whose required arguments
    are ``"name"`` and ``"address"``, your function should be defined as::

        from booleano.operations import Function

        class MyFunction(Function):

            # (...)

            required_arguments = ("name", "address")

            # (...)

    """

    optional_arguments = {}
    """
    The optional arguments along with their default values.

    :type: dict

    This is a dictionary whose keys are the argument names and the items
    are their respective default values.

    For example, if you have a binary function whose arguments are both
    optional (``"name"`` and ``"address"``), your function should be
    defined as::

        from booleano.operations import String, Number, Function

        class MyFunction(Function):

            # (...)

            optional_arguments = {
                'id': Number(5),
                'name': String("Gustavo"),
                'address': String("Somewhere in Madrid"),
                }

            # (...)

    Then when it's called without these arguments, their default values
    will be taken.

    """

    arity = 0
    """
    The arity of the function (i.e., the sum of the amount of the required
    arguments and the amount of optional arguments).

    :type: int

    This is set automatically when the class is defined.

    """

    all_args = ()
    """
    The names of all the arguments, required and optional.

    :type: tuple

    This is set automatically when the class is defined.

    """

    def __init__(self, *arguments):
        """

        :raises booleano.exc.BadCallError: If :meth:`check_arguments` finds
            that the ``arguments`` are invalid, or if few arguments are passed,
            or if too much arguments are passed.

        """
        super(Function, self).__init__()
        # Checking the amount of arguments received:
        argn = len(arguments)
        if argn < len(self.required_arguments):
            raise BadCallError("Too few arguments")
        if argn > self.arity:
            raise BadCallError("Too many arguments")
        # Checking that all the arguments are operands:
        for argument in arguments:
            if not isinstance(argument, Operand):
                raise BadCallError('Argument "%s" is not an operand' %
                                   argument)
        # Storing their values:
        self.arguments = OrderedDict()

        for arg_pos in range(len(arguments)):
            arg_name = self.all_args[arg_pos]
            self.arguments[arg_name] = arguments[arg_pos]
        for oname, odefault in self.optional_arguments.items():
            if oname not in self.arguments:
                self.arguments[oname] = odefault
        # Finally, check that all the parameters are correct:
        self.check_arguments()

    def check_arguments(self):
        """
        Check if all the arguments are correct.

        :raises booleano.exc.BadCallError: If at least one of the arguments are
            incorrect.

        **This method must be overridden in subclasses**.

        The arguments dictionary will be available in the :attr:`arguments`
        attribute. If any of them is wrong, this method must raise a
        :class:`BadCallError` exception.

        """
        raise NotImplementedError("Functions must validate the arguments")

    def check_equivalence(self, node):
        """
        Make sure function ``node`` and this function are equivalent.

        :param node: The other function which may be equivalent to this one.
        :type node: Function
        :raises AssertionError: If ``node`` is not a function or if it's a
            function but doesn't have the same arguments as this one OR doesn't
            have the same names as this one.

        """
        super(Function, self).check_equivalence(node)
        assert node.arguments == self.arguments, "Functions %s and %s were called with different arguments" % (
            node,
            self
        )

    def __str__(self):
        """Return the Unicode representation of this function."""
        args = [u'%s=%s' % (k, v) for (k, v) in self.arguments.items()]
        args = ", ".join(args)

        return "Anonymous function call [%s](%s)" % (self.__class__.__name__, args)

    def __repr__(self):
        """
        Represent this function, including its arguments.

        """
        args = ['%s=%s' % (k, repr(v)) for (k, v) in self.arguments.items()]
        args = ", ".join(args)

        return "<Anonymous function call [%s] %s>" % (self.__class__.__name__,
                                                      args)
