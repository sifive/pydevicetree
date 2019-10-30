#!/usr/bin/env python3

import unittest
from source.lexer import *

class TestLexer(unittest.TestCase):
    def test_arith_expr(self):
        self.assertEqual(arith_expr.parseString("1").asList(), [1])
        self.assertEqual(arith_expr.parseString("1 + 2").asList(), [[1, '+', 2]])

if __name__ == "__main__":
    unittest.main()
