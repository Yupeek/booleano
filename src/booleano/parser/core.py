# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging
from logging import getLogger

from booleano.exc import GrammarError
from booleano.parser.parsers import ConvertibleParser, EvaluableParser

logger = logging.getLogger(__name__)
LOGGER = getLogger(__name__)


class ParseManager(object):
    """
    Base class for parse managers.

    A parse manager controls the parsers to be used in a single kind of
    expression, with one parser per supported grammar.

    """

    def __init__(self, generic_grammar, cache_limit=0, **localized_grammars):
        """

        :param generic_grammar: The default grammar.
        :type generic_grammar: :class:`Grammar`
        :param cache_limit: The maximum amount of expressions to be cached
            internally (use ``None`` for no limit or ``0`` to disable caching).
        :type cache_limit: int

        Additional keyword arguments, if any, will be used as custom grammars
        where each key represents the locale of the grammar in the value.

        """
        self._cache = _Cache(cache_limit)
        self._generic_grammar = generic_grammar
        self._parsers = {}
        for (locale, grammar) in localized_grammars.items():
            self.add_parser(locale, grammar)

    def parse(self, expression, locale=None):
        """
        Parse ``expression`` and return its parse tree.

        :param expression: The expression to be parsed.
        :type expression: basestring
        :param locale: The locale of the grammar used by ``expression``
            (or ``None`` if it uses the generic grammar).
        :type locale: basestring
        :return: The parse tree for ``expression``.
        :rtype: :class:`booleano.parser.trees.ParseTree`
        :raises booleano.exc.BadExpressionError: If ``expression`` is bad-formed
            according to the grammar ``locale``.
        :raises booleano.exc.InvalidOperationError: If ``expression`` has an
            invalid operation.
        :raises booleano.exc.ScopeError: If ``expression`` contains unknown
            identifiers.

        If caching is enabled and the ``expression`` was cached previously,
        ``expression`` won't be parsed again and its cached parse tree will
        be returned.

        If caching is enabled, but the ``expression`` is not cached, it will
        be parsed and the resulting parse tree will be cached and finally
        returned.

        """
        if self._cache.is_stored(locale, expression):
            parse_tree = self._cache.get_tree(locale, expression)
        else:
            parser = self._get_parser(locale)
            parse_tree = parser(expression)
            self._cache.store_tree(locale, expression, parse_tree)
        return parse_tree

    # Parser management

    def add_parser(self, locale, grammar):
        """
        Create a parser for ``grammar`` and store it.

        :param locale: The locale of the ``grammar``.
        :type locale: basestring
        :param grammar: The grammar of the parser to be created.
        :type grammar: :class:`Grammar`

        """
        if locale in self._parsers:
            raise GrammarError("There is already a parser for grammar %s" %
                               locale)
        parser = self._define_parser(locale, grammar)
        self._parsers[locale] = parser

    def _get_parser(self, locale):
        """
        Return the parser for the grammar identifier by ``locale``.

        :param locale: The locale of the grammar whose parser is requested.
        :type locale: basestring
        :return: The requested parser.
        :rtype: Parser

        If there's no parser for grammar ``locale``, it will be created based
        on the generic grammar.

        """
        if locale not in self._parsers:
            self.add_parser(locale, self._generic_grammar)
            LOGGER.info("Generated parser for unknown grammar %s", repr(locale))
        return self._parsers[locale]

    def _define_parser(self, locale, grammar):
        """
        Build a parser for ``grammar`` and return it.

        :param locale: The locale of the ``grammar``.
        :type locale: basestring
        :param grammar: The grammar for the parser to be built.
        :type grammar: Grammar
        :return: The parser built from ``grammar``.
        :rtype: Parser

        """
        raise NotImplementedError("Actual parse managers must define their "
                                  "parsers")

        #


