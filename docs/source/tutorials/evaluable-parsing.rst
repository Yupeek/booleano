==========================
Evaluable Parsing Tutorial
==========================

.. todo:: Rewrite this tutorial to explain step-by-step how to develop an small
    yet real project with Booleano.

Overview
========

**Evaluable parsing** is when a boolean expression represents a condition that
some items must meet, or else they'll be ignored.

What you need
=============

You need an :class:`evaluable parse manager 
<booleano.parser.EvaluableParseManager>` configured with a
:class:`symbol table <booleano.parser.SymbolTable>` and at least one
:class:`grammar <booleano.parser.Grammar>`, as well as define all the Booleano
variables and functions that may be used in the expressions.


Defining variables and functions
--------------------------------

.. todo:: Explain how to define a function.


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
