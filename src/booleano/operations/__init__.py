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
Boolean operation nodes and utilities.

In other words, this package contains the elements of the parse trees.

Once parsed, the binary expressions are turned into the relevant operation
using the classes provided by this package.

"""
from __future__ import unicode_literals

from booleano.operations.operands.classes import Function, Variable
from booleano.operations.operands.constants import Number, Set, String
from booleano.operations.operands.placeholders import PlaceholderFunction, PlaceholderVariable
from booleano.operations.operators import (And, BelongsTo, Equal, GreaterEqual, GreaterThan, IsSubset, LessEqual,
                                           LessThan, Not, NotEqual, Or, Xor)

__all__ = (
    # Operands:
    "String", "Number", "Set", "Variable", "Function", "PlaceholderVariable",
    "PlaceholderFunction",
    # Operators:
    "Not", "And", "Or", "Xor", "Equal", "NotEqual", "LessThan", "GreaterThan",
    "LessEqual", "GreaterEqual", "BelongsTo", "IsSubset",
)
