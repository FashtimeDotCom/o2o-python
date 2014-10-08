#!/usr/bin/eny python
# coding:utf-8

import unittest, sys

sys.path.append('..')
from Socket import *


class TestSocket(unittest.TestCase):
    ''' Socket模块测试类 '''

    def setUp(self):
        self.socket = Socket()
        self.socket.start()

    def tearDown(self):
        self.socket = None

    def test_init(self):
        self.assertTrue(self.socket.is_alive());