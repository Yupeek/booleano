==========================
Evaluable Parsing Tutorial
==========================


.. automodule:: booleano

Overview
========

this tutorial will show how to build a parser step by step, and then use it
to check for a set of data, if the statment is true of false

What you need
=============

You need an :class:`evaluable parse manager 
<booleano.parser.EvaluableParseManager>` configured with a
:class:`symbol table <booleano.parser.SymbolTable>` and at least one
:class:`grammar <booleano.parser.Grammar>`, as well as define all the Booleano
variables and functions that may be used in the expressions.




Defining your Grammar
---------------------

the Grammar is the set of word used to understant your boolean expression.
the default Grammar use the mathematical symbol, like the and=&, or=|, belongs_to=∈

to know all default Grammar tokens:

.. code:: python

    Grammar().get_all_tokens()

this retrieve all token from a default Grammar.

to customize some of the token, you just create your Grammar with the token as keyword:

.. code:: python

    from booleano.parser.grammar import Grammar
    my_custom_grammar = Grammar(belongs_to='in')
    my_other_custom_grammar = Grammar(**{'and': 'and', 'or': 'or', 'belongs_to': 'in'})

with this grammar, you can now write ``{1} in {1, 2, 3} and name == "katara"`` instead of
``{1} ∈ {1, 2, 3} & name == "katara"``



Build your symbol table
-----------------------


to allow the parser to validate your synthax, you must provide a set of symbol specific for your expression. think
of it as a set of variables defined in advances.

your symbol tables can be some Constants, a Variable or a Function.

the creation of a SymbolTable require a name, a set of bound symbols, and optionaly some sub SymbolTables.

to bound a symbol, you must pass :class:`Bind` instance to the SymbolTable. the first argument is the name
of the object into the expression, and the 2nd argument the value of this symbol(a constant, variable or function)

.. code:: python

    from booleano.parser.scope import SymbolTable, Bind
    from booleano.operations.operands.constants import Number, Set, String

    SymbolTable('my_table', [])  # empty table
    SymbolTable('my_table', [
        Bind('age', Number(14)),
        Bind('name', String("katara")),
        Bind('bending', Set({'water'})),
    ])  # a table with bound constants

    SymbolTable(
        'my_table',
        [Bind('age', Number(14)),],
        SymbolTable('my_sub_table', [])  # this is an empty sub table
    )



Constants
^^^^^^^^^

the Available Constants are Number, String and Set. all hard coded value in a expression are converted to Constants

.. code:: python

    from booleano.operations.operands.constants import Number, Set, String

    age = Number(0)
    majority_age = Number(18)

    SymbolTable('my_table', [
        Bind('age', age),
        Bind('majority', majority_age),
        Bind('name', String("katara")),
        Bind('bending', Set({'water'})),
    ])

    # this expression is valid with the folowing SymbolTable:
    # age > majority & name == "katara" & {"water"} ∈ bending

Variables
^^^^^^^^^

remember that all beelean expression will be executed with a context. you can
build a parsed expression with some variables instead of constants. the Variables
will use the context to resolve itself with a final value.

booleano ship with subclass of Variable that take the name of the variable into the context, and will
resolve to it's value at execution.

the Available Variables are :

.. module:: booleano.operations.variables

- :class:`NumberVariable`: support operation valid for a number
- :class:`BooleanVariable`: support operation for a boolean
- :class:`StringVariable`: support pythonic operation for a String
- :class:`SetVariable`: support operation for a set
- :class:`DurationVariable`: support operation for a datetime.timedelat. can  be compared with a string if the format is
  "WW days XX hours YY minutes ZZ seconds"
- :class:`DateTimeVariable`: support operation for a datetime.datetime. can  be compared with a string if the format is
  "%d/%m/%Y %H:%M:%S"

- :class:`DateVariable`: support operation for a datetime.date. can  be compared with a string if the format is
  "%d/%m/%Y"

.. code::

    from booleano.parser.scope import SymbolTable, Bind
	from booleano.operations.variables import NumberVariable, StringVariable, SetVariable, DateVariable, DurationVariable


    SymbolTable('my_table', [
        Bind('age', NumberVariable('age')),
        Bind('name', StringVariable("name")),
        Bind('bending', SetVariable("character_bendings")),
        Bind('start_training', DateVariable('training_at')),
        Bind('training_duration', DurationVariable('training_duration')),

    ])

    # this expression is valid with the folowing SymbolTable:
    # age > 14 & name == "katara" & ( { "water" } ∈ bending |  start_training < "01-03-2017" | training_duration > "3d4h")


