#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

import unittest

from pydevicetree.source.grammar import *

class TestGrammar(unittest.TestCase):
    def test_label(self):
        from pydevicetree.ast import Label
        self.assertEqual(label.parseString("mylabel:")[0], Label("mylabel"))

    def test_node_path(self):
        from pydevicetree.ast import Path
        self.assertEqual(node_path.parseString("/path/to/foo@deadbeef")[0], Path("/path/to/foo@deadbeef"))

    def test_reference(self):
        from pydevicetree.ast import Label, Path
        self.assertEqual(reference.parseString("&mylabel")[0].label, Label("mylabel"))
        self.assertEqual(reference.parseString("&{/path/to/foo@deadbeef}")[0].path, Path("/path/to/foo@deadbeef"))

    def test_arith_expr(self):
        self.assertEqual(arith_expr.parseString("(1 + 2)").asList(), [3])
        self.assertEqual(arith_expr.parseString("(1 + 0xa)").asList(), [11])
        self.assertEqual(arith_expr.parseString("(1 ? 2 : 3)").asList(), [2])
        self.assertEqual(arith_expr.parseString("(1 + (2 + 3))").asList(), [6])

    def test_bytestring(self):
        self.assertEqual(bytestring.parseString("[00 01 02 03]")[0], bytearray([0, 1, 2, 3]))
        self.assertEqual(bytestring.parseString("[00010203]")[0], bytearray([0, 1, 2, 3]))
        self.assertEqual(bytestring.parseString("[31 14 15 92 af]")[0], bytearray([0x31, 0x14, 0x15, 0x92, 0xaf]))

        # we don't really handle lables here, so assert that they're removed
        self.assertEqual(bytestring.parseString("[31 14 15 label: 92 af]")[0], bytearray([0x31, 0x14, 0x15, 0x92, 0xaf]))

    def test_cell_array(self):
        self.assertEqual(cell_array.parseString("<1>")[0], [1])
        self.assertEqual(cell_array.parseString("<1 2 3>")[0], [1, 2, 3])
        self.assertEqual(cell_array.parseString("<1 (1 + 1) 3>")[0], [1, 2, 3])

        # we don't really handle lables here, so assert that they're removed
        self.assertEqual(cell_array.parseString("<1 2 label: 3>")[0], [1, 2, 3])

    def test_prop_value_comma_separated(self):
        from pydevicetree.ast import PropertyValues, CellArray, StringList
        # this test taken straight from the Devicetree v0.2 specification page 52
        teststring = "example = <0xf00f0000 19>, \"a strange property format\";"

        prop = property_assignment.parseString(teststring)[0]
        self.assertEqual(prop.name, "example")

        self.assertEqual(type(prop.values), PropertyValues)

        self.assertEqual(type(prop.values[0]), CellArray)
        self.assertEqual(prop.values[0][0], 0xf00f0000)
        self.assertEqual(prop.values[0][1], 19)

        self.assertEqual(type(prop.values[1]), StringList)
        self.assertEqual(prop.values[1][0], "a strange property format")

    def test_node_definition(self):
        from pydevicetree.ast import Node
        node = node_definition.parseString("label: my-node@DEADBEEF { my-property; compatible = \"my-node\"; };")[0]

        self.assertEqual(type(node), Node)
        self.assertEqual(node.label, "label")
        self.assertEqual(node.name, "my-node")
        self.assertEqual(node.properties[0].name, "my-property")
        self.assertEqual(node.properties[1].name, "compatible")
        self.assertEqual(node.properties[1].values[0], "my-node")
        self.assertEqual(node.children, [])

    def test_directive(self):
        from pydevicetree.ast import Directive
        dtsv1 = directive.parseString("/dts-v1/;")[0]

        self.assertEqual(type(dtsv1), Directive)
        self.assertEqual(dtsv1.directive, "/dts-v1/")
        self.assertEqual(dtsv1.option, None)

if __name__ == "__main__":
    unittest.main()
