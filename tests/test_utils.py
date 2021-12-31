# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import datetime
import logging

from nose.tools.trivial import eq_, ok_

from booleano.utils import eval_boolean, get_boolean_evaluator

logger = logging.getLogger(__name__)


class TestBooleanEval(object):
    def test_eval(self):
        ok_(
            eval_boolean(
                '"o" ∈ name & birthdate > "1983-02-02"',
                {"name": "sokka", "age": 15, "birthdate": datetime.date(1984, 1, 1)},
            )
        )

    def test_eval_grammar(self):
        ok_(
            eval_boolean(
                'age < const:majority & "o" in name & birthdate > "1983-02-02"',
                {"name": "sokka", "age": 15, "birthdate": datetime.date(1984, 1, 1)},
                {"majority": 18},
                grammar_tokens={"belongs_to": "in"},
            )
        )

    def test_eval_no_val(self):
        ok_(eval_boolean('"key" ∈ "keylogger"'))


class TestGetBooleanEvaluator(object):
    sample = [
        {"name": "katara", "age": 14, "birthdate": datetime.date(1985, 1, 1)},
        {"name": "aang", "age": 112, "birthdate": datetime.date(1888, 1, 1)},
        {"name": "zuko", "age": 16, "birthdate": datetime.date(1983, 1, 1)},
        {"name": "sokka", "age": 15, "birthdate": datetime.date(1984, 1, 1)},
    ]

    def test_call_no_args(self):
        ok_(get_boolean_evaluator('"key" ∈ "keylogger"')(None))

    def test_call_with(self):
        evaluator = get_boolean_evaluator(
            'age < const:majority & "o" in name & birthdate > "1983-02-02"',
            self.sample,
            {"majority": 18},
            grammar_tokens={"belongs_to": "in"},
        )
        for s, expected in zip(self.sample, (False, False, False, True)):
            eq_(evaluator(s), expected)
