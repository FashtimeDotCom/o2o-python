#!/usr/bin/env python
# coding: utf-8

import unittest, sys

sys.path.append('..')
from Scan import *


class TestScan(unittest.TestCase):
    ''' 扫描服务模块测试 '''

    def setUp(self):
        self.scan = Scan()
        self.scan.start()

    def tearDown(self):
        self.scan = None

    def test_scan(self):
        self.assertTrue(isinstance(self.scan.r, redis.client.StrictRedis))