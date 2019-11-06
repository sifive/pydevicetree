#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

from itertools import chain

from pydevicetree.source.grammar import *
from pydevicetree.ast import *

def transformNode(string, location, tokens):
    properties = [e for e in tokens.asList() if isinstance(e, Property)]
    directives = [e for e in tokens.asList() if isinstance(e, Directive)]
    children = [e for e in tokens.asList() if isinstance(e, Node)]

    if tokens.node_reference:
        return NodeReference(tokens.node_reference[0], properties=properties,
                             directives=directives, children=children)
    return Node(tokens.node_name, tokens.label, tokens.address, properties=properties,
                directives=directives, children=children)

def transformPropertyAssignment(string, location, tokens):
    for v in tokens.value:
        if isinstance(v, PropertyValues):
            return Property(tokens.property_name, v)
        if isinstance(v, CellArray):
            return Property(tokens.property_name, v)
        if isinstance(v, StringList):
            return Property(tokens.property_name, v)

    return Property(tokens.property_name, PropertyValues([]))

def transformDirective(string, location, tokens):
    return Directive(tokens.directive, tokens.option)

def evaluateArithExpr(string, location, tokens):
    flat_tokens = list(chain.from_iterable(tokens.asList()))
    expr = " ".join(str(t) for t in flat_tokens)
    # pylint: disable=eval-used
    return eval(expr)

def transformTernary(string, location, tokens):
    # pylint: disable=eval-used
    return eval(str(tokens[2]) +" if " + str(tokens[0]) + " else " + str(tokens[4]))

def transformPropertyValues(string, location, tokens):
    if len(tokens.asList()) == 1:
        return tokens.asList()[0]
    return PropertyValues(tokens.asList())

def transformStringList(string, location, tokens):
    return StringList(tokens.asList())

def transformBytestring(string, location, tokens):
    inttokens = []
    for t in tokens.asList():
        if all(c in "0123456789abcdefABCDEF" for c in t):
            inttokens.append(int(t, base=16))
    return Bytestring(inttokens)

def transformCellArray(string, location, tokens):
    return CellArray(tokens.asList())

node_definition.setParseAction(transformNode)
property_assignment.setParseAction(transformPropertyAssignment)
directive.setParseAction(transformDirective)
arith_expr.setParseAction(evaluateArithExpr)
ternary_expr.setParseAction(transformTernary)
stringlist.setParseAction(transformStringList)
bytestring.setParseAction(transformBytestring)
cell_array.setParseAction(transformCellArray)
property_values.setParseAction(transformPropertyValues)

def printTree(tree, level=0):
    def printlevel(level, s):
        print(" " * level + s)

    for item in tree:
        if isinstance(item, Node):
            if item.address:
                printlevel(level, "Node %s@%x" % (item.name, item.address))
            else:
                printlevel(level, "Node %s" % item.name)

            if item.label:
                printlevel(level, " Label: %s" % item.label)

            if item.parent:
                printlevel(level, " Parent: %s" % item.parent)

            printTree(item.properties, level=(level + 1))

            printTree(item.children, level=(level + 1))
        elif isinstance(item, Property):
            if item.values:
                printlevel(level, "Property %s: %s" % (item.name, item.values))
            else:
                printlevel(level, "Property %s" % item.name)
        elif isinstance(item, Directive):
            if item.options:
                printlevel(level, "Directive %s: %s" % (item.directive, item.options))
            else:
                printlevel(level, "Directive %s" % item.directive)

def parentNodes(tree, parent=None):
    for item in tree:
        if isinstance(item, Node):
            item.parent = parent
            parentNodes(item.children, item)

def recurseIncludeFiles(elements, pwd):
    for e in elements:
        if isinstance(e, Directive):
            if e.directive == "/include/":
                # Prefix with current directory if path is not absolute
                if e.options[0] != '/':
                    e.options = pwd + e.options

                with open(e.options, 'r') as f:
                    contents = f.read()

                elements += parseElements(contents)

def parseElements(dts, pwd="", followIncludes=False):
    elements = devicetree.parseString(dts)
    parentNodes(elements)
    if followIncludes:
        recurseIncludeFiles(elements, pwd)
    return elements

def parseTree(dts, pwd="", followIncludes=False):
    return Devicetree(parseElements(dts, pwd, followIncludes))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            dts = f.read()
        tree = parseTree(dts)
        printTree(tree)
        print(tree)
    else:
        print("Please pass the devicetree source file as an argument")
        sys.exit(1)
