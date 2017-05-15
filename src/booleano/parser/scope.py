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
Booleano scope handling.

"""
from __future__ import unicode_literals

from logging import getLogger

import six

from booleano.exc import ScopeError

__all__ = ("Bind", "SymbolTable", "Namespace")

LOGGER = getLogger(__name__)


@six.python_2_unicode_compatible
class _Identifier(object):
    """
    Multilingual identifier.

    """

    def __init__(self, global_name, **names):
        """
        Create the identifier using ``global_name`` as it's name.

        :param global_name: The identifier string (excludes parent symbol
            tables, if any).
        :type global_name: basestring

        Additional keyword arguments represent the translations of the
        ``global_name`` into other languages.

        """
        # By default, identifiers are not bound to a symbol table:
        self.symbol_table = None
        # Convert the ``names`` to lower-case:
        self.global_name = global_name.lower()
        for (locale, name) in names.items():
            names[locale] = name.lower()
        self.names = names

    def get_localized_name(self, locale):
        """
        Return the localized name of the identifier in ``locale``.

        :param locale: The locale of the name.
        :type locale: basestring
        :return: The name of the identifier in ``locale``; if it's not defined,
            the global name is returned.
        :rtype: basestring

        """
        if locale in self.names:
            name = self.names[locale]
        else:
            LOGGER.warn("%s doesn't have a name in %s; using the global one",
                        self, locale)
            name = self.global_name
        return name

    def _get_contents(self, locale):
        """
        Return the contents being wrapped, filtered by ``locale`` where
        relevant.

        :param locale: The locale used to filter the contents.
        :param locale: basestring
        :return: The contents being wrapped; in a binding, it's the operand,
            while in a symbol table, it's the namespace for the ``locale``.

        """
        raise NotImplementedError()

    # Comparison stuff

    def __hash__(self):
        """
        Make the identifier hashable based on its global name.

        """
        first = ord(self.global_name[0])
        last = ord(self.global_name[-1])
        hash_ = first * 2 + last * 3 + len(self.global_name)
        return hash_

    def __eq__(self, other):
        """
        Check that the ``other`` identifier is equivalent to this one.

        Two identifiers are equivalent if the have the same names.

        """
        if (isinstance(other, _Identifier) and
                self.global_name == other.global_name and
                self.names == other.names):
            return True
        return False

    def __ne__(self, other):
        """
        Check that the ``other`` identifier is NOT equivalent to this one.

        """
        return not self.__eq__(other)

    def __str__(self):
        """
        Return the Unicode representation for the identifier.

        This must be overridden by the specific identifiers.

        """
        raise NotImplementedError("Identifiers must set their Unicode "
                                  "representation")


@six.python_2_unicode_compatible
class Bind(_Identifier):
    """
    Operand binder.

    Each instance is a name :term:`binding`, which assigns an identifier to an
    operand (even in different languages).

    """

    def __init__(self, global_name, operand, **names):
        """

        :param global_name: The identifier string (excludes parent names, if
            any).
        :type global_name: basestring
        :param operand: The operand to be bound.
        :type operand: :class:`booleano.operations.Operand`

        Additional keyword arguments represent the translations of the
        ``global_name`` into other languages.

        """
        self.operand = operand
        super(Bind, self).__init__(global_name, **names)

    def _get_contents(self, locale):
        """
        Return the operand bound.

        The ``locale`` does nothing here.

        """
        return self.operand

    def __eq__(self, other):
        """
        Check that the ``other`` binding is equivalent to this one.

        Two bindings are equivalent if they have the same names, even though
        they don't wrap the same operand.

        """
        same_id = super(Bind, self).__eq__(other)
        # We have to make sure ``other`` is a binding; otherwise, a symbol
        # table with the same names would equal this binding:
        return same_id and isinstance(other, Bind)

    def __hash__(self):
        return super(Bind, self).__hash__()

    def __str__(self):
        """
        Return the Unicode representation for this binding, including its
        symbol table (if any).

        """
        description = 'Operand %s bound as "%s"' % (self.operand,
                                                    self.global_name)
        if self.symbol_table:
            description = "%s (in %s)" % (description, self.symbol_table)
        return description

    def __repr__(self):
        return '<%s>' % self


@six.python_2_unicode_compatible
class SymbolTable(_Identifier):
    """
    Symbol table.

    Symbol tables wrap *bound* operands (aka, "bindings").

    """

    def __init__(self, global_name, objects, *subtables, **names):
        """

        :param global_name: The name of the symbol table (excludes parent
            symbol tables, if any).
        :type global_name: basestring
        :param objects: List of bound operands available in this symbol table.
        :type objects: list | tuple
        :raises booleano.exc.ScopeError: If an object/subtable is already
            included or already belongs to another symbol table.

        Additional positional arguments represent the sub-tables of this
        symbol table.

        Additional keyword arguments represent the other names this table
        can take in different locales.

        """
        super(SymbolTable, self).__init__(global_name, **names)
        self.objects = set()
        self.subtables = set()
        for obj in objects:
            self.add_object(obj)
        for table in subtables:
            self.add_subtable(table)

    def add_object(self, obj):
        """
        Add the ``obj`` object to this symbol table.

        :param obj: The bound operand to be added.
        :type obj: :class:`Bind`
        :raises booleano.exc.ScopeError: If ``obj`` is already included or it
            already belongs to another symbol table.

        """
        # Checking if it's safe to include the object:
        if obj.symbol_table:
            raise ScopeError(u"%s already belongs to %s" % (obj.global_name,
                                                            obj.symbol_table))
        if obj in self.objects or obj.symbol_table:
            raise ScopeError(u"An equivalent of %s is already defined in %s" %
                             (obj, self))

        # It's safe to include it!
        obj.symbol_table = self
        self.objects.add(obj)

    def add_subtable(self, table):
        """
        Include ``table`` in the child tables of this symbol table.

        :param table: The symbol table to be added.
        :type table: :class:`SymbolTable`
        :raises booleano.exc.ScopeError: If ``table`` is already included or it
            already belongs to another symbol table.

        """
        # Checking if it's safe to include the sub-table:
        if table.symbol_table:
            raise ScopeError(u"%s already belongs to %s" %
                             (table, table.symbol_table))
        if table in self.subtables:
            raise ScopeError(u"An equivalent of %s is already available in %s" %
                             (table, self))

        # It's safe to include it!
        table.symbol_table = self
        self.subtables.add(table)

    def validate_scope(self):
        """
        Make sure there's no name clash in the symbol table.

        :raise booleano.exc.ScopeError: If a name clash in found, either in the
            global names or with the localized names.

        Users may want to run this in their test suite, instead of in
        production, for performance reasons.

        Note that it's perfectly valid for one object and one sub-table to
        have the same name in the parent symbol table.

        """
        # <--- Checking that there's no name clash among the global names

        unique_objects = set([obj.global_name for obj in self.objects])
        if len(unique_objects) != len(self.objects):
            raise ScopeError("Two or more objects in %s share the same global "
                             "name" % self)

        unique_tables = set([table.global_name for table in self.subtables])
        if len(unique_tables) != len(self.subtables):
            raise ScopeError("Two or more sub-tables in %s share the same "
                             "global name" % self)

        # <--- Checking that there's no name clash in the sub-tables
        for table in self.subtables:
            table.validate_scope()

        # <--- Checking that there's no name clash among the localized names

        # Collecting all the locales used:
        locales = set()
        for id_ in (self.objects | self.subtables):
            locales |= set(id_.names.keys())

        # Now let's see if any of them are duplicate:
        for locale in locales:
            # Checking the objects:
            used_object_names = set()
            for obj in self.objects:
                name = obj.get_localized_name(locale)
                if name in used_object_names:
                    raise ScopeError('The name "%s" is shared by two or more '
                                     'bindings in %s (locale: %s)' %
                                     (name, self, locale))
                used_object_names.add(name)

            # Checking the sub-tables:
            used_table_names = set()
            for table in self.subtables:
                name = table.get_localized_name(locale)
                if name in used_table_names:
                    raise ScopeError('The name "%s" is shared by two or more '
                                     'sub-tables in %s (locale: %s)' %
                                     (name, self, locale))
                used_table_names.add(name)

    def get_namespace(self, locale=None):
        """
        Extract the namespace for this symbol table in the ``locale``.

        :param locale: The locale of the namespace; if ``None``, the global
            names will be used instead.
        :param locale: basestring
        :return: The namespace in ``locale``.
        :rtype: :class:`booleano.parser.scope.Namespace`

        """
        objects = self._get_objects(locale)
        subnamespaces = self._get_subnamespaces(locale)
        return Namespace(objects, subnamespaces)

    def __str__(self):
        """
        Return the Unicode representation for this symbol table, including its
        ancestors.

        """
        ancestors = self._get_ancestors_global_names()
        names = u":".join(ancestors)
        return u"Symbol table %s" % names

    def __eq__(self, other):
        """
        Check that the ``other`` symbol table is equivalent to this one.

        Two tables are equivalent if they are equivalent identifiers
        (:meth:`_Identifier.__eq__`) and wrap the same objects and
        sub-tables.

        """
        same_id = super(SymbolTable, self).__eq__(other)
        return (same_id and
                hasattr(other, "subtables") and
                hasattr(other, "objects") and
                other.subtables == self.subtables and
                self.objects == other.objects)

    def __hash__(self):
        return hash((frozenset(getattr(self, 'subtables', set())), frozenset(getattr(self, 'objects', set()))))

    def _get_contents(self, locale):
        """Return the namespace for this symbol table in ``locale``."""
        return self.get_namespace(locale)

    def _get_objects(self, locale):
        """
        Return the objects available in this symbol table.

        :param locale: The locale to be used while resolving the names of the
            objects.
        :type locale: basestring
        :return: The operands in this table, in a dictionary whose keys
            are the names of the objects in ``locale``.
        :rtype: dict

        """
        objects = self.__extract_items__(self.objects, locale)
        return objects

    def _get_subnamespaces(self, locale):
        """
        Return the sub-tables available under this symbol table, turned into
        namespaces for the ``locale``.

        :param locale: The locale to be used while resolving the names of the
            sub-tables.
        :type locale: basestring
        :return: The namespaces for the sub-tables under this symbol table,
            in a dictionary whose keys are the namespace strings in
            ``locale``.
        :rtype: dict

        """
        subnamespaces = self.__extract_items__(self.subtables, locale)
        return subnamespaces

    def __extract_items__(self, items, locale):
        """
        Filter the contents of the ``items`` identifiers based on the
        ``locale``.

        :param items: A list of identifiers whose contents should be extracted.
        :type items: list|set|tuple
        :param locale: The locale to be used to filter the contents.
        :type locale: basestring or ``None``
        :return: The contents of each item in ``items``, in a dictionary whose
            keys are the names of such items in the ``locale``.
        :rtype: dict

        """
        extracted_items = {}

        if locale:
            # The items have to be extracted by their localized names:
            for item in items:
                localized_name = item.get_localized_name(locale)
                extracted_items[localized_name] = item._get_contents(locale)
        else:
            # We have to extract the items by their global names:
            for item in items:
                extracted_items[item.global_name] = item._get_contents(locale)

        return extracted_items

    def _get_ancestors_global_names(self):
        """
        Return the global names for the ancestors **and** the current
        symbol table's.

        :return: The list of names, from the topmost table to the current one.
        :rtype: list

        """
        if self.symbol_table:
            ancestors = self.symbol_table._get_ancestors_global_names()
        else:
            ancestors = []
        ancestors.append(self.global_name)
        return ancestors


class Namespace(object):
    """
    A namespace for a given locale.

    This is not aimed at end-users, it should only be used internally in
    Booleano.

    The parser only deals with this, not with the symbol table directly.

    A symbol table has one namespace per locale.

    """

    def __init__(self, objects, subnamespaces={}):
        """

        :param objects: The objects that belong to the table.
        :type objects: dict
        :param subnamespaces: The namespaces under this namespace, if any.
        :type subnamespaces: dict

        """
        self.objects = objects
        self.subnamespaces = subnamespaces

    def get_object(self, object_name, namespace_parts=None):
        """
        Return the object identified by ``object_name``, which is under the
        namespace whose names are ``namespace_parts``.

        :param object_name: The name of the object to be returned.
        :type object_name: basestring
        :param namespace_parts: The sub-namespace that contains the object
            identified by ``object_name``, represented by a list of names; or,
            ``None`` if the object is in the current namespace.
        :type namespace_parts: list
        :return: The requested object.
        :rtype: Operand
        :raises ScopeError: If the requested object doesn't exist in the
            namespace, or if the sub-namespace in ``namespace_parts`` doesn't
            exist.

        """
        ns = self._get_subnamespace(namespace_parts)
        if ns is None or object_name not in ns.objects:
            msg = u'No such object "%s"' % object_name
            if namespace_parts:
                msg = u'%s in %s' % (msg, u":".join(namespace_parts))
            raise ScopeError(msg)
        return ns.objects[object_name]

    def _get_subnamespace(self, namespace_parts):
        """
        Return the sub-namespace represented by the names in
        ``namespace_parts``.

        :param namespace_parts: The names that resolve a sub-namespace in this
            namespace.
        :type namespace_parts: list
        :return: The namespace represented by the names in
            ``namespace_parts`` or ``None`` if it's not found.
        :rtype: Namespace

        """
        if not namespace_parts:
            return self
        current_part = namespace_parts.pop(0)
        if current_part not in self.subnamespaces:
            return None
        # It's been found!
        subnamespace = self.subnamespaces[current_part]
        return subnamespace._get_subnamespace(namespace_parts)
