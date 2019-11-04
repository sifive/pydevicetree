#!/usr/bin/env python3

import unittest

from pydevicetree.source import parseTree
from pydevicetree.ast import *

class TestDevicetree(unittest.TestCase):
    def setUp(self):
        self.source = """
        /dts-v1/;
        chosen {
            my-cpu = "/cpus/cpu@0";
        };
        / {
            #address-cells = <2>;
            #size-cells = <2>;
            cpus {
                cpu@0 {
                    #address-cells = <1>;
                    compatible = "riscv";
                    reg = <0>;
                };
                cpu@1 {
                    #size-cells = <1>;
                    compatible = "riscv";
                    reg = <1>;
                };
            };
        };
        """

    def test_get_field(self):
        tree = parseTree(self.source)

        self.assertEqual(type(tree), Devicetree)

        cpu = tree.children[1].children[0].children[0]

        self.assertEqual(type(cpu), Node)
        self.assertEqual(cpu.name, "cpu")
        self.assertEqual(cpu.address, 0)
        self.assertEqual(cpu.get_field("compatible"), "riscv")
        self.assertEqual(cpu.get_field("reg"), 0)

    def test_cells(self):
        tree = parseTree(self.source)

        cpu0 = tree.match("riscv")[0]
        cpu1 = tree.match("riscv")[1]
        self.assertEqual(type(cpu0), Node)
        self.assertEqual(type(cpu1), Node)

        self.assertEqual(cpu0.address_cells(), 1)
        self.assertEqual(cpu0.size_cells(), 2)
        self.assertEqual(cpu1.address_cells(), 2)
        self.assertEqual(cpu1.size_cells(), 1)

    def test_match(self):
        tree = parseTree(self.source)

        self.assertEqual(type(tree), Devicetree)

        def func(cpu):
            self.assertEqual(type(cpu), Node)
            self.assertEqual(cpu.name, "cpu")
            self.assertEqual(cpu.address, cpu.get_field("reg"))
            self.assertEqual(cpu.get_field("compatible"), "riscv")

        tree.match("riscv", func)

    def test_chosen(self):
        tree = parseTree(self.source)

        self.assertEqual(type(tree), Devicetree)

        def func(values):
            self.assertEqual(values[0], "/cpus/cpu@0")

        tree.chosen("my-cpu", func)

if __name__ == "__main__":
    unittest.main()
