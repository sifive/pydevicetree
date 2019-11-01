#!/usr/bin/env python3

import os
import re

from typing import List, Union, Optional, TypeVar, Type, Iterable, Callable, cast, Any, Pattern

Element = Union['Node', 'Property', 'Directive']
ElementList = Iterable[Element]
MatchCallback = Optional[Callable[['Node'], None]]
PropertyValue = Optional[Union[int, str]]
PropertyValues = List[PropertyValue]
DirectiveOption = List[Any]
ChosenCallback = Optional[Callable[[PropertyValues], None]]

class Property:
    def __init__(self, name: str, values: PropertyValues = []):
        self.name = name
        self.values = values

    def __repr__(self) -> str:
        return "<Property %s>" % self.name

    def __str__(self) -> str:
        if self.values:
            return "Property %s: %s" % (self.name, self.values)
        else:
            return "Property %s" % self.name

class Directive:
    def __init__(self, directive: str, options: DirectiveOption = []):
        self.directive = directive
        self.options = options

    def __repr__(self) -> str:
        return "<Directive %s>" % self.directive

    def __str__(self) -> str:
        return "Directive %s" % self.directive

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
        return "Node %s" % self.name

    def get_fields(self, field_name: str) -> PropertyValues:
        for p in self.properties:
            if p.name == field_name:
                return p.values
        return []

    def get_field(self, field_name: str) -> PropertyValue:
        fields = self.get_fields(field_name)
        if len(fields) != 0:
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

class Devicetree:
    def __init__(self, elements: ElementList = []):
        self.elements = elements

    def __iter__(self) -> ElementList:
        return iter(self.elements)

    @staticmethod
    def parseFile(filename: str, followIncludes: Optional[bool] = False) -> 'Devicetree':
        from source import parseTree
        with open(filename, 'r') as f:
            contents = f.read()
        pwd = os.path.dirname(filename) + "/"
        return Devicetree(parseTree(contents, pwd, followIncludes))

    def dump(self) -> None:
        from source import printTree
        printTree(self.elements)

    def __filter_nodes(self, elements: ElementList) -> List[Node]:
        return cast(List[Node], filter(lambda e: type(e) is Node, elements),)

    def __find_nodes(self, match_func: Callable[[Node], bool], elements: ElementList) -> List[Node]:
        nodes = []
        for e in self.__filter_nodes(elements):
           if match_func(e):
               nodes.append(e)
           nodes += self.__find_nodes(match_func, e.children)
        return nodes

    def match(self, compatible: Pattern, func: MatchCallback = None) -> List[Node]:
        regex = re.compile(compatible)

        def match_compat(node: Node) -> bool:
            compatibles = node.get_fields("compatible")
            if compatibles is not None:
                return any(regex.match(c) for c in compatibles)
            return False

        nodes = self.__find_nodes(match_compat, self.elements)
        if func is not None:
            for n in nodes:
                func(n)
        return nodes

    def chosen(self, property_name: str, func: ChosenCallback = None) -> Optional[PropertyValues]:
        def match_chosen(node):
            return node.name == "chosen"
        for n in self.__find_nodes(match_chosen, self.elements):
            for p in n.properties:
                if p.name == property_name:
                    if func is not None:
                        func(p.values)
                    return p.values
        return None

