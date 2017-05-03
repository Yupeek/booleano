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
Exceptions raised by :mod:`booleano`.

"""


class BooleanoException(Exception):
    """
    Base class for the exceptions.
    
    It is never raised directly, but you can use it to handle any kind of
    exception raised by Booleano.
    
    """
    pass


#{ Operation-related errors


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


#{ Parsing-related exceptions


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


#{ Conversion-related exceptions


class ConversionError(BooleanoException):
    """
    Exception raised when trying to convert a parse tree, but an invalid node
    was passed.
    
    """
    pass


#}
