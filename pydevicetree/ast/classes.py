#!/usr/bin/env python3

import os
import re

from typing import List, Union, Optional, TypeVar, Type, Iterable, Callable, cast, Any, Pattern

# These type names are just used in the constructors for these clasess
ElementList = Iterable[Union['Node', 'Property', 'Directive']]
DirectiveOption = List[Any]

# Callback type signatures for Devicetree.match() and Devicetree.chosen()
MatchCallback = Optional[Callable[['Node'], None]]
ChosenCallback = Optional[Callable[['PropertyValues'], None]]

def formatLevel(level: int, s: str) -> str:
    return "\t" * level + s

def wrapStrings(values: List[Any], formatHex: bool = False) -> List[Any]:
    wrapped = []
    for v in values:
        if type(v) is str:
            if v[0] != '&':
                wrapped.append("\"%s\"" % v)
            else:
                wrapped.append(v)
        elif type(v) is int:
            if formatHex:
                wrapped.append("0x%x" % v)
            else:
                wrapped.append(str(v))
        else:
            wrapped.append(str(v))
    return wrapped

class PropertyValues:
    def __init__(self, values: List[Any] = []):
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
        return "<" + " ".join(wrapStrings(self.values, formatHex)) + ">"

    def __getitem__(self, key) -> Any:
        return self.values[key]

    def __eq__(self, other) -> bool:
        if isinstance(other, PropertyValues):
            return self.values == other.values
        else:
            return self.values == other

class StringList(PropertyValues):
    def __init__(self, strings: List[str] = []):
        PropertyValues.__init__(self, strings)

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
            value = self.values.to_dts(formatHex = True)
        else:
            value = self.values.to_dts(formatHex = False)

        if self.values:
            return formatLevel(level, "%s = %s;\n" % (self.name, value))
        else:
            return formatLevel(level, "%s;\n" % self.name)

class Directive:
    def __init__(self, directive: str, options: DirectiveOption = []):
        self.directive = directive
        self.options = options

    def __repr__(self) -> str:
        return "<Directive %s>" % self.directive

    def __str__(self) -> str:
        return self.to_dts()

    def to_dts(self, level: int = 0) -> str:
        if self.options:
            return formatLevel(level, "%s %s;\n" % (self.directive, self.options))
        else:
            return formatLevel(level, "%s;\n" % self.directive)

class Node:
    def __init__(self, name: str, label: Optional[str] = None, address: Optional[str] = None, properties: List[Property] = [], directives: List[Directive] = [], children: List['Node'] = []):
        self.name = name
        self.parent = None # type: Optional['Node']

        self.label = label
        self.address = address
        self.properties = properties
        self.directives = directives
        self.children = children

    def __repr__(self) -> str:
        if self.address:
            return "<Node %s@%s>" % (self.name, self.address)
        else:
            return "<Node %s>" % self.name

    def __str__(self) -> str:
        return self.to_dts()

    def to_dts(self, level: int = 0) -> str:
        out = ""
        if type(self.address) is int and self.label:
            out += formatLevel(level, "%s: %s@%x {\n" % (self.label, self.name, cast(int, self.address)))
        elif type(self.address) is int:
            out += formatLevel(level, "%s@%x {\n" % (self.name, cast(int, self.address)))
        elif self.label:
            out += formatLevel(level, "%s: %s {\n" % (self.label, self.name))
        elif self.name != "":
            out += formatLevel(level, "%s {\n" % self.name)

        for d in self.directives:
            out += d.to_dts(level + 1)
        for p in self.properties:
            out += p.to_dts(level + 1)
        for c in self.children:
            out += c.to_dts(level + 1)

        if self.name != "":
            out += formatLevel(level, "};\n")

        return out

    def child_nodes(self) -> Iterable['Node']:
        for n in self.children:
            yield n
            for m in n.child_nodes():
                yield m

    def get_fields(self, field_name: str) -> Optional[PropertyValues]:
        for p in self.properties:
            if p.name == field_name:
                return p.values
        return None

    def get_field(self, field_name: str) -> Any:
        fields = self.get_fields(field_name)
        if fields is not None:
            if len(cast(PropertyValues, fields)) != 0:
                return fields[0]
        return None

    def address_cells(self):
        cells = self.get_field("#address-cells")
        if cells is not None:
            return cells
        elif self.parent is not None:
            return self.parent.address_cells()
        # No address cells found
        return 0

    def size_cells(self):
        cells = self.get_field("#size-cells")
        if cells is not None:
            return cells
        elif self.parent is not None:
            return self.parent.size_cells()
        # No size cells found
        return 0

class Devicetree(Node):
    def __init__(self, elements: ElementList = []):
        properties = [] # type: List[Property]
        directives = [] # type: List[Directive]
        children = [] # type: List[Node]

        for e in elements:
            if type(e) is Node:
                children.append(cast(Node, e))
            elif type(e) is Property:
                properties.append(cast(Property, e))
            elif type(e) is Directive:
                directives.append(cast(Directive, e))

        Node.__init__(self, name="", properties=properties, directives=directives, children=children)

    def to_dts(self, level: int = 0) -> str:
        out = ""

        for d in self.directives:
            out += d.to_dts()
        for p in self.properties:
            out += p.to_dts()
        for c in self.children:
            out += c.to_dts()

        return out

    @staticmethod
    def parseFile(filename: str, followIncludes: bool = False) -> 'Devicetree':
        from pydevicetree.source import parseTree
        with open(filename, 'r') as f:
            contents = f.read()
        pwd = os.path.dirname(filename) + "/"
        return parseTree(contents, pwd, followIncludes)

    def all_nodes(self) -> Iterable[Node]:
        return self.child_nodes()

    def match(self, compatible: Pattern, func: MatchCallback = None) -> List[Node]:
        regex = re.compile(compatible)

        def match_compat(node: Node) -> bool:
            compatibles = node.get_fields("compatible")
            if compatibles is not None:
                return any(regex.match(c) for c in compatibles)
            return False

        nodes = list(filter(match_compat, self.all_nodes()))

        if func is not None:
            for n in nodes:
                func(n)

        return nodes

    def chosen(self, property_name: str, func: ChosenCallback = None) -> Optional[PropertyValues]:
        def match_chosen(node: Node) -> bool:
            return node.name == "chosen"

        for n in filter(match_chosen, self.all_nodes()):
            for p in n.properties:
                if p.name == property_name:
                    if func is not None:
                        func(p.values)
                    return p.values

        return None

