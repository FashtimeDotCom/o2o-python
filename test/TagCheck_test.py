#!/usr/bin/env python
# coding: utf-8

import unittest, sys

sys.path.append('..')
from TagCheck import *


class TestTagcheck(unittest.TestCase):
    ''' 标签检查测试类 '''

    def setUp(self):
        self.check = TagCheck()
        self.check.start()

    def test_onLine(self):
        self.check.onLine()
		