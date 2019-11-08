#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

from itertools import chain

from pydevicetree.source import grammar
from pydevicetree.ast import *

def transformNode(string, location, tokens):
    """Transforms a ParseResult into a Node"""
    properties = [e for e in tokens.asList() if isinstance(e, Property)]
    directives = [e for e in tokens.asList() if isinstance(e, Directive)]
    children = [e for e in tokens.asList() if isinstance(e, Node)]

    if tokens.node_reference:
        return NodeReference(tokens.node_reference[0], properties=properties,
                             directives=directives, children=children)
    return Node(tokens.node_name, tokens.label, tokens.address, properties=properties,
                directives=directives, children=children)

def transformPropertyAssignment(string, location, tokens):
    """Transforms a ParseResult into a Property"""
    for v in tokens.value:
        if isinstance(v, PropertyValues):
            return Property(tokens.property_name, v)
        if isinstance(v, CellArray):
            return Property(tokens.property_name, v)
        if isinstance(v, StringList):
            return Property(tokens.property_name, v)

    return Property(tokens.property_name, PropertyValues([]))

def transformDirective(string, location, tokens):
    """Transforms a ParseResult into a Directive"""
    return Directive(tokens.directive, tokens.option)

def evaluateArithExpr(string, location, tokens):
    """Evaluates a ParseResult as a python expression"""
    flat_tokens = list(chain.from_iterable(tokens.asList()))
    expr = " ".join(str(t) for t in flat_tokens)
    # pylint: disable=eval-used
    return eval(expr)

def transformTernary(string, location, tokens):
    """Evaluates a ParseResult as a ternary expression"""
    # pylint: disable=eval-used
    return eval(str(tokens[2]) +" if " + str(tokens[0]) + " else " + str(tokens[4]))

def transformPropertyValues(string, location, tokens):
    """Transforms a ParseResult into a PropertyValues"""
    if len(tokens.asList()) == 1:
        return tokens.asList()[0]
    return PropertyValues(tokens.asList())

def transformStringList(string, location, tokens):
    """Transforms a ParseResult into a StringList"""
    return StringList(tokens.asList())

def transformBytestring(string, location, tokens):
    """Transforms a ParseResult into a Bytestring"""
    inttokens = []
    for t in tokens.asList():
        if all(c in "0123456789abcdefABCDEF" for c in t):
            inttokens.append(int(t, base=16))
    return Bytestring(inttokens)

def transformCellArray(string, location, tokens):
    """Transforms a ParseResult into a CellArray"""
    return CellArray(tokens.asList())

grammar.node_definition.setParseAction(transformNode)
grammar.property_assignment.setParseAction(transformPropertyAssignment)
grammar.directive.setParseAction(transformDirective)
grammar.arith_expr.setParseAction(evaluateArithExpr)
grammar.ternary_expr.setParseAction(transformTernary)
grammar.stringlist.setParseAction(transformStringList)
grammar.bytestring.setParseAction(transformBytestring)
grammar.cell_array.setParseAction(transformCellArray)
grammar.property_values.setParseAction(transformPropertyValues)

def printTree(tree, level=0):
    """Helper function to print a bunch of elements as a tree"""
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
    """Walks a tree and sets Nodes' parent field to point at their parent"""
    for item in tree:
        if isinstance(item, Node):
            item.parent = parent
            parentNodes(item.children, item)

def recurseIncludeFiles(elements, pwd):
    """Recursively follows and parses /include/ directives an a tree"""
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
    """Parses a string into a list of elements"""
    elements = grammar.devicetree.parseString(dts)
    parentNodes(elements)
    if followIncludes:
        recurseIncludeFiles(elements, pwd)
    return elements

def parseTree(dts, pwd="", followIncludes=False):
    """Parses a string into a full Devicetree"""
    return Devicetree(parseElements(dts, pwd, followIncludes))

def parseNode(dts):
    """Parses a string into a Devictreee Node"""
    return grammar.node_definition.parseString(dts)[0]

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