Function
^^^^^^^^

comming soon. documentations upgrade are welcome from cuntributor :ref:`contributing`

Sub symbol table
^^^^^^^^^^^^^^^^

SymbolTable can be nested. you can create it by adding as many sub SymbolTable at creation time (args) or via
:meth:`SymbolTable.add_subtable`. you will then access each sub tables :class:`booleano.parsing.scope.Bind` ed
value via his name folowed by the grammar token «namespace_separator» (usualy «:»)

.. code::

    from booleano.parser.scope import SymbolTable, Bind
    from booleano.operations.operands.constants import Number


    SymbolTable(
        'my_table',
        [
            Bind('age', Number(14)),
        ],
        SymbolTable('my_sub_table', [
            Bind('age', Number(16)),
        ])  # this is an empty sub table
    )

    # the folowing expression will be true:
    # age == 14 & my_sub_table:age == 16


a subtable can have the same name as a :class:`booleano.parsing.scope.Bind` ed variable.


.. code:: python

    from booleano.parser.scope import SymbolTable, Bind
    from booleano.operations.operands.constants import Number

    name = String("katara")

    SymbolTable(
        'my_table',
        [
            Bind('character', name),
        ],
        SymbolTable('character', [
            Bind('age', Number(16)),
            Bind('name', name),
        ])
    )

    # the folowing expression will be true:
    # character == "katara"
    # character:age == 16
    # character:name == "katara"
    # character == "katara" & character:age == 16

Evaluable Parse Manager
-----------------------

EvaluableParseManager is the barbar name for «compiled boolean expression».

once a EvaluableParseManager is created with (Grammar + SymbolTable + expression) it can be used with different set
of context, and return each time a boolean verifying the expression.

.. code:: python

	import datetime

	from booleano.operations.operands.constants import Number
	from booleano.parser.core import EvaluableParseManager
	from booleano.parser.grammar import Grammar

	from booleano.operations.variables import NumberVariable, StringVariable, DurationVariable, SetVariable
	from booleano.parser.scope import SymbolTable, Bind

	name = StringVariable("name")

	symbols = SymbolTable(
		'my_table',
		[
			Bind('character', name),
		],
		SymbolTable('character', [
			Bind('age', NumberVariable('age')),
			Bind('name', name),
			Bind('training', DurationVariable('training')),
			Bind('bending', SetVariable('bending')),
		]),
		SymbolTable('consts', [
			Bind('majority', Number(18)),
		])
	)

	grammar = Grammar(**{'and': 'and', 'or': 'or', 'belongs_to': 'in'})


	# 2: create the parser with se symbol table and the grammar (customized)
	parse_manager = EvaluableParseManager(symbols, grammar)
	# 3: compile a expression
	compiled_expression = parse_manager.parse(
		'character:age < consts:majority & '
		'"a" in character & '
		'('
		'    {"water"} in character:bending | '
		'    character:training > "3d4h"'
		')'
	)

	sample = [
		{"name": "katara", "age": 14, "training": datetime.timedelta(days=24), "bending": {'water'}},
		{"name": "aang", "age": 112, "training": datetime.timedelta(days=6*365), "bending": {'water', 'earth', 'fire', 'air'}},
		{"name": "zuko", "age": 16, "training": datetime.timedelta(days=29), "bending": {'fire'}},
		{"name": "sokka", "age": 15, "training": datetime.timedelta(days=0), "bending": set()},
	]

	for character in sample:
		# 4 execute the cumpiled expression with a context
		print("%s => %s" % (character, compiled_expression(character)))


Advanced Variable Subclasses
============================


Once you know the Booleano functions and variables (not the same as Python
functions and variables), it's time to implement them.

If, for example, you have a bookstore, you may need the variables to represent 
the following:

* The title of a book.
* The amount of pages in a book.
* The author(s) of a book.

