#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

import pyparsing as p # type: ignore

p.ParserElement.enablePackrat()

node_name = p.Word(p.alphanums + ",.-+_") ^ p.Literal("/")
integer = p.pyparsing_common.integer ^ (p.Literal("0x").suppress() + p.pyparsing_common.hex_integer)
unit_address = p.pyparsing_common.hex_integer
property_name = p.Word(p.alphanums + ",.-_+?#")
label = p.Word(p.alphanums + "_").setResultsName("label")
label_creation = p.Combine(label + p.Literal(":"))
string = p.QuotedString(quoteChar='"')
stringlist = p.delimitedList(string)
node_path = p.Combine(p.Literal("/") + \
        p.delimitedList(node_name, delim="/", combine=True)).setResultsName("path") + \
        p.Optional(p.Literal("@").suppress() + unit_address("address"))
path_reference = p.Literal("&{").suppress() + node_path + p.Literal("}").suppress()
label_reference = p.Literal("&").suppress() + label
reference = path_reference ^ label_reference
directive = p.QuotedString(quoteChar="/", unquoteResults=False) + \
        p.Optional(string ^ property_name ^ node_name ^ reference ^ \
                (integer * 2)) + p.Literal(";").suppress()

operator = p.oneOf("~ ! * / + - << >> < <= > >= == != & ^ | && ||")
arith_expr = p.Forward()
ternary_element = arith_expr ^ integer
ternary_expr = ternary_element + p.Literal("?") + ternary_element + p.Literal(":") + ternary_element
arith_expr = p.nestedExpr(content=(p.OneOrMore(operator ^ integer) ^ ternary_expr))

cell_array = p.Literal("<").suppress() + \
        p.ZeroOrMore(integer ^ arith_expr ^ string ^ reference ^ label_creation.suppress()) + \
        p.Literal(">").suppress()
bytestring = p.Literal("[").suppress() + \
        (p.OneOrMore(p.Word(p.hexnums, exact=2) ^ label_creation.suppress())) + \
        p.Literal("]").suppress()
property_values = p.Forward()
property_values = p.delimitedList(property_values ^ cell_array ^ bytestring ^ stringlist)
property_assignment = property_name("property_name") + p.Optional(p.Literal("=").suppress() + \
        (property_values)).setResultsName("value") + p.Literal(";").suppress()

node_opener = p.Optional(label_creation) + node_name("node_name") + \
        p.Optional(p.Literal("@").suppress() + unit_address("address")) + p.Literal("{").suppress()
node_reference_opener = reference + p.Literal("{").suppress()
node_closer = p.Literal("}").suppress() + p.Literal(";").suppress()
node_definition = p.Forward()
# pylint: disable=expression-not-assigned
node_definition << (node_opener ^ node_reference_opener) + \
        p.ZeroOrMore(property_assignment ^ directive ^ node_definition) + \
        node_closer

devicetree = p.ZeroOrMore(directive ^ node_definition)

devicetree.ignore(p.cStyleComment)
devicetree.ignore("//" + p.SkipTo(p.lineEnd))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        devicetree.parseFile(sys.argv[1]).pprint()
