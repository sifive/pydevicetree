#!/usr/bin/env python3

import unittest
from source import parseTree
from ast import *

class TestDevicetree(unittest.TestCase):
    def setUp(self):
        self.source = """
        /dts-v1/;
        chosen {
            my-cpu = "/cpus/cpu@0";
        };
        / {
            cpus {
                cpu@0 {
                    compatible = "riscv";
                    reg = <0>;
                };
            };
        };
        """

    def test_get_field(self):
        tree = parseTree(self.source)

        self.assertEqual(type(tree), Devicetree)
        self.assertEqual(type(tree.elements[1]), Node)

        cpu = tree.elements[2].children[0].children[0]

        self.assertEqual(type(cpu), Node)
        self.assertEqual(cpu.name, "cpu")
        self.assertEqual(cpu.address, 0)
        self.assertEqual(cpu.get_field("compatible"), "riscv")
        self.assertEqual(cpu.get_field("reg"), 0)

    def test_match(self):
        tree = parseTree(self.source)

        self.assertEqual(type(tree), Devicetree)

        def func(cpu):
            self.assertEqual(type(cpu), Node)
            self.assertEqual(cpu.name, "cpu")
            self.assertEqual(cpu.address, 0)
            self.assertEqual(cpu.get_field("compatible"), "riscv")
            self.assertEqual(cpu.get_field("reg"), 0)

        tree.match("riscv", func)

    def test_chosen(self):
        tree = parseTree(self.source)

        self.assertEqual(type(tree), Devicetree)

        def func(values):
            self.assertEqual(values[0], "/cpus/cpu@0")

        tree.chosen("my-cpu", func)

if __name__ == "__main__":
    unittest.main()
