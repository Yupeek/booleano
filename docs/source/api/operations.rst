=====================================================
:mod:`booleano.operations` -- Boolean Operation Nodes
=====================================================

.. automodule:: booleano.operations.core
    :synopsis: Boolean operation nodes and utilities
    :show-inheritance:


.. autoclass:: OperationNode
    :members: __call__, is_branch, is_leaf, is_operand, is_operator

Operands
========

.. autoclass:: booleano.operations.operands.core.Operand

Constants
---------

.. automodule:: booleano.operations.operands.constants
    :synopsis: Boolean operation nodes and utilities
    :show-inheritance:

.. autoclass:: Constant

.. autoclass:: String

.. autoclass:: Number

.. autoclass:: Set


Classes
-------

Note we're talking about **Booleano classes**, not Python classes. These are
used in evaluable parsing.

.. automodule:: booleano.operations.operands.classes

.. autoclass:: Class

.. autoclass:: Variable
    :members:

.. autoclass:: Function
    :members:

Variables
---------

.. automodule:: booleano.operations.variables
    :members: NativeVariable, NativeCollectionVariable, NumberVariable, BooleanVariable, StringVariable, SetVariable,
        DurationVariable, DateTimeVariable, DateVariable


Placeholder instances
---------------------

Note we're talking about **placeholders for instances of Booleano classes**,
not Python class instances. These are used in convertible parsing.

.. automodule:: booleano.operations.operands.placeholders

.. autoclass:: PlaceholderInstance

.. autoclass:: PlaceholderVariable

.. autoclass:: PlaceholderFunction


Operators
=========

Logical connectives
-------------------

.. automodule:: booleano.operations.operators


.. autoclass:: Not

.. autoclass:: And

.. autoclass:: Xor

.. autoclass:: Or

Relational operators
--------------------

.. autoclass:: Equal

.. autoclass:: NotEqual

.. autoclass:: LessThan

.. autoclass:: GreaterThan

.. autoclass:: LessEqual

.. autoclass:: GreaterEqual

Membership operators
--------------------

.. autoclass:: BelongsTo

.. autoclass:: IsSubset


Parse tree converters
=====================

.. automodule:: booleano.operations.converters
    
    .. autoclass:: BaseConverter
        :members:
        
        .. automethod:: __call__
