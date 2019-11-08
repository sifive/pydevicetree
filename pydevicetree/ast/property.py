#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Any

from pydevicetree.ast.helpers import wrapStrings, formatLevel

class PropertyValues:
    """PropertyValues is the parent class of all values which can be assigned to a Property

    Child classes include

        Bytestring
        CellArray
        StringList
    """
    def __init__(self, values: List[Any] = None):
        """Create a PropertyValue"""
        self.values = values

    def __repr__(self) -> str:
        return "<PropertyValues " + self.values.__repr__() + ">"

    def __str__(self) -> str:
        return self.to_dts()

    def __iter__(self):
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def to_dts(self, formatHex: bool = False) -> str:
        """Format the values in Devicetree Source format"""
        return " ".join(wrapStrings(self.values, formatHex))

    def __getitem__(self, key) -> Any:
        return self.values[key]

    def __eq__(self, other) -> bool:
        if isinstance(other, PropertyValues):
            return self.values == other.values
        return self.values == other

class Bytestring(PropertyValues):
    """A Bytestring is a sequence of bytes

    In Devicetree, Bytestrings are represented as a sequence of two-digit hexadecimal integers,
    optionally space-separated, enclosed by square brackets:

        [de ad be eef]
    """
    def __init__(self, bytelist: List[int] = None):
        """Create a Bytestring object"""
        PropertyValues.__init__(self, bytearray(bytelist))

    def __repr__(self) -> str:
        return "<Bytestring " + str(self.values) + ">"

    def to_dts(self, formatHex: bool = False) -> str:
        """Format the bytestring in Devicetree Source format"""
        return "[" + " ".join("%02x" % v for v in self.values) + "]"

class CellArray(PropertyValues):
    """A CellArray is an array of integer values

    CellArrays are commonly used as the value of Devicetree properties like `reg` and `interrupts`.
    The interpretation of each element of a CellArray is device-dependent. For example, the `reg`
    property encodes a CellArray as a list of tuples (base address, size), while the `interrupts`
    property encodes a CellArray as simply a list of interrupt line numbers.
    """
    def __init__(self, cells: List[Any] = None):
        """Create a CellArray object"""
        PropertyValues.__init__(self, cells)

    def __repr__(self) -> str:
        return "<CellArray " + self.values.__repr__() + ">"

    def to_dts(self, formatHex: bool = False) -> str:
        """Format the cell array in Devicetree Source format"""
        return "<" + " ".join(wrapStrings(self.values, formatHex)) + ">"

class StringList(PropertyValues):
    """A StringList is a list of null-terminated strings

    The most common use of a StringList in Devicetree is to describe the `compatible` property.
    """
    def __init__(self, strings: List[str] = None):
        """Create a StringList object"""
        PropertyValues.__init__(self, strings)

    def __repr__(self) -> str:
        return "<StringList " + self.values.__repr__() + ">"

    def to_dts(self, formatHex: bool = False) -> str:
        """Format the list of strings in Devicetree Source format"""
        return ", ".join(wrapStrings(self.values))

class Property:
    """A Property is a key-value pair for a Devicetree Node

    Properties are used to describe Nodes in the tree. There are many common properties, like

        - compatible
        - reg
        - reg-names
        - ranges
        - interrupt-controller
        - interrupts
        - interrupt-parent
        - clocks
        - status

    Which might commonly describe many or all nodes in a tree, and there are device, vendor,
    operating system, runtime-specific properties.

    Properties can possess no value, conveing meaning solely by their presence:

        interrupt-controller;

    Properties can also possess values such as an array of cells, a list of strings, etc.

        reg = <0x10013000 0x1000>;
        compatible = "sifive,rocket0", "riscv";

    And properties can posses arbitrarily complex values, such as the following from the
    Devicetree specification:

        example = <0xf00f0000 19>, "a strange property format";
    """
    def __init__(self, name: str, values: PropertyValues):
        """Create a Property object"""
        self.name = name
        self.values = values

    def __repr__(self) -> str:
        return "<Property %s>" % self.name

    def __str__(self) -> str:
        return self.to_dts()

    def to_dts(self, level: int = 0) -> str:
        """Format the Property assignment in Devicetree Source format"""
        if self.name in ["reg", "ranges"]:
            value = self.values.to_dts(formatHex=True)
        else:
            value = self.values.to_dts(formatHex=False)

        if value != "":
            return formatLevel(level, "%s = %s;\n" % (self.name, value))
        return formatLevel(level, "%s;\n" % self.name)
