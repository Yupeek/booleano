=====================================================
:mod:`booleano.operations` -- Boolean Operation Nodes
=====================================================

.. automodule:: booleano.operations
    :synopsis: Boolean operation nodes and utilities
    :show-inheritance:


.. autoclass:: OperationNode
    :members: __call__, is_branch, is_leaf, is_operand, is_operator

Operands
========

.. autoclass:: booleano.operations.operands.Operand

.. inheritance-diagram:: String Number Set Variable Function PlaceholderVariable 
    PlaceholderFunction
    :parts: 1

Constants
---------

.. autoclass:: booleano.operations.operands.constants.Constant

.. autoclass:: String

.. autoclass:: Number

.. autoclass:: Set


Classes
-------

Note we're talking about **Booleano classes**, not Python classes. These are
used in :term:`evaluable parsing`.

.. autoclass:: booleano.operations.operands.classes.Class

.. autoclass:: Variable
    :members:

.. autoclass:: Function
    :members:


Placeholder instances
---------------------

Note we're talking about **placeholders for instances of Booleano classes**,
not Python class instances. These are used in :term:`convertible parsing`.

.. autoclass:: booleano.operations.operands.placeholders.PlaceholderInstance

.. autoclass:: PlaceholderVariable

.. autoclass:: PlaceholderFunction


Operators
=========

Logical connectives
-------------------

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
