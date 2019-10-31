#!/usr/bin/env python3

import re

class Devicetree:
    def __init__(self, elements=[]):
        self.elements = elements

    def __iter__(self):
        return iter(self.elements)

    def __find_nodes(self, match_func, elements):
        nodes = []
        for e in elements:
            if type(e) is Node:
               if match_func(e):
                   nodes.append(e)
               nodes += self.__find_nodes(match_func, e.children)
        return nodes

    def match(self, compatible, func):
        regex = re.compile(compatible)
        def match_compat(node):
            compatibles = node.get_fields("compatible")
            if compatibles is not None:
                return all(regex.match(c) for c in compatibles)
        for n in self.__find_nodes(match_compat, self.elements):
            func(n)

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
