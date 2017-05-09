# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging

import six

logger = logging.getLogger(__name__)


class SymbolTableBuilder(object):
    """
    a builder that can create a symbolTable of NativeVariable from a sample of data
    each available NativeVariable can register themselver to a Builder to make him
    aware of his python type binding
    """

    def __init__(self, use_key=True):
        """
        create the SsymbolTableBuilder.
        :param use_key: tell if we should pas the key or the value of the sample to create the subclass
        """
        self.registered_variables = {}
        """
        the mapping from a python type to a Variable subclass
        """
        self.use_key = use_key

    def register(self, type_, variable_class=None):
        if type_ in self.registered_variables:
            raise Exception("the type %s is arleady registered to %s" % (type_, self.registered_variables[type_]))

        if variable_class is not None:
            self.registered_variables[type_] = variable_class
            return variable_class
        else:
            # work as a decorator of class
            def wrapper(_variable_class):
                return self.register(type_, _variable_class)

            return wrapper

    def find_for_type(self, type_):
        """
        resolve the best registered variable for this type.
        it accept subclass of a registered type.
        :param type type_: the type to find the best match
        :return: the best match
        :rtype: NativeVariable
        """
        found = None
        for registered_type in self.registered_variables.keys():
            if issubclass(type_, registered_type):
                # of this is the firt we found, or it's the more concrete class for this type
                if found is None or len(found.__mro__) < len(registered_type.__mro__):
                    found = registered_type
        if found is None:
            raise Exception("the type of data %(type)s has no registered variable type. "
                            "try to use @symbol_table_builder.register(%(type)s)" % dict(type=type_))
        return self.registered_variables[found]

    def __call__(self, name, sample):
        """
        create a SymbolTalbe from the sample data
        :param string name: the name of the symbolTable
        :param dict sample: the sample of data
        :return: the SymbolTable
        :rtype: SymbolTable
        """
        from booleano.parser import Bind, SymbolTable  # isort:skip

        binds = []
        for k, v in sample.items():
            var_type = v if isinstance(v, six.class_types) else type(v)

            var = self.find_for_type(var_type)

            binds.append(
                Bind(k, var(k if self.use_key else v))
            )
        return SymbolTable(name, binds)
