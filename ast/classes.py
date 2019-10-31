#!/usr/bin/env python3

class Devicetree:
    def __init__(self, elements=[]):
        self.elements = elements

    def __iter__(self):
        return iter(self.elements)

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
