#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Any

from pydevicetree.ast.helpers import wrapStrings, formatLevel

class PropertyValues:
    def __init__(self, values: List[Any] = None):
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
        return " ".join(wrapStrings(self.values, formatHex))

    def __getitem__(self, key) -> Any:
        return self.values[key]

    def __eq__(self, other) -> bool:
        if isinstance(other, PropertyValues):
            return self.values == other.values
        return self.values == other

class Bytestring(PropertyValues):
    def __init__(self, bytelist: List[int] = None):
        PropertyValues.__init__(self, bytearray(bytelist))

    def __repr__(self) -> str:
        return "<Bytestring " + str(self.values) + ">"

    def to_dts(self, formatHex: bool = False) -> str:
        return "[" + " ".join("%02x" % v for v in self.values) + "]"

class CellArray(PropertyValues):
    def __init__(self, cells: List[Any] = None):
        PropertyValues.__init__(self, cells)

    def __repr__(self) -> str:
        return "<CellArray " + self.values.__repr__() + ">"

    def to_dts(self, formatHex: bool = False) -> str:
        return "<" + " ".join(wrapStrings(self.values, formatHex)) + ">"

class StringList(PropertyValues):
    def __init__(self, strings: List[str] = None):
        PropertyValues.__init__(self, strings)

    def __repr__(self) -> str:
        return "<StringList " + self.values.__repr__() + ">"

    def to_dts(self, formatHex: bool = False) -> str:
        return ", ".join(wrapStrings(self.values))

class Property:
    def __init__(self, name: str, values: PropertyValues):
        self.name = name
        self.values = values

    def __repr__(self) -> str:
        return "<Property %s>" % self.name

    def __str__(self) -> str:
        return self.to_dts()

    def to_dts(self, level: int = 0) -> str:
        if self.name in ["reg", "ranges"]:
            value = self.values.to_dts(formatHex=True)
        else:
            value = self.values.to_dts(formatHex=False)

        if value != "":
            return formatLevel(level, "%s = %s;\n" % (self.name, value))
        return formatLevel(level, "%s;\n" % self.name)
