#!/usr/bin/env python3

from lexer import *
from classes import *
import pprint

def transformNode(string, location, tokens):
    properties = [e for e in tokens.asList() if type(e) is Property or type(e) is Directive]
    children = [e for e in tokens.asList() if type(e) is Node]

    return Node(tokens.node_name, tokens.label, tokens.address, properties=properties, children=children)

def transformPropertyAssignment(string, location, tokens):
    return Property(tokens.property_name, tokens.value)

def transformDirective(string, location, tokens):
    return Directive(tokens.directive, tokens.option)

node_definition.setParseAction(transformNode)
property_assignment.setParseAction(transformPropertyAssignment)
directive.setParseAction(transformDirective)

def printTree(tree, level=0):
    def printlevel(level, s):
        print(" " * level + s)

    for item in tree:
        if type(item) is Node:
            if item.address:
                printlevel(level, "Node %s@%x" % (item.name, item.address))
            else:
                printlevel(level, "Node %s" % item.name)

            if item.label:
                printlevel(level, " Label: %s" % item.label)

            printTree(item.properties, level=(level + 1))

            printTree(item.children, level=(level + 1))
        elif type(item) is Property:
            if item.values:
                printlevel(level, "Property %s: %s" % (item.name, item.values))
            else:
                printlevel(level, "Property %s" % item.name)
        elif type(item) is Directive:
            if item.options:
                printlevel(level, "Directive %s: %s" % (item.directive, item.options))
            else:
                printlevel(level, "Directive %s" % item.directive)

def parseTree(dts):
    return devicetree.parseString(dts)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            dts = f.read()
        tree = parseTree(dts)
        printTree(tree)
    else:
        print("Please pass the devicetree source file as an argument")
        sys.exit(1)

