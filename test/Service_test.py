#!/usr/bin/env python
# coding: utf-8

import unittest, sys

sys.path.append('..')
import Service


class TestService(unittest.TestCase):
    def setUp(self):
        self.serv = Service()

    def test_process(self):
        data = {"CommandType": "GetTagsList", "Code": 100, "Data": []}
        self.serv.process(data)