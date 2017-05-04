# -*- coding: utf-8 -*-
"""
Exceptions raised by :mod:`booleano`.

"""


class BooleanoException(Exception):
    """
    Base class for the exceptions.

    It is never raised directly, but you can use it to handle any kind of
    exception raised by Booleano.

    """
    pass


# Operation-related errors


class InvalidOperationError(BooleanoException):
    """
    Exception raised when trying to apply an operation on an operand that
    doesn't support it.

    This exception must only be used for static errors in the expressions, not
    runtime errors.

    For example: ``"word" > 10``.

    """
    pass


class BadCallError(InvalidOperationError):
    """
    Exception raised when a function is called with wrong parameters.

    """
    pass


class BadOperandError(BooleanoException):
    """
    Exception raised when an operand is defined incorrectly.

    Because it's aimed at developers, its message doesn't have to be
    translatable.

    """
    pass


class BadFunctionError(BadOperandError):
    """
    Exception raised when a function is defined incorrectly.

    Because it's aimed at developers, its message doesn't have to be
    translatable.

    """
    pass


# Parsing-related exceptions


class ParsingException(BooleanoException):
    """
    Base class for exceptions raised when parsing goes wrong.

    It is never raised directly, but you can use it to handle any kind of
    exception raised by the parser.

    """
    pass


class GrammarError(ParsingException):
    """
    Exception raised when a grammar is defined incorrectly, or an attempt is
    made to use it incorrectly.

    """
    pass


class BadExpressionError(ParsingException):
    """Exception raised when a expression is not a valid boolean expression."""
    pass


class ScopeError(ParsingException):
    """Exception raised when a scope-related item is defined incorrectly."""
    pass


# Conversion-related exceptions


class ConversionError(BooleanoException):
    """
    Exception raised when trying to convert a parse tree, but an invalid node
    was passed.

    """
    pass
