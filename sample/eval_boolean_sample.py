# -*- coding: utf-8 -*-
import datetime

from booleano.utils import eval_boolean

sample = [
    {"name": "katara", "age": 14, "birthdate": datetime.date(1985, 1, 1)},
    {"name": "aang", "age": 112, "birthdate": datetime.date(1888, 1, 1)},
    {"name": "zuko", "age": 16, "birthdate": datetime.date(1983, 1, 1)},
    {"name": "sokka", "age": 15, "birthdate": datetime.date(1984, 1, 1)},
]


consts = {
    'majority': 18,
    'very old': 99
}

stmt = 'age < const:majority & "o" in name & birthdate > "1983-02-02"'

eval_boolean(
    'age < const:majority & "o" in name & birthdate > "1983-02-02"',
    {"name": "sokka", "age": 15, "birthdate": datetime.date(1984, 1, 1)},
    {'majority': 18},
    grammar_tokens={'belongs_to': 'in'}
)


for character in sample:
    res = eval_boolean(stmt, character, consts, grammar_tokens={'belongs_to': 'in'})
    code = '32' if res else '31'
    print('\033[%sm%r\x1b[0m' % (code, character))
