# -*- coding: utf-8 -*-
"""
this module contains all usable variables for native python type.
"""
import datetime
import six

from booleano.operations.operands.classes import Variable
from booleano.operations.operands.constants import String


class NativeVariable(Variable):
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
        return context[self.context_name]

    def equals(self, value, context):
        """Does ``value`` equal this variable?"""
        self.evaluated = True
        if isinstance(value, (String, six.text_type)):
            value = self._from_native_string(six.text_type(value))
        return context[self.context_name] == value

    def greater_than(self, value, context):
        """Does thes variable is greater than ``value``"""
        self.evaluated = True
        if isinstance(value, (String, six.text_type)):
            value = self._from_native_string(six.text_type(value))
        return context[self.context_name] > value

    def less_than(self, value, context):
        """Does thes variable is lesser than ``value``"""
        self.evaluated = True
        if isinstance(value, (String, six.text_type)):
            value = self._from_native_string(six.text_type(value))
        return context[self.context_name] < value

    def __call__(self, context):
        """Does this variable evaluate to True?"""
        self.evaluated = True
        return bool(context[self.context_name])

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
        return value in context[self.context_name]

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
        cv = context[self.context_name]
        return cv != value and value in cv


class IntegerVariable(NativeVariable):
    pass


class BooleanVariable(NativeVariable):
    pass


class StringVariable(NativeCollectionVariable):
    pass


class SetVariable(NativeCollectionVariable):

    def cast_val(self, value):
        if not isinstance(value, set):
            value = {value}
        return value

    def belongs_to(self, value, context):
        """does this variable belong to (in) """
        self.evaluated = True
        cv = context[self.context_name]
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
        cv = context[self.context_name]
        value = self.cast_val(value)

        return value < cv


class DateTimeVariable(NativeVariable):
    formats = (
        "%d/%m/%Y %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    )

    def __init__(self, context_name, formats=None):
        if formats is None:
            self.formats = self.formats
        elif isinstance(formats, six.text_type):
            self.formats = (formats,)
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


class DateVariable(DateTimeVariable):
    formats = (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
    )

    def _from_native_string(self, value):
        return super(DateVariable, self)._from_native_string(value).date()