class EvaluableParseManager(ParseManager):
    """
    Parsing manager for evaluable operations.

    It manages evaluable parsers.

    """

    def __init__(self, symbol_table, generic_grammar, cache_limit=0,
                 **localized_grammars):
        """

        :param symbol_table: The symbol table for the supported expressions.
        :type symbol_table: :class:`SymbolTable`
        :param generic_grammar: The default grammar.
        :type generic_grammar: :class:`Grammar`
        :param cache_limit: The maximum amount of expressions to be cached
            internally (use ``None`` for no limit or ``0`` to disable caching).
        :type cache_limit: int

        Additional keyword arguments, if any, will be used as custom grammars
        where each key represents the locale of the grammar in the value.

        """
        self._symbol_table = symbol_table
        super(EvaluableParseManager, self).__init__(generic_grammar,
                                                    cache_limit,
                                                    **localized_grammars)

    def evaluate(self, expression, locale, context):
        """
        Parse ``expression`` and return its evaluation result with ``context``.

        :param expression: The expression to be parsed.
        :type expression: basestring
        :param locale: The locale of the grammar used by ``expression``.
        :type locale: basestring
        :param context: The context under which the parse tree of ``expression``
            has to be evaluated.
        :type context: object
        :return: The result of the evaluation of the parse tree for
            ``expression``.
        :rtype: bool
        :raises BadExpressionError: If ``expression`` is bad-formed
            according to the ``locale`` grammar.
        :raises InvalidOperationError: If ``expression`` has an invalid
            operation.
        :raises ScopeError: If ``expression`` contains unknown identifiers.

        """
        tree = self.parse(expression, locale)
        return tree(context)

    def _define_parser(self, locale, grammar):
        """
        Build an evaluable parser for ``grammar`` and return it.

        :param locale: The locale of the ``grammar``.
        :type locale: basestring
        :param grammar: The grammar for the evaluable parser to be built.
        :type grammar: Grammar
        :return: The evaluable parser built from ``grammar``.
        :rtype: EvaluableParser

        """
        namespace = self._symbol_table.get_namespace(locale)
        parser = EvaluableParser(grammar, namespace)
        return parser


class ConvertibleParseManager(ParseManager):
    """
    Parsing manager for convertible operations.

    It manages convertible parsers.

    """

    def _define_parser(self, locale, grammar):
        """
        Build a parser for ``grammar`` and return it.

        :param locale: The locale of the ``grammar``.
        :type locale: basestring
        :param grammar: The grammar for the parser to be built.
        :type grammar: Grammar
        :return: The convertible parser built from ``grammar``.
        :rtype: ConvertibleParser

        Here the ``locale`` is not used.

        """
        parser = ConvertibleParser(grammar)
        return parser


class _Cache(object):
    """
    Cache handling for a parse manager.

    """

    def __init__(self, limit):
        """
        Set up the cache with ``limit``.

        :param limit: The maximum amount of expressions that can be cached
            (``None`` for no limit, ``0`` to disable caching).
        :type limit: int

        """
        self.limit = limit
        self.counter = 0
        self.cache_by_locale = {}
        self.latest_expressions = []

    def is_stored(self, locale, expression):
        """
        Check if ``expression`` has been cached.

        :param locale: The locale of the grammar used by ``expression``.
        :type locale: basestring
        :param expression: The expression in question.
        :type expression: basestring
        :return: Whether ``expression`` is included in the cache or not.
        :rtype: bool

        """
        stored = False
        try:
            stored = expression in self.cache_by_locale[locale]
        except KeyError:
            pass
        return stored

    def get_tree(self, locale, expression):
        """
        Return the cached parse tree for ``expression`` in ``locale``.

        :param locale: The locale of the grammar used by ``expression``.
        :type locale: basestring
        :param expression: The expression whose parse tree is requested.
        :type expression: basestring
        :return: The parse tree for ``expression`` in ``locale``.
        :rtype: ParseTree
        :raises KeyError: If the ``expression`` isn't cached (use
            :meth:`is_stored` first).

        """
        parse_tree = self.cache_by_locale[locale][expression]
        self.touch_tree(locale, expression)
        return parse_tree

    def store_tree(self, locale, expression, parse_tree):
        """
        Add the ``parse_tree`` of ``expression`` in ``locale`` to the cache.

        :param locale: The locale of the grammar used by ``expression``.
        :type locale: basestring
        :param expression: The expression whose parse tree is being stored.
        :type expression: basestring
        :param parse_tree: The parse tree of ``expression`` in ``locale``.
        :type parse_tree: ParseTree

        If caching is disabled, it won't do anything.

        """
        if self.limit == 0:
            # Cache is disabled.
            return
        # Cache is enabled, let's store it:
        self.remove_oldest()
        if locale not in self.cache_by_locale:
            self.cache_by_locale[locale] = {}
        self.cache_by_locale[locale][expression] = parse_tree
        self.counter += 1
        self.touch_tree(locale, expression)

    def touch_tree(self, locale, expression):
        """
        Mark ``expression`` in ``locale`` as the latest used item in the cache.

        :param locale: The locale of the grammar used by ``expression``.
        :type locale: basestring
        :param expression: The expression whose parse tree is being touched.
        :type expression: basestring

        """
        tree_indexes = (locale, expression)
        if tree_indexes in self.latest_expressions:
            # Removing the existing occurence:
            self.latest_expressions.remove(tree_indexes)
        self.latest_expressions.insert(0, tree_indexes)

    def remove_oldest(self):
        """
        Remove the oldest item in the cache.

        It won't do anything if there's no caching limit, the limit has not
        been reached or there's nothing cached.

        """
        if (self.limit is None or self.counter < self.limit or
                not self.latest_expressions):
            return
        (locale, expression) = self.latest_expressions.pop(-1)
        del self.cache_by_locale[locale][expression]
        self.counter -= 1
