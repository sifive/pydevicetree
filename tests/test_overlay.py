#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

import unittest
import os

from pydevicetree.source import parseTree
from pydevicetree.ast import *

devicetreedir = "tests/devicetrees/include/"
devicetreebase = devicetreedir + "/base.dts"

class TestOverlay(unittest.TestCase):
    def test_devicetree(self):
        base = Devicetree.parseFile(devicetreebase)

        # /include/ directives are only followed if followIncludes is True
        full = Devicetree.parseFile(devicetreebase, followIncludes=True)
        
        self.assertEqual(type(base), Devicetree)
        self.assertEqual(type(full), Devicetree)
        
        baseuart = base.match("uart")[0]
        fulluart = full.match("uart")[0]
        for uart in [baseuart, fulluart]:
            self.assertEqual(type(uart), Node)
            self.assertEqual(uart.address, 0x1000);
            self.assertEqual(uart.get_fields("reg"), [0x1000, 0x1000])
            self.assertEqual(uart.get_field("reg-names"), "control")

        self.assertEqual(fulluart.get_field("status"), "okay")

        basepath = base.chosen("stdout-path")
        fullpath = full.chosen("stdout-path")
        self.assertEqual(basepath, None)
        self.assertEqual(fullpath, ["/soc/uart@1000"])

        cpus = full.get_by_path("/cpus")
        self.assertEqual(type(cpus), Node)
        self.assertEqual(len(cpus.children), 2)

if __name__ == "__main__":
    unittest.main()
