#!/usr/bin/env python3

import unittest
import os
from source import parseTree
from ast import *

devicetreedir = "tests/devicetrees/include/"
devicetreebase = devicetreedir + "/base.dts"

class TestOverlay(unittest.TestCase):
    def test_devicetree(self):
        with open(devicetreebase, 'r') as f:
            base = f.read()

        tree = parseTree(base, devicetreedir)

        self.assertEqual(type(tree), Devicetree)

        uart = tree.match("uart")[0]
        self.assertEqual(type(uart), Node)
        self.assertEqual(uart.address, 0x1000);
        self.assertEqual(uart.get_fields("reg"), [0x1000, 0x1000])
        self.assertEqual(uart.get_field("reg-names"), "control")

        path = tree.chosen("stdout-path")
        self.assertEqual(path, ["/soc/uart@1000"])

if __name__ == "__main__":
    unittest.main()
