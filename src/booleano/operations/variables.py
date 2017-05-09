# -*- coding: utf-8 -*-
"""
this module contains all usable variables for native python type.
"""
import datetime
import re

import six

from booleano.operations.operands.classes import Variable
from booleano.operations.operands.constants import String
from booleano.parser.symbol_table_builder import SymbolTableBuilder

variable_symbol_table_builder = SymbolTableBuilder()


@variable_symbol_table_builder.register(type(None))
class NativeVariable(Variable):
    """
    a generic Bindable item that will resolve from the context with
    his given name. it shall be subclass for more specific operations, but
    it work as is using the python type operations.
    
    it can be lazy if the given context_name is a callable, in this case, the callable
    will be called with the current context
    """
    operations = {
        "equality",           # ==, !=
        "inequality",         # >, <, >=, <=
        "boolean",            # Logical values
    }

    def __init__(self, context_name):
        self.evaluated = False
        self.context_name = context_name
        super(NativeVariable, self).__init__()

    def to_python(self, context):
        """Return the value of the ``bool`` context item"""
        self.evaluated = True
        if callable(self.context_name):
            return self.context_name(context)
        return context[self.context_name]

    def equals(self, value, context):
        """Does ``value`` equal this variable?"""
        self.evaluated = True
        if isinstance(value, (String, six.text_type)):
            value = self._from_native_string(six.text_type(value))
        return self.to_python(context) == value

    def greater_than(self, value, context):
        """Does thes variable is greater than ``value``"""
        self.evaluated = True
        if isinstance(value, (String, six.text_type)):
            value = self._from_native_string(six.text_type(value))
        return self.to_python(context) > value

    def less_than(self, value, context):
        """Does thes variable is lesser than ``value``"""
        self.evaluated = True
        if isinstance(value, (String, six.text_type)):
            value = self._from_native_string(six.text_type(value))
        return self.to_python(context) < value

    def __call__(self, context):
        """Does this variable evaluate to True?"""
        self.evaluated = True
        return bool(self.to_python(context))

    def _from_native_string(self, value):
        """
        special case where a variable can interperete
        a sting to other think (a date, a duration ?)
        :param value:
        :return:
        """
        return value

    def __str__(self):
        """Return the Unicode representation of this variable."""
        return 'Scop variable for %s [%s]' % (self.context_name, self.__class__.__name__)

    def __repr__(self):
        """Represent this variable."""
        return '<Scop variable for %s [%s]>' % (self.context_name, self.__class__.__name__)


@variable_symbol_table_builder.register(list)
@variable_symbol_table_builder.register(tuple)
class NativeCollectionVariable(NativeVariable):
    operations = {
        "equality",  # ==, !=
        "inequality",  # >, <, >=, <=
        "boolean",  # Logical values
        "membership",
    }

    def belongs_to(self, value, context):
        """does this variable belong to (in) """
        self.evaluated = True
        if isinstance(value, String):
            value = self._from_native_string(value)
        return value in self.to_python(context)

    def is_subset(self, value, context):
        """
        a strict subset contains some element, but not all.
        (belongs_to can contains all elements)
        :param value:
        :param context:
        :return:
        """
        self.evaluated = True
        if isinstance(value, String):
            value = self._from_native_string(value)
        cv = self.to_python(context)
        return cv != value and value in cv


@variable_symbol_table_builder.register(int)
@variable_symbol_table_builder.register(float)
class NumberVariable(NativeVariable):
    pass


@variable_symbol_table_builder.register(bool)
class BooleanVariable(NativeVariable):
    pass


@variable_symbol_table_builder.register(six.text_type)
class StringVariable(NativeCollectionVariable):
    pass


@variable_symbol_table_builder.register(set)
@variable_symbol_table_builder.register(frozenset)
class SetVariable(NativeCollectionVariable):

    def cast_val(self, value):
        if not isinstance(value, set):
            value = {value}
        return value

    def belongs_to(self, value, context):
        """does this variable belong to (in) """
        self.evaluated = True
        cv = self.to_python(context)
        value = self.cast_val(value)

        return value <= cv

    def is_subset(self, value, context):
        """
        a strict subset contains some element, but not all.
        (belongs_to can contains all elements)
        :param value:
        :param context:
        :return:
        """
        self.evaluated = True
        cv = self.to_python(context)
        value = self.cast_val(value)

        return value < cv


@variable_symbol_table_builder.register(datetime.timedelta)
class DurationVariable(NativeVariable):
    formats = [
        (
            r'^((?P<days>\d+?) ?d(ays)?)? *'
            r'((?P<hours>\d+?) ?h(r|ours?)?)? *'
            r'((?P<minutes>\d+?) ?m(inutes)?)? *'
            r'((?P<seconds>\d+?) ?s(econds)?)? *$'
        )
    ]

    def __init__(self, context_name, formats=None):

        if isinstance(formats, six.text_type):
            self.formats = (formats, )
        elif formats is not None:
            self.formats = formats

        self.regexps = [
            re.compile(regex) for regex in self.formats
        ]
        super(DurationVariable, self).__init__(context_name)

    def _from_native_string(self, value):
        """
        parse a string as a date using self.formats.
        :param value: the date as a string. matching one of the format
        :return: the datetime object
        :rtype: datetime.datetime
        """
        for regex in self.regexps:
            match = regex.search(value)
            if match:
                res = {unit: int(val) for unit, val in match.groupdict().items() if val is not None}
                if res:
                    return datetime.timedelta(**res)
        raise ValueError("bad date format for %s: tied %r" % (value, self.formats))


@variable_symbol_table_builder.register(datetime.datetime)
class DateTimeVariable(NativeVariable):
    formats = (
        "%d/%m/%Y %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    )

    def __init__(self, context_name, formats=None):
        if isinstance(formats, six.text_type):
            self.formats = (formats, )
        elif formats is not None:
            self.formats = formats
        super(DateTimeVariable, self).__init__(context_name)

    def _from_native_string(self, value):
        """
        parse a string as a date using self.formats.
        :param value: the date as a string. matching one of the format
        :return: the datetime object
        :rtype: datetime.datetime
        """
        for format in self.formats:
            try:
                return datetime.datetime.strptime(value, format)
            except ValueError:
                pass
        raise ValueError("bad date format for %s: tied %r" % (value, self.formats))


@variable_symbol_table_builder.register(datetime.date)
class DateVariable(DateTimeVariable):
    formats = (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
    )

    def _from_native_string(self, value):
        return super(DateVariable, self)._from_native_string(value).date()