You could define them as follows::

    from booleano.operations import Variable

    class BookTitle(Variable):
        """
        Booleano variable that represents the title of a book.

        """

        # We can perform equality (==, !=) and membership operations on the
        # name of a book:
        operations = set(["equality", "membership"])

        def equals(self, value, context):
            """
            Check if ``value`` is the title of the book.

            Comparison is case-insensitive.

            """
            actual_book_title = context['title'].lower()
            other_book_title = value.lower()
            return actual_book_title == other_book_title

        def belongs_to(self, value, context):
            """
            Check if word ``value`` is part of the words in the book title.

            """
            word = value.lower()
            title = context['title'].lower()
            return word in title

        def is_subset(self, value, context):
            """
            Check if the words in ``value`` are part of the words in the book
            title.

            """
            words = set(value.lower().split())
            title_words = set(context['title'].lower().split())
            return words.issubset(title_words)

        def to_python(self, value):
            return unicode(context['title'].lower())

    class BookPages(Variable):
        """
        Booleano variable that represents the amount of pages in a book.

        """

        # This variable supports equality (==, !=) and inequality (<, >, <=, >=)
        # operations:
        operations = set(["equality", "inequality"])

        def equals(self, value, context):
            """
            Check that the book has the same amount of pages as ``value``.

            """
            actual_pages = context['pages']
            expected_pages = int(value)
            return actual_pages == expected_pages

        def greater_than(self, value, context):
            """
            Check that the amount of pages in the book is greater than
            ``value``.

            """
            actual_pages = context['pages']
            expected_pages = int(value)
            return actual_pages > expected_pages

        def less_than(self, value, context):
            """
            Check that the amount of pages in the book is less than ``value``.

            """
            actual_pages = context['pages']
            expected_pages = int(value)
            return actual_pages < expected_pages

        def to_python(self, value):
            return int(context['pages'])

    class BookAuthor(Variable):
        """
        Booleano variable that represents the name of a book author.

        """

        # This variable only supports equality and boolean operations:
        operations = set(["equality", "boolean"])

        def __call__(self, context):
            """
            Check if the author of the book is known.

            """
            return bool(context['author'])

        def equals(self, value, context):
            """
            Check if ``value`` is the name of the book author.

            """
            expected_name = value.lower()
            actual_name = context['author'].lower()
            return expected_name == actual_name

        def to_python(self, value):
            return unicode(context['author'].lower())


Defining the symbol table
-------------------------

Once the required variables and functions have been defined, it's time give them
names in the expressions::

    from booleano.parser import SymbolTable, Bind
    from booleano.operations import Number

    book_title_var = BookTitle()

    root_table = SymbolTable("root",
        (
        Bind("book", book_title_var),
        ),
        SymbolTable("book",
            (
            Bind("title", book_title_var),
            Bind("author", BookAuthor()),
            Bind("pages", BookPages())
            )
        ),
        SymbolTable("constants",
            (
            Bind("average_pages", Number(200)),
            )
        )
    )

With the symbol table above, we have 5 identifiers:

* ``book`` and ``book:title``, which are equivalent, represent the title of
  the book.
* ``book:author`` represents the name of the book author.
* ``book:pages`` represents the amounts of pages in the book.
* ``constants:average_pages`` is a named constant that represents the average
  amount of pages in all the books (200 in this case).


Defining the grammar
--------------------

We're going to customize the tokens for the following operators:

* "~" (negation) will be "not".
* "==" ("equals") will be "is".
* "!=" ("not equals") will be "isn't".
* "∈" ("belongs to") will be "in".
* "⊂" ("is sub-set of") will be "are included in".

So we instatiate it like this::

    from booleano.parser import Grammar

    new_tokens = {
        'not': "not",
        'eq': "is",
        'ne': "isn't",
        'belongs_to': "in",
        'is_subset': "are included in",
    }

    english_grammar = Grammar(**new_tokens)


Creating the parse manager
--------------------------

Finally, it's time to put it all together::

    from booleano.parser import EvaluableParseManager

    parse_manager = EvaluableParseManager(root_table, english_grammar)


Parsing and evaluating expressions
==================================

First let's check that our parser works correctly with our custom grammar::

    >>> parse_manager.parse('book is "Programming in Ada 2005"')
    <Parse tree (evaluable) <Equal <Anonymous variable [BookTitle]> <String "Programming in Ada 2005">>>
    >>> parse_manager.parse('book:title is "Programming in Ada 2005"')
    <Parse tree (evaluable) <Equal <Anonymous variable [BookTitle]> <String "Programming in Ada 2005">>>
    >>> parse_manager.parse('"Programming in Ada 2005" is book')
    <Parse tree (evaluable) <Equal <Anonymous variable [BookTitle]> <String "Programming in Ada 2005">>>
    >>> parse_manager.parse('book:title isn\'t "Programming in Ada 2005"')
    <Parse tree (evaluable) <NotEqual <Anonymous variable [BookTitle]> <String "Programming in Ada 2005">>>
    >>> parse_manager.parse('{"ada", "programming"} are included in book:title')
    <Parse tree (evaluable) <IsSubset <Anonymous variable [BookTitle]> <Set <String "ada">, <String "programming">>>>
    >>> parse_manager.parse('"software measurement" in book:title')
    <Parse tree (evaluable) <BelongsTo <Anonymous variable [BookTitle]> <String "software measurement">>>
    >>> parse_manager.parse('"software engineering" in book:title & book:author is "Ian Sommerville"')
    <Parse tree (evaluable) <And <BelongsTo <Anonymous variable [BookTitle]> <String "software engineering">> <Equal <Anonymous variable [BookAuthor]> <String "Ian Sommerville">>>>

