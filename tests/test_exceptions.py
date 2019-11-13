#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

import unittest

from pydevicetree import *
from pyparsing import ParseException

class TestExceptions(unittest.TestCase):
    def test_bad_tree(self):
        with self.assertRaises(ParseException):
            Devicetree.from_dts("/dts-v1/; / { } // No semicolon")
        with self.assertRaises(ParseException):
            Devicetree.from_dts("/dts-v1/; / { #address-cells = <10; /* missing '>' */ };")

    def test_bad_node(self):
        with self.assertRaises(ParseException):
            Node.from_dts("/ { } // No semicolon")
        with self.assertRaises(ParseException):
            Node.from_dts("/ { #address-cells = <10; /* missing '>' */ };")

    def test_bad_property(self):
        with self.assertRaises(ParseException):
            Property.from_dts("reg = <0x0 0x1> // no semicolon")
        with self.assertRaises(ParseException):
            Property.from_dts("reg = <0x0 0x1 /* missing '>' */;")

if __name__ == "__main__":
    unittest.main()
