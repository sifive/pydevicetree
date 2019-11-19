#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

import unittest

from pydevicetree.ast import *

class TestDevicetree(unittest.TestCase):
    def setUp(self):
        self.source = """
        /dts-v1/;
        /* ignore this comment */
        / {
            #address-cells = <1>; // ignore this comment
            #size-cells = <1>;
            aliases {
                cpu-alias = "/cpus/cpu@1";
            };
            chosen {
                my-cpu = "/cpus/cpu@0";
            };
            cpus {
                #address-cells = <1>;
                #size-cells = <0>;
                cpu0: cpu@0 {
                    compatible = "riscv";
                    reg = <0>;
                };
                cpu@1 {
                    /* ignore this comment */
                    compatible = "riscv";
                    reg = <1>;
                };
            };
            memory@80000000 {
                reg = <0x80000000 0x1000>;
                reg-names = "mem";
            };
            soc {
                delete-property {
                    delete-me = "foo";
                    /delete-property/ delete-me;
                };
                delete_label: delete-by-label {
                };
                delete-by-name {
                };
                /delete-node/ &delete_label;
                /delete-node/ delete-by-name;
            };
        };
        """
        self.tree = Devicetree.from_dts(self.source)

    def test_get_path(self):
        cpu0 = self.tree.match("riscv")[0]
        self.assertEqual(cpu0.get_path(), "/cpus/cpu@0")

    def test_get_by_path(self):
        cpu0 = self.tree.get_by_path("/cpus/cpu@0")
        self.assertEqual(cpu0.name, "cpu")
        self.assertEqual(cpu0.address, 0)
        self.assertEqual(cpu0.get_field("compatible"), "riscv")

        cpus = self.tree.get_by_path("/cpus")
        self.assertEqual(cpus.name, "cpus")
        self.assertEqual(len(cpus.children), 2)

        # get node by path without address when unambiguous
        memory = self.tree.get_by_path("/memory")
        self.assertEqual(type(memory), Node)

        # aliases can be part of the path
        cpu_alias = self.tree.get_by_path("cpu-alias")
        self.assertEqual(type(cpu_alias), Node)
        self.assertEqual(cpu_alias.get_field("reg"), 1)
        # also test with a Path
        cpu_alias = self.tree.get_by_path(Path("cpu-alias"))
        self.assertEqual(type(cpu_alias), Node)
        self.assertEqual(cpu_alias.get_field("reg"), 1)

    def test_delete_directive(self):
        soc = self.tree.get_by_path("/soc")
        self.assertEqual(type(soc), Node)
        self.assertEqual(len(soc.children), 1)

        delete_property = self.tree.get_by_path("/soc/delete-property")
        self.assertEqual(type(delete_property), Node)
        self.assertEqual(delete_property.get_field("delete-me"), None)

    def test_get_by_label(self):
        cpu0 = self.tree.get_by_label("cpu0")
        self.assertEqual(cpu0.name, "cpu")
        self.assertEqual(cpu0.address, 0)
        self.assertEqual(cpu0.get_field("compatible"), "riscv")

    def test_get_field(self):
        cpu = self.tree.match("riscv")[0]

        self.assertEqual(type(cpu), Node)
        self.assertEqual(cpu.name, "cpu")
        self.assertEqual(cpu.address, 0)
        self.assertEqual(cpu.get_field("compatible"), "riscv")
        self.assertEqual(cpu.get_field("reg"), 0)

    def test_cells(self):
        cpu0 = self.tree.match("riscv")[0]
        cpu1 = self.tree.match("riscv")[1]
        self.assertEqual(type(cpu0), Node)
        self.assertEqual(type(cpu1), Node)

        self.assertEqual(cpu0.address_cells(), 1)
        self.assertEqual(cpu0.size_cells(), 0)
        self.assertEqual(cpu1.address_cells(), 1)
        self.assertEqual(cpu1.size_cells(), 0)

    def test_filter(self):
        def matchFunc(n):
            return n.get_field("reg") == 1
        def cbFunc(n):
            self.assertEqual(n.get_field("compatible"), "riscv");

        filtered_nodes = self.tree.filter(matchFunc, cbFunc)

        # only the cpu1 node fulfills the matchFunc check
        self.assertEqual(len(filtered_nodes), 1)

    def test_match(self):
        def func(cpu):
            self.assertEqual(type(cpu), Node)
            self.assertEqual(cpu.name, "cpu")
            self.assertEqual(cpu.address, cpu.get_field("reg"))
            self.assertEqual(cpu.get_field("compatible"), "riscv")

        self.tree.match("riscv", func)

    def test_chosen(self):
        def func(values):
            self.assertEqual(values[0], "/cpus/cpu@0")

        self.tree.chosen("my-cpu", func)

        cpu = self.tree.get_by_path("/cpus/cpu@0")
        self.assertEqual(type(cpu), Node)
        self.assertEqual(cpu.get_path(), "/cpus/cpu@0")
        self.assertEqual(cpu.get_field("reg"), 0)

    def test_node_from_dts(self):
        node = Node.from_dts("uart0: uart@10013000 { compatible = \"sifive,uart0\"; };")

        self.assertEqual(type(node), Node)
        self.assertEqual(node.label, "uart0")
        self.assertEqual(node.name, "uart")
        self.assertEqual(node.address, 0x10013000)
        self.assertEqual(node.get_field("compatible"), "sifive,uart0")

    def test_property_from_dts(self):
        prop = Property.from_dts("reg = <0x1337 0x42>;")

        self.assertEqual(type(prop), Property)
        self.assertEqual(prop.name, "reg")
        self.assertEqual(prop.values, [0x1337, 0x42])

    def test_add_child(self):
        new_node = Node.from_dts("uart0: uart@10013000 { compatible = \"sifive,uart0\"; };")

        soc = self.tree.get_by_path("/soc")
        soc.add_child(new_node)

        uart = self.tree.get_by_path("/soc/uart@10013000")
        self.assertEqual(type(uart), Node)
        self.assertEqual(uart.label, "uart0")
        self.assertEqual(uart.name, "uart")
        self.assertEqual(uart.address, 0x10013000)
        self.assertEqual(uart.get_field("compatible"), "sifive,uart0")

    def test_reg_array(self):
        spi_node = Node.from_dts("""spi@110013000 {
            reg = <0x1 0x10013000 0x1000 0x0 0x20000000 0x10000000>;
            reg-names = "control", "mem";
        };""")

        spi_reg = spi_node.get_reg()

        control_reg = spi_reg.get_by_name("control")[0]
        self.assertEqual(control_reg[0], 0x110013000)
        self.assertEqual(control_reg[1], 0x1000)
        mem_reg = spi_reg.get_by_name("mem")[0]
        self.assertEqual(mem_reg[0], 0x20000000)
        self.assertEqual(mem_reg[1], 0x10000000)

    def test_ranges(self):
        mem_node = Node.from_dts("""memory@180000000 {
            device-type = "memory";
            ranges = <0x1 0x80000000 0x1 0x80000000 0x80000000>;
        };""")

        mem_ranges = mem_node.get_ranges()

        first_range = mem_ranges[0]
        self.assertEqual(first_range[0], 0x180000000)
        self.assertEqual(first_range[1], 0x180000000)
        self.assertEqual(first_range[2], 0x80000000)

if __name__ == "__main__":
    unittest.main()