They all look great, so finally let's check if they are evaluated correctly
too::

    >>> books = (
    ... {'title': "Programming in Ada 2005", 'author': "John Barnes", 'pages': 828},
    ... {'title': "Software Engineering, 8th edition", 'author': "Ian Sommerville", 'pages': 864},
    ... {'title': "Software Testing", 'author': "Ron Patton", 'pages': 408},
    ... )
    >>> expr1 = parse_manager.parse('book is "Programming in Ada 2005"')
    >>> expr1(books[0])
    True
    >>> expr1(books[1])
    False
    >>> expr1(books[2])
    False
    >>> expr2 = parse_manager.parse('"ron patton" is book:author')
    >>> expr2(books[0])
    False
    >>> expr2(books[1])
    False
    >>> expr2(books[2])
    True
    >>> expr3 = parse_manager.parse('"software" in book:title')
    >>> expr3(books[0])
    False
    >>> expr3(books[1])
    True
    >>> expr3(books[2])
    True
    >>> expr4 = parse_manager.parse('book:pages > 800')
    >>> expr4(books[0])
    True
    >>> expr4(books[1])
    True
    >>> expr4(books[2])
    False

And there you go! They were all evaluated correctly!


Supporting more than one grammar
================================

If you have more than one language to support, that'd be a piece of cake! You
can add translations in the symbol table and/or add a customized grammar.

For example, if we had to support Castilian (aka Spanish), our symbol table
would've looked like this::

    from booleano.parser import SymbolTable, Bind
    from booleano.operations import Number

    book_title_var = BookTitle()

    root_table = SymbolTable("root",
        (
        Bind("book", book_title_var, es="libro"),
        ),
        SymbolTable("book",
            (
            Bind("title", book_title_var, es=u"título"),
            Bind("author", BookAuthor(), es="autor"),
            Bind("pages", BookPages(), es=u"páginas")
            ),
            es="libro"
        ),
        SymbolTable("constants",
            (
            Bind("average_pages", Number(200)),
            ),
            es="constantes"
        )
    )


And we could've customized the grammar like this::

    from booleano.parser import Grammar

    new_es_tokens = {
        'not': "no",
        'eq': "es",
        'ne': "no es",
        'belongs_to': u"está en",
        'is_subset': u"están en",
    }

    castilian_grammar = Grammar(**new_es_tokens)


Finally, we'd have to add the new grammar to the parse manager::


    from booleano.parser import EvaluableParseManager

    parse_manager = EvaluableParseManager(root_table, english_grammar, es=castilian_grammar)

Now test the expressions, but this time with our new localization::

    >>> expr1 = parse_manager.parse('libro es "Programming in Ada 2005"', "es")
    >>> expr1
    <Parse tree (evaluable) <Equal <Anonymous variable [BookTitle]> <String "Programming in Ada 2005">>>
    >>> expr1(books[0])
    True
    >>> expr1(books[1])
    False
    >>> expr1(books[2])
    False
    >>> expr2 = parse_manager.parse(u'libro:páginas < 500', "es")
    >>> expr2
    <Parse tree (evaluable) <LessThan <Anonymous variable [BookPages]> <Number 500.0>>>
    >>> expr2(books[0])
    False
    >>> expr2(books[1])
    False
    >>> expr2(books[2])
    True
    >>> expr3 = parse_manager.parse(u'"software" está en libro', "es")
    >>> expr3
    <Parse tree (evaluable) <BelongsTo <Anonymous variable [BookTitle]> <String "software">>>
    >>> expr3(books[0])
    False
    >>> expr3(books[1])
    True
    >>> expr3(books[2])
    True

They worked just like the original, English expressions!
