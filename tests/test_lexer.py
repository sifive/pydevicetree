#!/usr/bin/env python3

import unittest
from source.lexer import *

class TestLexer(unittest.TestCase):
    def test_arith_expr(self):
        self.assertEqual(arith_expr.parseString("(1 + 2)").asList(), [[1, '+', 2]])
        self.assertEqual(arith_expr.parseString("(1 + 0xa)").asList(), [[1, '+', 10]])
        self.assertEqual(arith_expr.parseString("(1 ? 2 : 3)").asList(), [[1, '?', 2, ':', 3]])
        self.assertEqual(arith_expr.parseString("(1 + (2 + 3))").asList(), [[1, '+', [2, '+', 3]]])

    def test_array(self):
        self.assertEqual(array.parseString("<1>").asList(), [1])

    def test_node_definition(self):
        from ast.classes import Node
        node = node_definition.parseString("label: my-node@DEADBEEF { my-property; compatible = \"my-node\"; };")[0]

        self.assertEqual(type(node), Node)
        self.assertEqual(node.label, "label")
        self.assertEqual(node.name, "my-node")
        self.assertEqual(node.properties[0].name, "my-property")
        self.assertEqual(node.properties[1].name, "compatible")
        self.assertEqual(node.properties[1].values[0], "my-node")
        self.assertEqual(node.children, [])

    def test_directive(self):
        from ast.classes import Directive
        dtsv1 = directive.parseString("/dts-v1/;")[0]

        self.assertEqual(type(dtsv1), Directive)
        self.assertEqual(dtsv1.directive, "/dts-v1/")
        self.assertEqual(dtsv1.options, '')

if __name__ == "__main__":
    unittest.main()
