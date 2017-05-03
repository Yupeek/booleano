====================================================
:mod:`booleano.parser` -- Boolean expressions parser
====================================================

.. automodule:: booleano.parser
    :synopsis: Boolean parsers and utilities


Grammar definition
==================

.. autoclass:: Grammar
    :members: default_tokens
    :inherited-members:

Test utilities
--------------

.. autoclass:: booleano.parser.testutils.BaseGrammarTest


Scope definition / name :term:`binding`
=======================================

.. autoclass:: Bind
    :inherited-members:

.. autoclass:: SymbolTable
    :inherited-members:

.. autoclass:: booleano.parser.scope.Namespace


Parse managers
==============

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
