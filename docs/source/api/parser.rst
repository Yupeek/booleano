====================================================
:mod:`booleano.parser` -- Boolean expressions parser
====================================================

Grammar definition
==================

.. autoclass:: booleano.parser.grammar.Grammar
    :members: default_tokens
    :inherited-members:

Test utilities
--------------

.. autoclass:: booleano.parser.testutils.BaseGrammarTest


Scope definition / name binding
===============================


.. automodule:: booleano.parser.scope
    :synopsis: Scope definition & name binding

.. autoclass:: Bind
    :inherited-members:

.. autoclass:: SymbolTable
    :inherited-members:

.. autoclass:: Namespace


Parse managers
==============


.. automodule:: booleano.parser.core
    :synopsis: Boolean parsers and utilities

A parse manager controls the parsers to be used in a single kind of expression,
with one parser per supported grammar.

.. autoclass:: EvaluableParseManager
    :inherited-members:

.. autoclass:: ConvertibleParseManager
    :inherited-members:


Parsers
=======

.. automodule:: booleano.parser.parsers
    :synopsis: Boolean parsers
    :show-inheritance:

.. autoclass:: Parser

.. autoclass:: EvaluableParser

.. autoclass:: ConvertibleParser


Parse trees
===========

.. automodule:: booleano.parser.trees
    :synopsis: Parse trees
    :members: ParseTree, EvaluableParseTree, ConvertibleParseTree
    :show-inheritance:
