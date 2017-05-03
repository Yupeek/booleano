============================
Convertible Parsing Tutorial
============================

.. todo:: Rewrite this tutorial to explain step-by-step how to develop an small
    yet real project with Booleano.


Overview
========

**Convertible parsing** is when the boolean expressions should be converted into
something else, most likely another filter.

What you need
=============

For this you need a :class:`grammar <booleano.parser.Grammar>`, passed to a
:class:`convertible parse manager <booleano.parser.ConvertibleParseManager>`
and finally, your :class:`converter class
<booleano.operations.converters.BaseConverter>`.


Configuring the grammar
-----------------------

We're going to use the grammar with the default tokens, except for the
"belongs to" and "is sub-set of" operators (the default tokens are "∈" and "⊂",
respectively, which is not easy to type in a keyboard)::

    from booleano.parser import Grammar
    
    grammar = Grammar(belongs_to="in", is_subset="is subset of")

With this ``grammar``, we can write expressions like:

* ``"thursday" in {"monday", "tuesday", "wednesday", "thursday", "friday"}``
* ``"thursday" in week_days``
* ``{"thursday", "monday"} is subset of {"monday", "tuesday", "wednesday", "thursday", "friday"}``
* ``{"thursday", "monday"} is subset of week_days``


Configuring the convertible parse manager
-----------------------------------------

This is easy. You just need the grammar we created before::

    from booleano.parser import ConvertibleParseManager
    
    parse_manager = ConvertibleParseManager(grammar)


Defining a converter
--------------------

You have to subclass :class:`booleano.operations.converters.BaseConverter`
and define its abstract methods (i.e., the node-specific converters) so they
return the data type you want.


Parsing and converting expressions
==================================

That's all you need. Your module should look like this::

    from booleano.parser import Grammar, ConvertibleParseManager
    from your_project import YourCustomConverter
    
    grammar = Grammar(belongs_to="in", is_subset="is subset of")
    parse_manager = ConvertibleParseManager(grammar)
    converter = YourCustomConverter()

It's now time to put out parser to the test! Let's start by checking how
expressions are parsed::

    >>> parse_manager.parse('"thursday" in {"monday", "tuesday", "wednesday", "thursday", "friday"}')
    <Parse tree (convertible) <BelongsTo <Set <String "monday">, <String "tuesday">, <String "friday">, <String "thursday">, <String "wednesday">> <String "thursday">>>
    >>> parse_manager.parse('today == "2009-07-17"')
    <Parse tree (convertible) <Equal <Placeholder variable "today"> <String "2009-07-17">>>
    >>> parse_manager.parse('today != "2009-07-17"')
    <Parse tree (convertible) <NotEqual <Placeholder variable "today"> <String "2009-07-17">>>
    >>> parse_manager.parse('~ today == "2009-07-17"')
    <Parse tree (convertible) <Not <Equal <Placeholder variable "today"> <String "2009-07-17">>>>
    >>> parse_manager.parse('today > "2009-07-17"')
    <Parse tree (convertible) <GreaterThan <Placeholder variable "today"> <String "2009-07-17">>>
    >>> parse_manager.parse('time:today == "sunday" & ~weather:will_it_rain_today("paris")')
    <Parse tree (convertible) <And <Equal <Placeholder variable "today" at namespace="time"> <String "sunday">> <Not <Placeholder function call "will_it_rain_today"(<String "paris">) at namespace="weather">>>>

OK, it seems like all the expressions above were parsed as expected.

In order to convert these trees with ``YourCustomConverter``, you'd just need
to pass its instance ``converter`` to the parse tree (which is a callable).
For example::

    >>> parse_tree = parse_manager.parse('today > "2009-07-17"')
    >>> the_conversion_result = parse_tree(converter)

And ``the_conversion_result`` will be, well, the conversion result.

