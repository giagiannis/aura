#!/usr/bin/python

import sys
import random
import unittest
from aura.core import ApplicationDescriptionParser


class TestDescription(unittest.TestCase):
    def test_foo(self):
        desc = ApplicationDescriptionParser("example/demo")
        multi = {}
        for m in desc.get_description()['modules']:
            multi[m['name']] = random.randint(1,9)
        desc.set_multiplicities(multi)
        expanded = desc.expand_description()
        self.assertEqual(sum(multi.values()), len(expanded['modules']))
        result = {}
        for m in expanded['modules']:
            pref = m['name'][0:len(m['name'])-1]
            if pref not in result:
                result[pref]=0
            result[pref]+=1
        for key in multi:
            if key in result and key in multi:
                self.assertEqual(result[key], multi[key])
            else:
                self.assertEqual(multi[key], 1)

