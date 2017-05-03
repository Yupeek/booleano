# -*- coding: utf-8 -*-
#
# Copyright (c) 2009 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano/>.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, distribute with
# modifications, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written authorization.
"""
Scope handling tests.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises, raises

from booleano.parser.scope import Bind, SymbolTable, Namespace, _Identifier
from booleano.operations import String, Number
from booleano.exc import ScopeError

from tests import (TrafficLightVar, PermissiveFunction, TrafficViolationFunc,
                   BoolVar, LoggingHandlerFixture)


class TestIdentifiers(object):
    """Tests for the base :class:`_Identifier`."""
    
    def test_no_identifier_contents_by_default(self):
        """Identifiers must not return any contents by default."""
        id_ = _Identifier("name")
        assert_raises(NotImplementedError, id_._get_contents, None)
    
    def test_no_unicode_representation_by_default(self):
        id_ = _Identifier("name")
        assert_raises(NotImplementedError, unicode, id_)


class TestBind(object):
    """Tests for operand binder."""
    
    def test_global_names(self):
        """When an operand is bound, its global name must be set accordingly."""
        operand = String("hey there")
        bind1 = Bind("da_global_name", operand)
        bind2 = Bind("Da_Global_Name", operand)
        eq_(bind1.global_name, "da_global_name")
        eq_(bind1.global_name, bind2.global_name)
    
    def test_names(self):
        """
        When an operand is bound, its multiple names must be set accordingly.
        
        """
        operand = String("Vive la france !")
        # No localized names:
        bind1 = Bind("foo", operand)
        eq_(bind1.names, {})
        # Lower-case names:
        names0 = {'es_VE': "cartuchera", 'es_ES': "estuche"}
        bind2 = Bind("bar", operand, **names0)
        eq_(bind2.names, names0)
        # Mixed-case names -- must be converted to lower-case:
        names1 = {'es_VE': "Cartuchera", 'es_ES': "estuche"}
        bind2 = Bind("bar", operand, **names1)
        eq_(bind2.names, names0)
    
    def test_retrieving_existing_localized_names(self):
        bind = Bind("foo", String("hey"), es="fulano")
        eq_(bind.get_localized_name("es"), "fulano")
    
    def test_retrieving_non_existing_localized_names(self):
        """
        When a non-existing localized name is requested, a warning must be 
        issued and the global name returned.
        
        """
        bind = Bind("foo", String("hey"), es="fulano")
        logging_fixture = LoggingHandlerFixture()
        eq_(bind.get_localized_name("fr"), "foo")
        # Checking for the the warning:
        eq_(len(logging_fixture.handler.messages["warning"]), 1)
        warning = logging_fixture.handler.messages["warning"][0]
        eq_(warning, 'Operand "hey" bound as "foo" doesn\'t have a name in fr; '
                     'using the global one')
        # Undoing it:
        logging_fixture.undo()
    
    def test_no_default_symbol_table(self):
        """Operand bindings must not be in a symbol table by default."""
        bind = Bind("foo", String("whatever"))
        eq_(bind.symbol_table, None)
    
    def test_constant(self):
        """Constants can be bound."""
        constant = String("I'm a string!")
        bound_constant = Bind("da_string", constant)
        eq_(bound_constant.operand, constant)
    
    def test_instance(self):
        """Class instances can be bound."""
        instance = TrafficLightVar()
        bound_instance = Bind("da_variable", instance)
        eq_(bound_instance.operand, instance)
    
    def test_contents_retrieval(self):
        """Bindings must return bound operand as its contents."""
        op = BoolVar()
        bind = Bind("bool", op)
        eq_(op, bind._get_contents(None))
    
    def test_equality(self):
        """Two bindings are equivalent if they have the same names."""
        op1 = TrafficLightVar()
        op2 = String("hey, where's my car?")
        bind1 = Bind("name1", op1)
        bind2 = Bind("name2", op2)
        bind3 = Bind("name2", op1)
        bind4 = Bind("name1", op2)
        bind5 = Bind("name1", op1)
        bind6 = Bind("name2", op2)
        bind7 = Bind("name1", op1, es="nombre1")
        bind8 = Bind("name1", op1, es_VE="nombre1", es="nombre1")
        bind9 = Bind("name1", op1, es="nombre1")
        
        ok_(bind1 == bind4)
        ok_(bind1 == bind5)
        ok_(bind2 == bind3)
        ok_(bind2 == bind6)
        ok_(bind3 == bind2)
        ok_(bind3 == bind6)
        ok_(bind4 == bind1)
        ok_(bind4 == bind5)
        ok_(bind5 == bind5)
        ok_(bind5 == bind1)
        ok_(bind5 == bind4)
        ok_(bind6 == bind2)
        ok_(bind6 == bind3)
        ok_(bind7 == bind9)
        ok_(bind9 == bind7)
        
        ok_(bind1 != None)
        ok_(bind1 != SymbolTable("name1", []))
        
        ok_(bind1 != bind2)
        ok_(bind1 != bind3)
        ok_(bind1 != bind6)
        ok_(bind1 != bind7)
        ok_(bind1 != bind8)
        ok_(bind1 != bind9)
        ok_(bind2 != bind1)
        ok_(bind2 != bind4)
        ok_(bind2 != bind5)
        ok_(bind2 != bind7)
        ok_(bind2 != bind8)
        ok_(bind2 != bind9)
        ok_(bind3 != bind1)
        ok_(bind3 != bind4)
        ok_(bind3 != bind5)
        ok_(bind3 != bind7)
        ok_(bind3 != bind8)
        ok_(bind3 != bind9)
        ok_(bind4 != bind2)
        ok_(bind4 != bind3)
        ok_(bind4 != bind6)
        ok_(bind4 != bind7)
        ok_(bind4 != bind8)
        ok_(bind4 != bind9)
        ok_(bind5 != bind2)
        ok_(bind5 != bind3)
        ok_(bind5 != bind6)
        ok_(bind5 != bind7)
        ok_(bind5 != bind8)
        ok_(bind5 != bind9)
        ok_(bind6 != bind1)
        ok_(bind6 != bind4)
        ok_(bind6 != bind5)
        ok_(bind6 != bind7)
        ok_(bind6 != bind8)
        ok_(bind6 != bind9)
        ok_(bind7 != bind1)
        ok_(bind7 != bind2)
        ok_(bind7 != bind3)
        ok_(bind7 != bind4)
        ok_(bind7 != bind5)
        ok_(bind7 != bind6)
        ok_(bind7 != bind8)
        ok_(bind8 != bind1)
        ok_(bind8 != bind2)
        ok_(bind8 != bind3)
        ok_(bind8 != bind4)
        ok_(bind8 != bind5)
        ok_(bind8 != bind6)
        ok_(bind8 != bind7)
        ok_(bind8 != bind9)
        ok_(bind9 != bind1)
        ok_(bind9 != bind2)
        ok_(bind9 != bind3)
        ok_(bind9 != bind4)
        ok_(bind9 != bind5)
        ok_(bind9 != bind6)
        ok_(bind9 != bind8)
    
    def test_string_without_symbol_table(self):
        # With ASCII characters:
        bind1 = Bind("pi", Number(3.1416))
        bind1_as_unicode = unicode(bind1)
        eq_(bind1_as_unicode, 'Operand 3.1416 bound as "pi"')
        eq_(bind1_as_unicode, str(bind1))
        # With non-ASCII characters:
        bind2 = Bind(u"pí", Number(3.1416))
        bind2_as_unicode = unicode(bind2)
        eq_(bind2_as_unicode, u'Operand 3.1416 bound as "pí"')
        eq_(str(bind2), 'Operand 3.1416 bound as "pí"')
    
    def test_string_with_symbol_table(self):
        # With ASCII characters:
        bind1 = Bind("pi", Number(3.1416))
        SymbolTable("global", [bind1])
        bind1_as_unicode = unicode(bind1)
        eq_('Operand 3.1416 bound as "pi" (in Symbol table global)',
            bind1_as_unicode)
        eq_(str(bind1), bind1_as_unicode)
        # With non-ASCII characters:
        bind2 = Bind(u"pí", Number(3.1416))
        SymbolTable("global", [bind2])
        bind2_as_unicode = unicode(bind2)
        eq_(u'Operand 3.1416 bound as "pí" (in Symbol table global)',
            bind2_as_unicode)
        eq_('Operand 3.1416 bound as "pí" (in Symbol table global)', str(bind2))


class TestSymbolTable(object):
    """Tests for the multilingual symbol tables."""
    
    def test_global_names(self):
        """
        When a symbol table is created, its global name must be set accordingly.
        
        """
        st1 = SymbolTable("foo", [])
        st2 = SymbolTable("Foo", [])
        eq_(st1.global_name, "foo")
        eq_(st1.global_name, st2.global_name)
    
    def test_names(self):
        """
        When a table is created, its multiple names must be set accordingly.
        
        """
        # No localized names:
        st0 = SymbolTable("foo", [])
        eq_(st0.names, {})
        # Lower-case names:
        names0 = {'es_VE': "cartuchera", 'es_ES': "estuche"}
        st1 = SymbolTable("bar", [], **names0)
        eq_(st1.names, names0)
        # Mixed-case names -- must be converted to lower-case:
        names1 = {'es_VE': "Cartuchera", 'es_ES': "estuche"}
        st2 = SymbolTable("bar", [], **names1)
        eq_(st2.names, names0)
    
    def test_no_default_symbol_table(self):
        """Tables must not have a parent table by default."""
        st = SymbolTable("foo", [])
        eq_(st.symbol_table, None)
    
    def test_constructor_without_subtables(self):
        """Sub-tables are optional."""
        st = SymbolTable("foo", [])
        eq_(len(st.subtables), 0)
    
    def test_constructor_without_objects(self):
        """Objects are mandatory, or an empty list must be passed explicitly."""
        # No objects
        assert_raises(TypeError, SymbolTable, "foo")
        # Empty list of objects:
        st = SymbolTable("foo", [])
        eq_(len(st.objects), 0)
    
    def test_constructor_with_objects(self):
        objects = [Bind("greeting", String("hey")),
                   Bind("traffic", TrafficLightVar())]
        st = SymbolTable("global", objects)
        eq_(st.objects, set(objects))
    
    def test_constructor_with_subtables(self):
        tables = [
            SymbolTable("sub1", []),
            SymbolTable(
                "sub2",
                [],
                SymbolTable("sub2.sub1", []),
                SymbolTable("sub2.sub2", [])
            ),
        ]
        st = SymbolTable("global", [], *tables)
        eq_(st.subtables, set(tables))
    
    def test_duplicate_objects(self):
        """There must be no duplicate object."""
        # In the constructor:
        objects1 = [Bind("salutation", String("hey")),
                    Bind("traffic", TrafficLightVar()),
                    Bind("salutation", String("hey"))]
        assert_raises(ScopeError, SymbolTable, "global", objects1)
        # Post-instantiation:
        objects2 = [Bind("salutation", String("hey")),
                    Bind("traffic", TrafficLightVar())]
        st = SymbolTable("global", objects2)
        assert_raises(ScopeError, st.add_object,
                      Bind("salutation", String("hey")))
    
    def test_duplicate_subtables(self):
        """There must not be duplicate sub-tables."""
        # In the constructor:
        subtables1 = [SymbolTable("foo", ()),
                      SymbolTable("bar", ()),
                      SymbolTable("foo", ())]
        assert_raises(ScopeError, SymbolTable, "global", (), *subtables1)
        # Post-instantiation:
        subtables2 = [SymbolTable("foo", ()), SymbolTable("bar", ())]
        st = SymbolTable("global", [], *subtables2)
        assert_raises(ScopeError, st.add_subtable, SymbolTable("bar", []))
    
    def test_unreusable_bindings(self):
        """
        Operand bindings and symbol tables can only be bound to a single parent
        symbol table.
        
        """
        # An operand binding:
        bind = Bind("traffic-light", TrafficLightVar())
        SymbolTable("traffic", [bind])
        assert_raises(ScopeError, SymbolTable, "baz", [bind])
        # A symbol table:
        st0 = SymbolTable("foo", [])
        SymbolTable("global", [], st0)
        assert_raises(ScopeError, SymbolTable, "bar", [], st0)
    
    def test_checking_valid_table(self):
        st = SymbolTable("global",
            # Bindings/global objects:
            (
             Bind("bool", BoolVar(), es="booleano"),
             Bind("traffic", TrafficLightVar(), es=u"tráfico"),
            ),
            # Sub-tables:
            SymbolTable("maths",
                (
                 Bind("pi", Number(3.1416)),
                 Bind("e", Number(2.7183)),
                ),
            ),
        )
        eq_(st.validate_scope(), None)
    
    def test_checking_object_and_subtable_sharing_global_name(self):
        """
        It's valid for an object and a sub-table to share the global name.
        
        """
        st = SymbolTable("global",
            (
                Bind("today", BoolVar()),
            ),
            SymbolTable("today", ()),
        )
        eq_(st.validate_scope(), None)
    
    def test_checking_object_and_subtable_sharing_localized_name(self):
        """
        It's valid for an object and a sub-table to share the localized name.
        
        """
        st1 = SymbolTable("global",
            (
                Bind("current_day", BoolVar(), es="hoy"),
            ),
            SymbolTable("today", (), es="hoy"),
        )
        st2 = SymbolTable("global",
            (
                Bind("current_day", BoolVar(), es="hoy"),
            ),
            # This sub-name will be called "hoy" in Spanish too:
            SymbolTable("hoy", ()),
        )
        eq_(st1.validate_scope(), None)
        eq_(st2.validate_scope(), None)
    
    def test_checking_duplicate_object_global_names(self):
        """
        Two objects cannot have the same global names in the same table.
        
        """
        st = SymbolTable("global",
            (
                Bind("e", Number(2.7183), es_VE=u"número e"),
                Bind("pi", Number(3.1416)),
                Bind("e", Number(2.71828), es_ES=u"número e"),
            ),
        )
        assert_raises(ScopeError, st.validate_scope)
    
    def test_checking_duplicate_object_localized_names(self):
        """
        Two objects cannot have the same localized names in the same table.
        
        """
        st1 = SymbolTable("global",
            (
                Bind("e", Number(2.7183), es_VE=u"número e"),
                Bind("pi", Number(3.1416)),
                Bind("eulers-number", Number(2.71828), es_VE=u"número e"),
            ),
        )
        st2 = SymbolTable("global",
            (
                Bind("e", Number(2.7183), es_VE=u"número e"),
                Bind("pi", Number(3.1416)),
                # These object will be called "número e" in Spanish too:
                Bind(u"número e", Number(2.71828)),
            ),
        )
        assert_raises(ScopeError, st1.validate_scope)
        assert_raises(ScopeError, st2.validate_scope)
    
    def test_checking_duplicate_subtable_global_names(self):
        """
        Two sub-tables cannot have the same global names in the same
        parent symbol table.
        
        """
        st = SymbolTable("global",
            (),
            SymbolTable("maths", ()),
            SymbolTable("computing", ()),
            SymbolTable("maths", (), es=u"matemática"),
        )
        assert_raises(ScopeError, st.validate_scope)
    
    def test_checking_duplicate_subtable_localized_names(self):
        """
        Two sub-tables cannot have the same global names in the same
        parent table.
        
        """
        st1 = SymbolTable("global",
            (),
            SymbolTable("maths", (), es=u"matemática"),
            SymbolTable("computing", ()),
            SymbolTable("mathematics", (), es=u"matemática"),
        )
        st2 = SymbolTable("global",
            (),
            SymbolTable("maths", (), es=u"matemática"),
            SymbolTable("computing", ()),
            # This sub-table will be called "matemática" in Spanish too:
            SymbolTable(u"matemática", ()),
        )
        assert_raises(ScopeError, st1.validate_scope)
        assert_raises(ScopeError, st2.validate_scope)
    
    def test_name_clash_in_grand_children(self):
        """
        The scope must be validated even inside the sub-tables.
        
        """
        sciences_st1 = SymbolTable("sciences",
            (),
            SymbolTable("maths", (), es=u"matemática"),
            SymbolTable("computing", ()),
            SymbolTable("maths", ()),
        )
        sciences_st2 = SymbolTable("sciences",
            (),
            SymbolTable("maths", (), es=u"matemática"),
            SymbolTable("computing", ()),
            SymbolTable("mathematics", (), es=u"matemática"),
        )
        sciences_st3 = SymbolTable("sciences",
            (),
            SymbolTable("maths", (), es=u"matemática"),
            SymbolTable("computing", ()),
            # This sub-table will be called "matemática" in Spanish too:
            SymbolTable(u"matemática", ()),
        )
        # Now a name clash at the objects level:
        sciences_st4 = SymbolTable("global",
            (
                Bind("foo", BoolVar()),
                Bind("foo", TrafficLightVar(), es="bar"),
            )
        )
        
        st1 = SymbolTable("global", (), sciences_st1,
                          SymbolTable("society", ()))
        st2 = SymbolTable("global", (), sciences_st2,
                          SymbolTable("society", ()))
        st3 = SymbolTable("global", (), sciences_st3,
                          SymbolTable("society", ()))
        st4 = SymbolTable("global", (), sciences_st4)
        
        assert_raises(ScopeError, st1.validate_scope)
        assert_raises(ScopeError, st2.validate_scope)
        assert_raises(ScopeError, st3.validate_scope)
        assert_raises(ScopeError, st4.validate_scope)
    
    def test_retrieving_namespace_without_children(self):
        """
        A namespace shouldn't have sub-namespaces if the original symbol table
        doesn't have sub-tables.
        
        """
        bool_var = BoolVar()
        traffic = TrafficLightVar()
        st = SymbolTable("global",
            (
                Bind("bool", bool_var, es="booleano"),
                Bind("traffic", traffic, es=u"tráfico")
            ),
        )
        
        # Checking the namespace:
        global_namespace = st.get_namespace()
        eq_(len(global_namespace.subnamespaces), 0)
        
        # Checking the namespace in Castilian:
        castilian_namespace = st.get_namespace("es")
        eq_(len(castilian_namespace.subnamespaces), 0)
    
    def test_retrieving_namespace_with_children(self):
        """
        A namespace should have sub-namespaces for the sub-tables of the
        original symbol table.
        
        """
        bool_var = BoolVar()
        traffic = TrafficLightVar()
        st = SymbolTable("global",
            (
                Bind("bool", bool_var, es="booleano"),
                Bind("traffic", traffic, es=u"tráfico")
            ),
            SymbolTable("foo",
                (
                    Bind("bar", bool_var, es="fulano"),
                    Bind("baz", traffic, es="mengano"),
                ),
            ),
        )
        
        # Checking the namespace:
        global_namespace = st.get_namespace()
        eq_(len(global_namespace.subnamespaces), 1)
        global_subnamespace = global_namespace.subnamespaces["foo"]
        global_subnamespace_objects = {
            'bar': bool_var,
            'baz': traffic,
        }
        eq_(global_subnamespace.objects, global_subnamespace_objects)
        
        # Checking the namespace in Castilian:
        castilian_namespace = st.get_namespace("es")
        eq_(len(castilian_namespace.subnamespaces), 1)
        castilian_subnamespace = castilian_namespace.subnamespaces["foo"]
        castilian_subnamespace_objects = {
            'fulano': bool_var,
            'mengano': traffic,
        }
        eq_(castilian_subnamespace.objects, castilian_subnamespace_objects)
    
    def test_retrieving_namespace_with_untrastlated_contents(self):
        """
        When a namespace is requested in a locale which is not available,
        the namespace with global names should be returned isttead.
        
        """
        bool_var = BoolVar()
        traffic = TrafficLightVar()
        st = SymbolTable("global",
            (
                Bind("bool", BoolVar(), es="booleano"),
                Bind("traffic", TrafficLightVar(), es=u"tráfico")
            ),
            SymbolTable("foo",
                (
                    Bind("bar", bool_var, es="fulano"),
                    Bind("baz", traffic, es="mengano"),
                ),
            ),
        )
        
        # Checking the namespace:
        namespace = st.get_namespace("fr")
        eq_(len(namespace.subnamespaces), 1)
        subnamespace = namespace.subnamespaces["foo"]
        subnamespace_objects = {
            'bar': bool_var,
            'baz': traffic,
        }
        eq_(subnamespace.objects, subnamespace_objects)
        expected_unbound_objects_global = {
            'bool': BoolVar(),
            'traffic': TrafficLightVar(),
        }
        eq_(namespace.objects, expected_unbound_objects_global)
    
    def test_retrieving_namespace_with_partially_untrastlated_contents(self):
        """
        When a namespace is requested in a locale in which not all items are
        available, the namespace with global names should be returned instead.
        
        """
        bool_var = BoolVar()
        traffic = TrafficLightVar()
        st = SymbolTable("global",
            (
                Bind("bool", BoolVar(), es="booleano", fr=u"booléen"),
                Bind("traffic", TrafficLightVar(), es=u"tráfico")
            ),
            SymbolTable("foo",
                (
                    Bind("bar", bool_var, es="fulano"),
                    Bind("baz", traffic, es="mengano", fr="bonjour"),
                ),
            ),
        )
        
        # Checking the namespace:
        namespace = st.get_namespace("fr")
        eq_(len(namespace.subnamespaces), 1)
        subnamespace = namespace.subnamespaces["foo"]
        subnamespace_objects = {
            'bar': bool_var,
            'bonjour': traffic,
        }
        eq_(subnamespace.objects, subnamespace_objects)
        expected_unbound_objects_global = {
            u'booléen': BoolVar(),
            'traffic': TrafficLightVar(),
        }
        eq_(namespace.objects, expected_unbound_objects_global)
    
    def test_equivalence(self):
        objects1 = lambda: [Bind("dish", String("cachapa")),
                            Bind("drink", String("empanada"))]
        objects2 = lambda: [Bind("drink", String("empanada")),
                            Bind("dish", String("cachapa"))]
        objects3 = lambda: [Bind("pi", Number(3.1416))]
        
        st1 = SymbolTable("foo", objects1())
        st2 = SymbolTable("foo", objects1())
        st3 = SymbolTable("foo", objects1(), es="fulano")
        st4 = SymbolTable("foo", objects1(), es="fulano")
        st5 = SymbolTable("foo", objects2())
        st6 = SymbolTable("foo", objects3())
        st7 = SymbolTable("foo", objects2(), es="fulano")
        st8 = SymbolTable("foo", objects3(), es_VE="fulano")
        st9 = SymbolTable("bar", objects1())
        st10 = SymbolTable("foo", objects1())
        st11 = SymbolTable(
            "foo", objects1(), SymbolTable("bar", []), SymbolTable("baz", []))
        st12 = SymbolTable(
            "foo", objects1(), SymbolTable("baz", []), SymbolTable("bar", []))
        
        # Moving st10 into the "baz" symbol table:
        SymbolTable("baz", [], st10)
        
        ok_(st1 == st2)
        ok_(st1 == st5)
        ok_(st1 == st10)
        ok_(st2 == st1)
        ok_(st2 == st5)
        ok_(st2 == st10)
        ok_(st3 == st4)
        ok_(st3 == st7)
        ok_(st4 == st3)
        ok_(st4 == st7)
        ok_(st5 == st1)
        ok_(st5 == st2)
        ok_(st5 == st10)
        ok_(st7 == st3)
        ok_(st7 == st4)
        ok_(st10 == st1)
        ok_(st10 == st2)
        ok_(st10 == st5)
        ok_(st11 == st12)
        ok_(st12 == st11)
        
        ok_(st1 != None)
        ok_(st1 != Bind("foo", String("cachapa")))
        
        ok_(st1 != st3)
        ok_(st1 != st4)
        ok_(st1 != st6)
        ok_(st1 != st7)
        ok_(st1 != st8)
        ok_(st1 != st9)
        ok_(st1 != st11)
        ok_(st1 != st12)
        ok_(st2 != st3)
        ok_(st2 != st4)
        ok_(st2 != st6)
        ok_(st2 != st7)
        ok_(st2 != st8)
        ok_(st2 != st9)
        ok_(st2 != st11)
        ok_(st2 != st12)
        ok_(st3 != st1)
        ok_(st3 != st2)
        ok_(st3 != st5)
        ok_(st3 != st6)
        ok_(st3 != st8)
        ok_(st3 != st9)
        ok_(st3 != st10)
        ok_(st3 != st11)
        ok_(st3 != st12)
        ok_(st4 != st1)
        ok_(st4 != st2)
        ok_(st4 != st5)
        ok_(st4 != st6)
        ok_(st4 != st8)
        ok_(st4 != st9)
        ok_(st4 != st10)
        ok_(st4 != st11)
        ok_(st4 != st12)
        ok_(st5 != st3)
        ok_(st5 != st4)
        ok_(st5 != st6)
        ok_(st5 != st7)
        ok_(st5 != st8)
        ok_(st5 != st9)
        ok_(st5 != st11)
        ok_(st5 != st12)
        ok_(st6 != st1)
        ok_(st6 != st2)
        ok_(st6 != st3)
        ok_(st6 != st4)
        ok_(st6 != st5)
        ok_(st6 != st7)
        ok_(st6 != st8)
        ok_(st6 != st9)
        ok_(st6 != st10)
        ok_(st6 != st11)
        ok_(st6 != st12)
        ok_(st7 != st1)
        ok_(st7 != st2)
        ok_(st7 != st5)
        ok_(st7 != st6)
        ok_(st7 != st8)
        ok_(st7 != st9)
        ok_(st7 != st10)
        ok_(st7 != st11)
        ok_(st7 != st12)
        ok_(st8 != st1)
        ok_(st8 != st2)
        ok_(st8 != st3)
        ok_(st8 != st4)
        ok_(st8 != st5)
        ok_(st8 != st6)
        ok_(st8 != st7)
        ok_(st8 != st9)
        ok_(st8 != st10)
        ok_(st8 != st11)
        ok_(st8 != st12)
        ok_(st9 != st1)
        ok_(st9 != st2)
        ok_(st9 != st3)
        ok_(st9 != st4)
        ok_(st9 != st5)
        ok_(st9 != st6)
        ok_(st9 != st7)
        ok_(st9 != st8)
        ok_(st9 != st10)
        ok_(st9 != st11)
        ok_(st9 != st12)
        ok_(st10 != st3)
        ok_(st10 != st4)
        ok_(st10 != st6)
        ok_(st10 != st7)
        ok_(st10 != st8)
        ok_(st10 != st9)
        ok_(st11 != st1)
        ok_(st11 != st2)
        ok_(st11 != st3)
        ok_(st11 != st4)
        ok_(st11 != st5)
        ok_(st11 != st6)
        ok_(st11 != st7)
        ok_(st11 != st8)
        ok_(st11 != st9)
        ok_(st11 != st10)
        ok_(st12 != st1)
        ok_(st12 != st2)
        ok_(st12 != st3)
        ok_(st12 != st4)
        ok_(st12 != st5)
        ok_(st12 != st6)
        ok_(st12 != st7)
        ok_(st12 != st8)
        ok_(st12 != st9)
        ok_(st12 != st10)
    
    def test_string(self):
        # With ASCII names:
        st2 = SymbolTable("grand-child", [])
        st1 = SymbolTable("parent", (), st2)
        st0 = SymbolTable("global", (), st1)
        eq_(str(st0), "Symbol table global")
        eq_(str(st1), "Symbol table global:parent")
        eq_(str(st2), "Symbol table global:parent:grand-child")
        # With Unicode characters:
        st2 = SymbolTable(u"gránd-chíld", [])
        st1 = SymbolTable(u"párênt", (), st2)
        st0 = SymbolTable(u"glòbál", (), st1)
        eq_(str(st0), "Symbol table glòbál")
        eq_(str(st1), "Symbol table glòbál:párênt")
        eq_(str(st2), "Symbol table glòbál:párênt:gránd-chíld")
    
    def test_unicode(self):
        # With ASCII names:
        st2 = SymbolTable("grand-child", [])
        st1 = SymbolTable("parent", (), st2)
        st0 = SymbolTable("global", (), st1)
        eq_(unicode(st0), "Symbol table global")
        eq_(unicode(st1), "Symbol table global:parent")
        eq_(unicode(st2), "Symbol table global:parent:grand-child")
        # With Unicode characters:
        st2 = SymbolTable(u"gránd-chíld", [])
        st1 = SymbolTable(u"párênt", (), st2)
        st0 = SymbolTable(u"glòbál", (), st1)
        eq_(unicode(st0), u"Symbol table glòbál")
        eq_(unicode(st1), u"Symbol table glòbál:párênt")
        eq_(unicode(st2), u"Symbol table glòbál:párênt:gránd-chíld")


class TestNamespaces(object):
    """Tests for the namespaces."""
    
    def test_subnamespaces_are_optional(self):
        """Namespaces may not have sub-namespaces."""
        st = Namespace(objects={})
        eq_(st.subnamespaces, {})
    
    def test_retrieving_existing_global_object(self):
        objects = {
            'bool': BoolVar(),
            'traffic': TrafficLightVar(),
        }
        st = Namespace(objects)
        requested_object = st.get_object("bool")
        eq_(requested_object, BoolVar())
    
    def test_retrieving_existing_2nd_level_object(self):
        sub_objects = {
            'bool': BoolVar(),
            'traffic': TrafficLightVar(),
        }
        global_objects = {
            'foo': TrafficLightVar(),
        }
        sub_namespace = {'sub1': Namespace(sub_objects)}
        st = Namespace(global_objects, sub_namespace)
        requested_object = st.get_object("bool", ["sub1"])
        eq_(requested_object, BoolVar())
    
    def test_retrieving_existing_3rd_level_object(self):
        third_level_objects = {
            'bool': BoolVar(),
        }
        second_level_objects = {
            'traffic': TrafficLightVar(),
        }
        global_objects = {
            'foo': TrafficLightVar(),
            'traffic-violation': TrafficViolationFunc(String("pedestrians")),
        }
        third_level_namespaces = {'sub2': Namespace(third_level_objects)}
        second_level_namespaces = {
            'sub1': Namespace(second_level_objects, third_level_namespaces)}
        st = Namespace(global_objects, second_level_namespaces)
        requested_object = st.get_object("bool", ["sub1", "sub2"])
        eq_(requested_object, BoolVar())
    
    def test_retrieving_object_in_non_existing_subtable(self):
        global_objects = {
            'foo': TrafficLightVar(),
            'traffic-violation': TrafficViolationFunc(String("pedestrians")),
        }
        st = Namespace(global_objects,)
        assert_raises(ScopeError, st.get_object, "foo", ["doesn't", "exist"])
    
    def test_retrieving_non_existing_object(self):
        global_objects = {
            'foo': TrafficLightVar(),
            'traffic-violation': TrafficViolationFunc(String("pedestrians")),
        }
        st = Namespace(global_objects,)
        assert_raises(ScopeError, st.get_object, "bool")

