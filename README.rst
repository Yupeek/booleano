=========================================
Booleano: Boolean Expressions Interpreter
=========================================



**Booleano** is an interpreter of `boolean expressions
<http://en.wikipedia.org/wiki/Boolean_expression>`_, a library to **define
and run filters** available as text (e.g., in a natural language) or in
`Python <http://python.org/>`_ code.


stable branche

.. image:: https://img.shields.io/travis/Yupeek/booleano/master.svg
    :target: https://travis-ci.org/Yupeek/booleano

.. image:: https://readthedocs.org/projects/booleano/badge/?version=latest
    :target: http://booleano.readthedocs.org/en/latest/

.. image:: https://coveralls.io/repos/github/Yupeek/booleano/badge.svg?branch=master
    :target: https://coveralls.io/github/Yupeek/booleano?branch=master

.. image:: https://img.shields.io/pypi/v/booleano.svg
    :target: https://pypi.python.org/pypi/booleano
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/booleano.svg
    :target: https://pypi.python.org/pypi/booleano
    :alt: Number of PyPI downloads per month

.. image:: https://codeclimate.com/github/Yupeek/booleano/badges/gpa.svg
   :target: https://codeclimate.com/github/Yupeek/booleano
   :alt: Code Climate


development status

.. image:: https://img.shields.io/travis/Yupeek/booleano/develop.svg
    :target: https://travis-ci.org/Yupeek/booleano

.. image:: https://coveralls.io/repos/github/Yupeek/booleano/badge.svg?branch=develop
    :target: https://coveralls.io/github/Yupeek/booleano?branch=develop


In order to handle text-based filters, Booleano ships with a fully-featured
parser whose grammar is `adaptive
<http://en.wikipedia.org/wiki/Adaptive_grammar>`_: Its properties
can be overridden using simple configuration directives.

On the other hand, the library exposes a pythonic API for filters written
in pure Python. These filters are particularly useful to build reusable
conditions from objects provided by a third party library.

TLDR;
-----

a string + some variable = safe boolean evaluation

.. code:: python

    # is this character a minor guy with a "0" in his name and born after 1983 ?
    eval_boolean(
        'age < const:majority & "o" in name & birthdate > "1983-02-02"',
        {"name": "sokka", "age": 15, "birthdate": datetime.date(1984, 1, 1)},
        {'majority': 18},
        grammar_tokens={'belongs_to': 'in'}
    ) => True



The Fun Use Case
----------------

Booleano allow to safely evaluate an expression into something usable.

- ``user:name is "john" and user:surname in {"doe", "shepard"}``


+``{"user": {"name": "katara"}}`` => False
+``{"user": {"name": "john", "surname": "doe"}}`` => True

with some code, you can provide any type you want, and the expression can still be in text:

+``user:birthdate > "03-07-1987"``
+``duration > 1m30s``

check the sample dirrectory to view more running examples !


Documentation
-------------

The full documentation is at http://django-rest-models.readthedocs.org/en/latest/.


Contribute
----------

this project was not created by the current maintainer. in fact, the knowlege of this project from us is fare from
perfect, but with 100% of test coverages, it's not hard to keep it running.

if you find a bug, or want some feature, feel free to create a issues, or a Pull Request, but keep in mind that
it can be hard for us to work on it. the best way to have it fixed, it's to write a Pull Request with passing tests,
and we will merge it if it's a good piece of code.

see CONTRIBUTING.rst to know how work with ease on this project.

Upgrade Note
------------

the old alpha release 1.0a1 is not compatible with newer version (starting with 1.1a1) because of heavy
import path changes. all import from the modules (__init__.py) is discouraged.


Credit
------

**forked** from  Gustavo Narea's booleano project on `launchpad.net <https://launchpad.net/booleano>`_.

**maintened** by yupeek


Links
-----

* `Web site <https://github.com/Yupeek/booleano>`_.
* `Bug reports <https://github.com/Yupeek/booleano/issues>`_.
