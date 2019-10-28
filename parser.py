#!/usr/bin/env python3

from lexer import *
import pprint

def transformNode(string, location, tokens):
    return { "label": tokens.label, "name": tokens.name, "address": tokens.address, "children": tokens.children.asList() }

def transformPropertyAssignment(string, location, tokens):
    return { "name": tokens.name, "value": tokens.value }

node_definition.setParseAction(transformNode)
property_assignment.setParseAction(transformPropertyAssignment)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        devicetree.parseFile(sys.argv[1]).pprint()
