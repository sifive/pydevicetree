#!/usr/bin/env python3

import os
import re

class Devicetree:
    def __init__(self, elements=[]):
        self.elements = elements

    def __iter__(self):
        return iter(self.elements)

    @staticmethod
    def parseFile(filename, followIncludes=False):
        from source import parseTree
        with open(filename, 'r') as f:
            contents = f.read()
        pwd = os.path.dirname(filename) + "/"
        return Devicetree(parseTree(contents, pwd, followIncludes))

    def dump(self):
        from source import printTree
        printTree(self.elements)

    def __find_nodes(self, match_func, elements):
        nodes = []
        for e in elements:
            if type(e) is Node:
               if match_func(e):
                   nodes.append(e)
               nodes += self.__find_nodes(match_func, e.children)
        return nodes

    def match(self, compatible, func=None):
        regex = re.compile(compatible)
        def match_compat(node):
            compatibles = node.get_fields("compatible")
            if compatibles is not None:
                return all(regex.match(c) for c in compatibles)
        nodes = self.__find_nodes(match_compat, self.elements)
        if func is not None:
            for n in nodes:
                func(n)
        return nodes

    def chosen(self, property_name, func=None):
        def match_chosen(node):
            return node.name == "chosen"
        for n in self.__find_nodes(match_chosen, self.elements):
            for p in n.properties:
                if p.name == property_name:
                    if func is not None:
                        func(p.values)
                    return p.values

class Node:
    def __init__(self, name, label=None, address=None, properties=None, children=None):
        self.name = name
        self.parent=None

        self.label = label
        self.address = address
        self.properties = properties
        self.children = children

    def __repr__(self):
        if self.address:
            return "<Node %s@%s>" % (self.name, self.address)
        else:
            return "<Node %s>" % self.name

    def __str__(self):
        return "Node %s" % self.name

    def get_fields(self, field_name):
        for p in self.properties:
            if p.name == field_name:
                return p.values

    def get_field(self, field_name):
        fields = self.get_fields(field_name)
        if fields is not None:
            return fields[0]

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

class Property:
    def __init__(self, name, values=None):
        self.name = name

        self.values = values

    def __repr__(self):
        return "<Property %s>" % self.name

    def __str__(self):
        if self.values:
            return "Property %s: %s" % (self.name, self.values)
        else:
            return "Property %s" % self.name

class Directive:
    def __init__(self, directive, options=None):
        self.directive = directive

        self.options = options

    def __repr__(self):
        return "<Directive %s>" % self.directive

    def __str__(self):
        return "Directive %s" % self.directive
